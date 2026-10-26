"""Install a hashed local snapshot, preserving unmanaged files and failed updates.

Usage: python3 tooling/sync_course.py ../course
No network, Git writes or publishing. Stop builds while synchronizing a course.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile

import licensing

from safe_paths import UnsafePath, checked_path, project_files

SOURCE = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_lock(path):
    try:
        files = json.loads(path.read_text())['files']
        if not isinstance(files, dict) or any(not isinstance(sha, str) or not re.fullmatch('[0-9a-f]{64}', sha)
                                               for sha in files.values()):
            raise ValueError('invalid file digests')
        return files
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError('Invalid manifest: ' + path.name) from error


def inspect(target):
    """Complete preflight: no destination changes are made here."""
    if not checked_path(target, 'course.yml').is_file():
        raise ValueError('Target must contain course.yml')
    extension = '_extensions/ustudyopen-design'
    source = checked_path(SOURCE, extension)
    source_files = project_files(source)
    if not source_files:
        raise ValueError('The source extension is empty')
    dest = checked_path(target, extension)
    lock = checked_path(target, 'design-vendor.json')
    previous = read_lock(lock) if lock.exists() else {}
    for name, sha in previous.items():
        path = checked_path(target, extension + '/' + name)
        if not path.is_file() or digest(path) != sha:
            raise ValueError('Local extension edits detected: ' + name)
    actual = {p.relative_to(dest).as_posix() for p in project_files(dest)} if dest.exists() else set()
    if actual != set(previous):
        raise ValueError('Unmanaged or missing extension files; inspect before installing')
    managed = {'tests/' + name: 'tooling/' + name for name in
               ['platform_validate.py', 'render_clean.py', 'post_render.py', 'install_quarto.py',
                'browser_course.py', 'browser_client.mjs', 'safe_paths.py', 'legal_distribution.py', 'licensing.py',
                'pages_authorization.py']}
    managed.update({'.github/workflows/' + name: 'workflows/' + name for name in ['validate.yml', 'deploy.yml']})
    managed['tests/LICENSE-platform.txt'] = 'tooling/LICENSE'
    managed['.github/workflows/LICENSE-platform.txt'] = 'workflows/LICENSE'
    managed['tests/action-pins.json'] = 'workflows/action-pins.json'
    if checked_path(target, 'licensing.json').exists():
        managed['tests/requirements-licensing.txt'] = 'tooling/requirements-licensing.txt'
        managed['tests/licensing-policy.json'] = 'LICENSES/policy.json'
        managed['LICENSES/SHARED-NOTICES.md'] = 'THIRD-PARTY-NOTICES.md'
        local_legal = json.loads((target / 'licensing.json').read_text())
        course_license = json.loads((target / 'course.yml').read_text()).get('course', {}).get('license')
        central_policy = json.loads(checked_path(SOURCE, 'LICENSES/policy.json').read_text())
        license_ids = {central_policy['categories']['platform']}
        academic = central_policy['categories']['academic_default'] if local_legal.get('is_template') else course_license
        if academic and academic != 'pendiente-de-aclaracion':
            license_ids.update(t for t in re.findall(r'[A-Za-z0-9.+-]+', academic) if t not in {'AND', 'OR', 'WITH'})
        for entry in local_legal.get('third_party', []) + local_legal.get('groups', []):
            license_ids.update(t for t in re.findall(r'[A-Za-z0-9.+-]+', entry.get('license', '')) if t not in {'AND', 'OR', 'WITH'})
        for name in sorted(license_ids):
            managed['LICENSES/' + name + '.txt'] = 'LICENSES/' + name + '.txt'
        managed['REUSE.toml'] = None
    platform = checked_path(target, 'platform-vendor.json')
    old_platform = read_lock(platform) if platform.exists() else {}
    retired = (set(old_platform) - set(managed)) & {p for p in old_platform if p.startswith('LICENSES/') and re.fullmatch(r'LICENSES/[A-Za-z0-9.+-]+\.txt', p) and checked_path(SOURCE, p).is_file()}
    if set(old_platform) - set(managed) - retired:
        raise ValueError('Unmanaged platform manifest path')
    for name in set(old_platform) | set(managed):
        path = checked_path(target, name)
        if name in old_platform:
            if not path.is_file() or digest(path) != old_platform[name]:
                raise ValueError('Local platform edits detected: ' + name)
        elif path.exists() and name.startswith('LICENSES/') and managed[name] and path.is_file() and digest(path) == digest(checked_path(SOURCE, managed[name])):
            pass  # Adopt only byte-identical canonical legal texts; no overwrite permission inferred.
        elif path.exists():
            raise ValueError('Unmanaged platform file exists; preserve and reconcile: ' + name)
    writes = {extension + '/' + p.relative_to(source).as_posix(): (p, digest(p)) for p in source_files}
    for name, source_name in managed.items():
        if source_name is None:
            data = licensing.annotations(target, list(managed), central_policy).encode()
            writes[name] = (data, hashlib.sha256(data).hexdigest())
            continue
        path = checked_path(SOURCE, source_name)
        if not path.is_file():
            raise ValueError('Missing managed source: ' + source_name)
        if name == '.github/workflows/deploy.yml':
            approved = json.loads((target / 'course.yml').read_text()).get('course', {}).get('pages_automation_approved') is True
            data = path.read_text().replace('  # AUTOMATIC_PAGES_TRIGGER',
                                          '  push:\n    branches: [main]' if approved else '  # Automatic publication not approved for this course.').encode()
            writes[name] = (data, hashlib.sha256(data).hexdigest())
        else:
            writes[name] = (path, digest(path))
    files = {p.relative_to(source).as_posix(): writes[extension + '/' + p.relative_to(source).as_posix()][1]
             for p in source_files}
    manifests = {
        'design-vendor.json': {'name': 'ustudyopen-design', 'version': '0.3.0', 'quarto': '1.10.18',
                              'source': 'UStudyOpen/ustudyopen-design',
                              'source_kind': 'local working-tree snapshot; not a tagged or approved release', 'files': files},
        'platform-vendor.json': {'version': '0.3.0', 'source': 'UStudyOpen/ustudyopen-design/tooling + workflows',
                                'files': {name: writes[name][1] for name in managed}},
    }
    removals = {extension + '/' + name for name in set(previous) - set(files)} | retired
    names = set(writes) | set(manifests) | removals
    original = {}
    for name in names:
        path = checked_path(target, name)
        if path.exists() and not path.is_file():
            raise ValueError('Destination is not a regular file: ' + name)
        original[name] = digest(path) if path.exists() else None
    return writes, manifests, removals, original


def sync(target, dry_run=False, check=False):
    if Path(target).is_symlink():
        raise SystemExit('Symlink course roots are not supported')
    target = Path(target).resolve()
    stage = None
    preserve_stage = False
    try:
        writes, manifests, removals, original = inspect(target)
        changes = []
        for name, (source, sha) in writes.items():
            if original[name] != sha:
                changes.append(name)
        for name, data in manifests.items():
            sha = hashlib.sha256((json.dumps(data, indent=2) + '\n').encode()).hexdigest()
            if original[name] != sha:
                changes.append(name)
        changes = sorted(set(changes) | removals)
        print(json.dumps({'course': target.name, 'changes': changes}, indent=2))
        if dry_run or check:
            if check and changes:
                raise ValueError('Synchronization required')
            return changes
        if not changes:
            return []
        stage = Path(tempfile.mkdtemp(prefix='.ustudyopen-sync-', dir=target))
        payload, backup = stage / 'new', stage / 'backup'
        for name, (source, sha) in writes.items():
            output = payload / name
            output.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(source, bytes):
                output.write_bytes(source)
            else:
                shutil.copy2(source, output)
            if digest(output) != sha:
                raise ValueError('Source changed while staging: ' + name)
        for name, data in manifests.items():
            output = payload / name
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(json.dumps(data, indent=2) + '\n')
        for name, sha in original.items():
            path = checked_path(target, name)
            actual = digest(path) if path.exists() and path.is_file() else None
            if actual != sha or (path.exists() and not path.is_file()):
                raise ValueError('Destination changed while staging: ' + name)
        plan = [name for name in sorted(set(writes) | removals) + sorted(manifests) if name in changes]
        (stage / 'recovery.json').write_text(json.dumps({'original': original, 'plan': plan}, indent=2) + '\n')
        touched, created_dirs = [], []
        try:
            for name in plan:
                path = checked_path(target, name)
                missing = []
                parent = path.parent
                while not parent.exists():
                    missing.append(parent)
                    parent = parent.parent
                for directory in reversed(missing):
                    directory.mkdir()
                    created_dirs.append(directory)
                old = backup / name
                touched.append(name)
                if path.exists():
                    old.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(path, old)
                if name not in removals:
                    os.replace(payload / name, checked_path(target, name))
        except BaseException:
            failures = []
            for name in reversed(touched):
                try:
                    path = checked_path(target, name)
                    if (backup / name).exists():
                        os.replace(backup / name, path)
                    elif original[name] is None and path.exists():
                        path.unlink()
                except (OSError, UnsafePath):
                    failures.append(name)
            for directory in reversed(created_dirs):
                try:
                    directory.rmdir()
                except OSError:
                    pass
            if failures:
                preserve_stage = True
                raise RuntimeError('Rollback incomplete; recovery backup preserved at ' + str(stage))
            raise
    except (OSError, ValueError, RuntimeError) as error:
        raise SystemExit(str(error)) from error
    finally:
        if stage is not None and not preserve_stage:
            shutil.rmtree(stage)
    print(f'Installed local 0.3.0 snapshot in {target.name}: {len(manifests["design-vendor.json"]["files"])} extension files, '
          f'{len(manifests["platform-vendor.json"]["files"])} platform files')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('course', type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    sync(args.course, dry_run=args.dry_run, check=args.check)
