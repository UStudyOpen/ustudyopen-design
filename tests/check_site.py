"""Check local output paths, fragments and theme assets with Python's stdlib."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'

class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.refs, self.ids = path, [], set()
        self.duplicates, self.associations, self.external_scripts = [], [], []
        self.native_duplicate_ids = []
        self.toc_context = None
        self.feed(path.read_text())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'nav' and a.get('id') in ('TOC', 'TOC-body'): self.toc_context = a['id']
        if 'id' in a:
            if a['id'] in self.ids:
                native_style = tag == 'link' and a['id'] in ('quarto-bootstrap', 'quarto-text-highlighting-styles') and any(c in a.get('class', '').split() for c in ('quarto-color-alternate', 'quarto-color-scheme-extra'))
                native_toc = self.toc_context == 'TOC-body' and ((tag == 'a' and a['id'].startswith('toc-')) or (tag == 'h2' and a['id'] == 'toc-title'))
                (self.native_duplicate_ids if native_style or native_toc else self.duplicates).append(a['id'])
            self.ids.add(a['id'])
        for key in ('aria-labelledby', 'aria-describedby', 'aria-controls', 'for'):
            if a.get(key): self.associations.extend(a[key].split())
        if tag == 'script' and a.get('src', '').startswith(('http:', 'https:')):
            self.external_scripts.append(a['src'])
        for key in ('href', 'src'):
            if a.get(key):
                self.refs.append((tag, key, a[key]))

    def handle_endtag(self, tag):
        if tag == 'nav': self.toc_context = None

pages = {p: Page(p) for p in SITE.rglob('*.html')}
errors, checked = [], 0
import sys
sys.path.insert(0, str(ROOT / 'tooling'))
import legal_distribution
legal_distribution.output_checks(ROOT, errors)
theme_pairs = {}
for path, page in pages.items():
    # Counting CSS files alone misses a partial render referencing stale themes.
    themes = {}
    class Themes(HTMLParser):
        def handle_starttag(self, tag, attrs):
            a = dict(attrs)
            if tag == 'link' and a.get('id') == 'quarto-bootstrap' and a.get('data-mode'):
                themes.setdefault(a['data-mode'], set()).add(Path(a['href']).name)
    Themes().feed(path.read_text())
    theme_pairs[str(path.relative_to(SITE))] = {mode: sorted(names) for mode, names in themes.items()}
    if set(themes) != {'light', 'dark'} or any(len(names) != 1 for names in themes.values()):
        errors.append(f'{path.relative_to(SITE)}: expected one theme per mode')
    for tag, attr, ref in page.refs:
        u = urlsplit(ref)
        if u.scheme or u.netloc or ref.startswith('data:'):
            continue
        if u.path.startswith('/'):
            errors.append(f'{path.relative_to(SITE)}: absolute path: {ref}')
            continue
        target = (path.parent / unquote(u.path)).resolve() if u.path else path
        if target.is_dir():
            target /= 'index.html'
        if not target.is_relative_to(SITE.resolve()):
            errors.append(f'{path}: escapes output: {ref}')
        elif not target.exists():
            errors.append(f'{path.relative_to(SITE)}: missing: {ref}')
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:
            errors.append(f'{path.relative_to(SITE)}: missing fragment: {ref}')
        checked += 1
    for identifier in page.duplicates:
        errors.append(f'{path.relative_to(SITE)}: duplicate id: {identifier}')
    for identifier in page.associations:
        if identifier not in page.ids: errors.append(f'{path.relative_to(SITE)}: missing associated id: {identifier}')
    text = path.read_text()
    has_demo = 'Gallery only: illustrative models' in text
    if has_demo != (path.name == 'laboratorio.html'):
        errors.append(f'{path.relative_to(SITE)}: gallery script isolation')
    if 'form.querySelector("#uso-answer")' in text:
        errors.append(f'{path.relative_to(SITE)}: fixed form selector')
    for required in ('quarto-color-scheme-toggle', 'quarto-sidebar', 'uso-skip-link', 'quartoToggleColorScheme'):
        if required not in text:
            errors.append(f'{path.relative_to(SITE)}: missing {required}')
    for mode in ('light', 'dark'):
        if f'data-mode="{mode}"' not in text:
            errors.append(f'{path.relative_to(SITE)}: missing theme {mode}')
    if '/home/' in text or 'file://' in text:
        errors.append(f'{path.relative_to(SITE)}: local machine path')
css = [p for p in (SITE / 'site_libs/bootstrap').glob('bootstrap*.css') if p.name != 'bootstrap-icons.css']
for path in css:
    text = path.read_text()
    for token in ('--uso-bg:', '--uso-primary:', '--uso-control-border:', '.uso-chart'):
        if token not in text:
            errors.append(f'{path.name}: missing {token}')
    if re.search(r'@import[^;]*https?://', text):
        errors.append(f'{path.name}: remote stylesheet import')
# Search result links must remain relative to the project base.
search = json.loads((SITE / 'search.json').read_text())
for item in search:
    if item['href'].startswith('/'):
        errors.append(f'absolute search link: {item["href"]}')
if len(pages) != 5 or len(css) != 2:
    errors.append('expected five pages and two compiled themes')
expected_pages = {'index.html', 'sistema.html', 'componentes.html', 'laboratorio.html', 'unidades/fundamentos.html'}
if set(theme_pairs) != expected_pages:
    errors.append('unexpected public page routes')
if len({json.dumps(pair, sort_keys=True) for pair in theme_pairs.values()}) != 1:
    errors.append('pages reference inconsistent theme pairs (partial/stale render)')
for path in SITE.rglob('*'):
    if path.is_file() and (path.name.startswith('.env') or path.suffix in ('.pem', '.key', '.p12', '.pfx', '.zip', '.tgz') or any(x in path.relative_to(SITE).parts for x in ('artifacts', 'tests', 'docs', '.git', 'gallery'))):
        errors.append(f'unexpected published file: {path.relative_to(SITE)}')
result = {'theme_pairs': theme_pairs, 'native_quarto_duplicate_ids': {str(path.relative_to(SITE)): page.native_duplicate_ids for path, page in pages.items() if page.native_duplicate_ids}, 'external_scripts': sorted({src for page in pages.values() for src in page.external_scripts}), 'pages':len(pages),'local_references':checked,'bootstrap_sheets':len(css),'search_entries':len(search),'errors':errors}
(ROOT / 'artifacts/v0.2').mkdir(parents=True, exist_ok=True)
(ROOT / 'artifacts/v0.2/static-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(bool(errors))
