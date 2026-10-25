"""Render twice from source in empty directories and compare output byte for byte.

Requires exactly Quarto 1.10.18. Only replaces disposable _site after successful
renders; never carries .quarto, _site or a user cache into either build.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
version = subprocess.check_output(['quarto', '--version'], text=True).strip()
if version != '1.10.18':
    raise SystemExit(f'Expected Quarto 1.10.18, got {version}')
sources = ('_quarto.yml', '.quartoignore', '_extensions', 'tooling', 'workflows', 'gallery', 'index.qmd',
           'LICENSE', 'LICENSING.md', 'THIRD-PARTY-NOTICES.md', 'LICENSES',
           'unidades', 'componentes.qmd', 'laboratorio.qmd', 'sistema.qmd')
report_dir = ROOT / 'artifacts/stabilization'
report_dir.mkdir(parents=True, exist_ok=True)
manifests = []
for attempt in (1, 2):
    with tempfile.TemporaryDirectory(prefix='ustudyopen-design-clean-') as temp:
        work = Path(temp)
        for name in sources:
            source, target = ROOT / name, work / name
            if source.is_dir():
                shutil.copytree(source, target)
            else:
                shutil.copy2(source, target)
        env = dict(os.environ, XDG_CACHE_HOME=str(work / '.cache'))
        with (report_dir / f'render-{attempt}.log').open('w') as log:
            subprocess.run(['quarto', 'render'], cwd=work, env=env,
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        site = work / '_site'
        manifests.append({str(p.relative_to(site)): hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(site.rglob('*')) if p.is_file()})
        if attempt == 2:
            if manifests[0] != manifests[1]:
                changed = sorted(k for k in manifests[0].keys() | manifests[1].keys()
                                 if manifests[0].get(k) != manifests[1].get(k))
                raise SystemExit(f'Non-reproducible output: {changed}')
            if (ROOT / '_site').exists():
                shutil.rmtree(ROOT / '_site')
            shutil.copytree(site, ROOT / '_site')
result = {'quarto': version, 'independent_clean_builds': 2,
          'identical_files': len(manifests[0]), 'sha256': manifests[0]}
(report_dir / 'reproducibility.json').write_text(json.dumps(result, indent=2) + '\n')
print(f'PASS: two clean builds, {len(manifests[0])} identical files, Quarto {version}')
