"""Safety regressions use only disposable fixtures; never touch a real course."""
from pathlib import Path
import contextlib
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tooling'))
import sync_course
from safe_paths import UnsafePath, checked_path, project_files, replace_directory


def snapshot(root):
    result = {}
    for directory, dirs, names in os.walk(root, followlinks=False):
        for name in dirs + names:
            path = Path(directory) / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                result[rel] = ('link', os.readlink(path))
            elif path.is_dir():
                result[rel] = ('directory',)
            else:
                result[rel] = ('file', path.read_bytes(), path.stat().st_mode & 0o777)
    return result


class ToolingSafety(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='ustudyopen-tooling-test-')
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.central = self.work / 'central'
        for name in ['_extensions', 'tooling', 'workflows', 'LICENSES']:
            shutil.copytree(ROOT / name, self.central / name, ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copy2(ROOT / 'THIRD-PARTY-NOTICES.md', self.central / 'THIRD-PARTY-NOTICES.md')
        self.original_source = sync_course.SOURCE
        sync_course.SOURCE = self.central
        self.addCleanup(setattr, sync_course, 'SOURCE', self.original_source)

    def course(self, installed=True):
        root = self.work / 'course'
        root.mkdir()
        (root / 'course.yml').write_text('{}\n')
        (root / 'README.md').write_text('user-owned course content\n')
        if installed:
            self.sync(root)
        return root

    def sync(self, root):
        with contextlib.redirect_stdout(io.StringIO()):
            sync_course.sync(root)

    def change_source(self):
        for name in ['PROVENANCE.md', 'assets/after-body.html']:
            path = self.central / '_extensions/ustudyopen-design' / name
            path.write_text(path.read_text() + '\n<!-- test update -->\n')

    def assert_no_stage(self, root):
        self.assertFalse(list(root.glob('.ustudyopen-sync-*')))
        self.assertFalse(list(root.glob('.ustudyopen-output-*')))

    def test_initial_install_and_repeat_preserve_unmanaged_content(self):
        root = self.course()
        (root / 'tests/run_course.py').write_text('# course-owned checks\n')
        before = snapshot(root)
        self.sync(root)
        self.assertEqual(snapshot(root), before)
        self.assert_no_stage(root)

    def test_vendor_licenses_accompany_each_channel_and_are_hashed(self):
        root = self.course()
        extension = root / '_extensions/ustudyopen-design'
        lock = json.loads((root / 'design-vendor.json').read_text())['files']
        for name in ['LICENSE', 'LICENSING.md', 'PROVENANCE.md',
                     'THIRD-PARTY-NOTICES.md', 'LICENSES/fuse-6.6.2.txt']:
            self.assertEqual(hashlib.sha256((extension / name).read_bytes()).hexdigest(), lock[name])
        platform = json.loads((root / 'platform-vendor.json').read_text())['files']
        for name, source in [('tests/LICENSE-platform.txt', 'tooling/LICENSE'),
                             ('.github/workflows/LICENSE-platform.txt', 'workflows/LICENSE')]:
            self.assertEqual((root / name).read_bytes(), (self.central / source).read_bytes())
            self.assertEqual(hashlib.sha256((root / name).read_bytes()).hexdigest(), platform[name])

    def test_independent_license_is_never_overwritten(self):
        root = self.course(False)
        (root / 'tests').mkdir()
        (root / 'tests/LICENSE-platform.txt').write_text('independent legal notice')
        before = snapshot(root)
        with self.assertRaisesRegex(SystemExit, 'Unmanaged platform file'):
            self.sync(root)
        self.assertEqual(snapshot(root), before)

    def test_unmanaged_initial_render_script_is_never_overwritten(self):
        root = self.course(False)
        (root / 'tests').mkdir()
        (root / 'tests/render_clean.py').write_text('# pre-existing local implementation\n')
        before = snapshot(root)
        with self.assertRaisesRegex(SystemExit, 'Unmanaged platform file'):
            self.sync(root)
        self.assertEqual(snapshot(root), before)

    def test_new_managed_path_cannot_overwrite_an_unmanaged_file(self):
        root = self.course()
        lock = root / 'platform-vendor.json'
        data = json.loads(lock.read_text())
        del data['files']['tests/browser_client.mjs']
        lock.write_text(json.dumps(data))
        (root / 'tests/browser_client.mjs').write_text('// independent local work\n')
        before = snapshot(root)
        with self.assertRaisesRegex(SystemExit, 'Unmanaged platform file'):
            self.sync(root)
        self.assertEqual(snapshot(root), before)

    def test_local_managed_edit_is_rejected(self):
        root = self.course()
        (root / 'tests/render_clean.py').write_text('# independent edit\n')
        before = snapshot(root)
        with self.assertRaisesRegex(SystemExit, 'Local platform edits'):
            self.sync(root)
        self.assertEqual(snapshot(root), before)

    def test_symlinked_extension_parent_cannot_write_outside_course(self):
        root = self.course()
        directory = root / '_extensions/ustudyopen-design/assets'
        outside = self.work / 'outside'
        shutil.copytree(directory, outside)
        shutil.rmtree(directory)
        directory.symlink_to(outside, target_is_directory=True)
        before, foreign = snapshot(root), snapshot(outside)
        self.change_source()
        with self.assertRaisesRegex(SystemExit, 'Symlink component'):
            self.sync(root)
        self.assertEqual(snapshot(root), before)
        self.assertEqual(snapshot(outside), foreign)

    def test_symlinked_platform_parent_is_rejected(self):
        root = self.course()
        outside = self.work / 'outside-tests'
        shutil.move(root / 'tests', outside)
        (root / 'tests').symlink_to(outside, target_is_directory=True)
        before, foreign = snapshot(root), snapshot(outside)
        with self.assertRaisesRegex(SystemExit, 'Symlink component'):
            self.sync(root)
        self.assertEqual(snapshot(root), before)
        self.assertEqual(snapshot(outside), foreign)

    def test_symlinked_manifest_is_rejected(self):
        root = self.course()
        lock = root / 'design-vendor.json'
        outside = self.work / 'outside-lock.json'
        lock.rename(outside)
        lock.symlink_to(outside)
        before, foreign = snapshot(root), outside.read_bytes()
        with self.assertRaisesRegex(SystemExit, 'Symlink component'):
            self.sync(root)
        self.assertEqual(snapshot(root), before)
        self.assertEqual(outside.read_bytes(), foreign)

    def test_unsafe_manifest_path_is_rejected_before_reading(self):
        root = self.course()
        lock = root / 'design-vendor.json'
        data = json.loads(lock.read_text())
        data['files']['../../outside'] = '0' * 64
        lock.write_text(json.dumps(data))
        before = snapshot(root)
        with self.assertRaisesRegex(SystemExit, 'Unsafe relative path'):
            self.sync(root)
        self.assertEqual(snapshot(root), before)

    def test_staging_copy_failure_preserves_every_destination_file(self):
        root = self.course()
        self.change_source()
        before, real = snapshot(root), shutil.copy2
        calls = 0
        def fail(source, dest, *args, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError('simulated full filesystem')
            return real(source, dest, *args, **kwargs)
        with patch.object(sync_course.shutil, 'copy2', side_effect=fail):
            with self.assertRaisesRegex(SystemExit, 'simulated full filesystem'):
                self.sync(root)
        self.assertEqual(snapshot(root), before)
        self.assert_no_stage(root)

    def test_commit_failure_rolls_back_files_and_both_manifests(self):
        root = self.course()
        self.change_source()
        before, real = snapshot(root), os.replace
        installs = 0
        def fail(source, dest):
            nonlocal installs
            if '/new/' in str(source):
                installs += 1
                if installs == 3:
                    raise OSError('simulated rename failure')
            return real(source, dest)
        with patch.object(sync_course.os, 'replace', side_effect=fail):
            with self.assertRaisesRegex(SystemExit, 'simulated rename failure'):
                self.sync(root)
        self.assertEqual(snapshot(root), before)
        self.assert_no_stage(root)

    def test_failed_first_install_removes_only_its_own_files_and_directories(self):
        root = self.course(False)
        before, real = snapshot(root), os.replace
        installs = 0
        def fail(source, dest):
            nonlocal installs
            if '/new/' in str(source):
                installs += 1
                if installs == 3:
                    raise OSError('first install failure')
            return real(source, dest)
        with patch.object(sync_course.os, 'replace', side_effect=fail):
            with self.assertRaisesRegex(SystemExit, 'first install failure'):
                self.sync(root)
        self.assertEqual(snapshot(root), before)
        self.assert_no_stage(root)

    def test_failed_rollback_preserves_recovery_backup(self):
        root = self.course()
        self.change_source()
        real, installs = os.replace, 0
        def fail(source, dest):
            nonlocal installs
            if '/backup/' in str(source):
                raise OSError('simulated rollback failure')
            if '/new/' in str(source):
                installs += 1
                if installs == 2:
                    raise OSError('simulated commit failure')
            return real(source, dest)
        with patch.object(sync_course.os, 'replace', side_effect=fail):
            with self.assertRaisesRegex(SystemExit, 'recovery backup preserved'):
                self.sync(root)
        stages = list(root.glob('.ustudyopen-sync-*'))
        self.assertEqual(len(stages), 1)
        self.assertTrue((stages[0] / 'recovery.json').is_file())
        self.assertTrue(any(p.is_file() for p in (stages[0] / 'backup').rglob('*')))

    def test_interrupt_after_backup_rename_restores_every_file(self):
        root = self.course()
        self.change_source()
        before, real = snapshot(root), os.replace
        interrupted = False
        def interrupt(source, dest):
            nonlocal interrupted
            result = real(source, dest)
            if '/backup/' in str(dest) and not interrupted:
                interrupted = True
                raise KeyboardInterrupt()
            return result
        with patch.object(sync_course.os, 'replace', side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.sync(root)
        self.assertEqual(snapshot(root), before)
        self.assert_no_stage(root)

    def test_interrupt_after_site_rename_restores_previous_site(self):
        for phase in ['previous', 'new']:
            with self.subTest(phase=phase):
                source = self.work / ('site-source-' + phase)
                root = self.work / ('site-target-' + phase)
                source.mkdir(); root.mkdir(); (root / '_site').mkdir()
                (source / 'index.html').write_text('new')
                (root / '_site/index.html').write_text('original')
                before, real, interrupted = snapshot(root), os.replace, False
                def interrupt(src, dest):
                    nonlocal interrupted
                    result = real(src, dest)
                    if not interrupted and ((phase == 'previous' and Path(dest).name == 'previous')
                                            or (phase == 'new' and Path(src).name == 'new')):
                        interrupted = True
                        raise KeyboardInterrupt()
                    return result
                with patch('safe_paths.os.replace', side_effect=interrupt):
                    with self.assertRaises(KeyboardInterrupt):
                        replace_directory(source, root, '_site')
                self.assertEqual(snapshot(root), before)
                self.assert_no_stage(root)

    def test_source_changed_during_staging_is_rejected(self):
        root = self.course()
        self.change_source()
        before, real = snapshot(root), shutil.copy2
        changed = False
        def mutate(source, dest, *args, **kwargs):
            nonlocal changed
            if not changed:
                Path(source).write_bytes(Path(source).read_bytes() + b'\nfixture concurrent edit\n')
                changed = True
            return real(source, dest, *args, **kwargs)
        with patch.object(sync_course.shutil, 'copy2', side_effect=mutate):
            with self.assertRaisesRegex(SystemExit, 'Source changed while staging'):
                self.sync(root)
        self.assertEqual(snapshot(root), before)
        self.assert_no_stage(root)

    def test_concurrent_destination_edit_is_preserved(self):
        root = self.course()
        self.change_source()
        real, changed = shutil.copy2, False
        path = root / 'tests/install_quarto.py'
        lock = (root / 'platform-vendor.json').read_bytes()
        def mutate(source, dest, *args, **kwargs):
            nonlocal changed
            if not changed:
                path.write_text('# concurrent user work\n')
                changed = True
            return real(source, dest, *args, **kwargs)
        with patch.object(sync_course.shutil, 'copy2', side_effect=mutate):
            with self.assertRaisesRegex(SystemExit, 'Destination changed while staging'):
                self.sync(root)
        self.assertEqual(path.read_text(), '# concurrent user work\n')
        self.assertEqual((root / 'platform-vendor.json').read_bytes(), lock)
        self.assert_no_stage(root)

    def site(self):
        source, root = self.work / 'new-site', self.work / 'web'
        source.mkdir(); root.mkdir()
        (source / 'index.html').write_text('new site')
        (root / '_site').mkdir()
        (root / '_site/index.html').write_text('previous site')
        (root / 'docs').mkdir()
        (root / 'docs/index.html').write_text('published site')
        return source, root

    def test_site_copy_failure_keeps_previous_output_and_docs(self):
        source, root = self.site()
        before = snapshot(root)
        with patch('safe_paths.shutil.copytree', side_effect=OSError('copy failed')):
            with self.assertRaises(OSError):
                replace_directory(source, root, '_site')
        self.assertEqual(snapshot(root), before)
        self.assert_no_stage(root)

    def test_site_promotion_failure_restores_previous_directory(self):
        source, root = self.site()
        before, real = snapshot(root), os.replace
        def fail(source, dest):
            if Path(source).name == 'new':
                raise OSError('promotion failed')
            return real(source, dest)
        with patch('safe_paths.os.replace', side_effect=fail):
            with self.assertRaisesRegex(OSError, 'promotion failed'):
                replace_directory(source, root, '_site')
        self.assertEqual(snapshot(root), before)
        self.assert_no_stage(root)

    def test_successful_site_promotion_preserves_published_docs(self):
        source, root = self.site()
        replace_directory(source, root, '_site')
        self.assertEqual((root / '_site/index.html').read_text(), 'new site')
        self.assertEqual((root / 'docs/index.html').read_text(), 'published site')
        self.assert_no_stage(root)

    def test_source_symlink_is_not_followed(self):
        source, root = self.site()
        (source / 'external.html').symlink_to(root / 'docs/index.html')
        before = snapshot(root)
        with self.assertRaises(UnsafePath):
            replace_directory(source, root, '_site')
        self.assertEqual(snapshot(root), before)

    def test_platform_validator_rejects_traversal_and_symlinks(self):
        root = self.work / 'validation-course'
        shutil.copytree(ROOT.parent / 'ustudyopen-template', root,
                        ignore=shutil.ignore_patterns('.git', '.quarto', '_site', 'artifacts', '__pycache__'))
        self.sync(root)
        lock = root / 'platform-vendor.json'
        original = lock.read_text()
        data = json.loads(original)
        data['files']['../foreign'] = '0' * 64
        lock.write_text(json.dumps(data))
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        p = subprocess.run([sys.executable, 'tests/platform_validate.py', '--source-only'], cwd=root,
                           env=env, capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Unsafe relative path', p.stdout)
        lock.write_text(original)
        (root / 'assets/external').symlink_to(self.central, target_is_directory=True)
        p = subprocess.run([sys.executable, 'tests/platform_validate.py', '--source-only'], cwd=root,
                           env=env, capture_output=True, text=True)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn('Symlink component', p.stdout)

    def test_checked_paths_reject_platform_specific_traversal(self):
        for name in ['../foreign', '/absolute', 'C:/foreign', 'a\\..\\foreign', './a', 'a//b', 'bad\nname']:
            with self.subTest(name=name), self.assertRaises(UnsafePath):
                checked_path(self.work, name)


if __name__ == '__main__':
    unittest.main(verbosity=2)
