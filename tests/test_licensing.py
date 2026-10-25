"""Distribution-channel regressions; all mutations use disposable fixtures."""
from pathlib import Path
import json
import shutil
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tooling'))
import legal_distribution as legal
import sync_course


class Licensing(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'course'
        self.root.mkdir()
        template = ROOT.parent / 'ustudyopen-template'
        for name in legal.DOCUMENTS:
            shutil.copy2(template / name, self.root / name)
        shutil.copytree(template / 'LICENSES', self.root / 'LICENSES')
        (self.root / 'course.yml').write_text(json.dumps({'course': {'license': 'decisión-del-nuevo-autor'}}))
        sync_course.sync(self.root)
        (self.root / '_site/unit').mkdir(parents=True)
        for name in ['index.html', 'unit/lesson.html']:
            (self.root / '_site' / name).write_text('<html><body><main>academic text</main></body></html>')
        (self.root / 'docs').mkdir()
        (self.root / 'docs/index.html').write_text('historical site')

    def test_source_clone_and_new_course_may_choose_own_academic_license(self):
        errors = []
        self.assertGreater(legal.source_checks(self.root, errors), 20)
        self.assertEqual(errors, [])
        self.assertEqual(json.loads((self.root / 'course.yml').read_text())['course']['license'], 'decisión-del-nuevo-autor')

    def test_installed_extension_is_self_contained(self):
        installed = Path(self.temp.name) / 'quarto-install'
        shutil.copytree(self.root / legal.EXTENSION, installed)
        for name in ['LICENSE', 'PROVENANCE.md', 'LICENSING.md', 'THIRD-PARTY-NOTICES.md',
                     'LICENSES/fuse-6.6.2.txt', 'LICENSES/mathjax-4.1.3.txt']:
            self.assertTrue((installed / name).is_file())
        self.assertIn('Apache License', (installed / 'LICENSES/fuse-6.6.2.txt').read_text())

    def test_site_has_all_texts_links_and_reproducible_manifests(self):
        legal.prepare(self.root)
        first = {p.relative_to(self.root / '_site').as_posix(): p.read_bytes()
                 for p in (self.root / '_site').rglob('*') if p.is_file()}
        legal.prepare(self.root)
        second = {p.relative_to(self.root / '_site').as_posix(): p.read_bytes()
                  for p in (self.root / '_site').rglob('*') if p.is_file()}
        self.assertEqual(first, second)
        errors = []
        legal.output_checks(self.root, errors)
        self.assertEqual(errors, [])
        self.assertIn('href="../legal/index.txt"', (self.root / '_site/unit/lesson.html').read_text())
        self.assertEqual((self.root / 'docs/index.html').read_text(), 'historical site')
        self.assertIn('<main>academic text</main>', (self.root / '_site/index.html').read_text())

    def test_missing_output_license_fails_publication_validation(self):
        legal.prepare(self.root)
        (self.root / '_site/legal/extension/LICENSES/fuse-6.6.2.txt').unlink()
        errors = []
        legal.output_checks(self.root, errors)
        self.assertTrue(any('missing/changed' in e for e in errors))

    def test_missing_source_notice_fails_before_writing_output(self):
        (self.root / 'THIRD-PARTY-NOTICES.md').unlink()
        with self.assertRaisesRegex(ValueError, 'Missing legal source'):
            legal.prepare(self.root)
        self.assertFalse((self.root / '_site/legal').exists())

    def test_tampered_upstream_text_rejected(self):
        (self.root / 'LICENSES/fuse-6.6.2.txt').write_text('MIT')
        errors = []
        legal.source_checks(self.root, errors)
        self.assertTrue(any('integrity mismatch' in e for e in errors))

    def test_symlinked_legal_destination_cannot_escape(self):
        outside = Path(self.temp.name) / 'outside'
        outside.mkdir()
        (outside / 'precious.txt').write_text('preserve')
        (self.root / '_site/legal').symlink_to(outside, target_is_directory=True)
        with self.assertRaises(ValueError):
            legal.prepare(self.root)
        self.assertEqual((outside / 'precious.txt').read_text(), 'preserve')
        self.assertEqual(sorted(p.name for p in outside.iterdir()), ['precious.txt'])

    def test_symlinked_license_source_cannot_escape(self):
        path = self.root / 'LICENSE'
        path.unlink()
        path.symlink_to(ROOT / 'LICENSE')
        with self.assertRaises(ValueError):
            legal.prepare(self.root)


if __name__ == '__main__':
    unittest.main(verbosity=2)
