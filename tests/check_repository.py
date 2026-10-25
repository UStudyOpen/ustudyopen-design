"""Check publication hygiene without printing potentially sensitive source values."""
from pathlib import Path
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
errors = []
import sys
sys.path.insert(0, str(ROOT / 'tooling'))
import legal_distribution
legal_distribution.source_checks(ROOT, errors)

candidates = ['.env', '.env.local', '.env.production', 'credentials.json', 'private.key', 'certificate.pem', '_site/index.html', '.quarto/test', 'artifacts/browser-profile/Local State', 'release.zip', 'node_modules/a']
for candidate in candidates:
    if subprocess.run(['git', 'check-ignore', '-q', candidate], cwd=ROOT).returncode:
        errors.append(f'not ignored: {candidate}')
if subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode:
    errors.append('git diff --check failed')
shared = ROOT / '_extensions/ustudyopen-design'
for path in shared.rglob('*'):
    if path.is_symlink(): errors.append(f'extension symlink: {path.relative_to(ROOT)}')
    if path.is_file() and path.stat().st_mode & 0o111: errors.append(f'unnecessary executable: {path.relative_to(ROOT)}')
source = (shared / 'assets/after-body.html').read_text()
if any(marker in source for marker in ('data-uso-demo', 'data-uso-form', '#uso-answer', 'data-line')):
    errors.append('shared JavaScript contains gallery behavior')
# A limited high-confidence scan; this is not a credential-audit certification.
secret = re.compile(r'(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}|sk-proj-[A-Za-z0-9_-]{30,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----)')
paths = []
for directory in ['_extensions', 'gallery', 'tests', 'docs']:
    paths.extend(p for p in (ROOT / directory).rglob('*') if p.is_file())
paths.extend(p for p in ROOT.iterdir() if p.is_file())
for path in paths:
    if secret.search(path.read_text(errors='ignore')):
        errors.append(f'possible secret in {path.relative_to(ROOT)}; inspect locally')
result = {'ignore_probes': len(candidates), 'scanned_source_files': len(paths), 'errors': errors}
(ROOT / 'artifacts/v0.2').mkdir(parents=True, exist_ok=True)
(ROOT / 'artifacts/v0.2/hygiene-results.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
raise SystemExit(bool(errors))
