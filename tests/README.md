# Comprobaciones locales v0.2

`check_site.py` y `check_repository.py` usan Python estándar. Las pruebas de navegador usan Deno, WebSocket y CDP del Brave/Chromium instalado; no instalan paquetes. `run-browser.sh` inicia servidores y un navegador desechable con sandbox, limita permisos de Deno y limpia los procesos y el perfil al terminar.

```sh
python3 tests/clean_render.py  # dos renders limpios idénticos; Quarto 1.10.18
python3 tests/check_site.py
python3 tests/check_repository.py
bash tests/run-browser.sh
```

Suites selectivas: `bash tests/run-browser.sh browser|callouts|instances|subpath|sandbox` (elegir una palabra). Puertos locales 4850, 4851 y 9228; las rutas de ejecutables se configuran mediante `USO_BROWSER_BIN` y `USO_DENO_BIN`.

- `browser.mjs`: navegación, tema, búsquedas, teclado, estado y matriz de reflujo.
- `cdp.mjs`: cliente común con timeouts y CDP restringido a loopback.
- `callouts.mjs`: cinco tipos, tres estados, colores calculados, teclado/puntero y capturas.
- `make_fixtures.py` / `instances.mjs`: dos gráficos y formularios desde el HTML renderizado y el include original del laboratorio; detectan dependencia de IDs y estado global.
- `sandbox.mjs`: estado del aislamiento del navegador en su página interna.

Resultados y capturas en `artifacts/v0.2/`, excluidos de Git y del render. [PRUEBAS.md](../docs/PRUEBAS.md) distingue lo ejecutado de lo pendiente y documenta los límites de accesibilidad. Las capturas `before` de esta iteración son evidencia histórica local; no regenerarlas con el CSS v0.2.
