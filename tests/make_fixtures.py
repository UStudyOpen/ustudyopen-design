"""Build a disposable two-instance page from the *rendered* gallery and its source script."""
from pathlib import Path
import re

root = Path(__file__).resolve().parents[1]
html = (root / '_site/laboratorio.html').read_text()
graph = re.search(r'<section class="uso-demo".*?</section>', html, re.S).group()
form = re.search(r'<form data-uso-form.*?</form>', html, re.S).group()

def duplicate(markup):
    identifiers = re.findall(r'\bid="([^"]+)"', markup)
    # Replace complete identifiers in id, for and ARIA references together.
    for identifier in sorted(identifiers, key=len, reverse=True):
        markup = re.sub(r'(?<![\w-])'+re.escape(identifier)+r'(?![\w-])', 'second-'+identifier, markup)
    return markup

out = root / 'artifacts/v0.2/subpath'
out.mkdir(parents=True, exist_ok=True)
(out / 'instances.html').write_text('<!doctype html><html lang="es"><meta charset="utf-8"><title>Prueba local de instancias</title><link rel="icon" href="data:,"><body><main>'+graph+duplicate(graph)+form+duplicate(form)+'</main>'+(root/'gallery/laboratorio.html').read_text()+'</body></html>')
