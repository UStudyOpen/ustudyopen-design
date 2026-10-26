# Alcance de las licencias

Copyright (c) 2026 ngulloa para los aportes originales autorizados. La atribución
pública fue elegida expresamente por el titular el 25 de octubre de 2026; no se
atribuye titularidad a la organización GitHub UStudyOpen ni a los asistentes.
El año 2026 está acreditado por los avisos originales de BD/IA y por el registro
de creación del prototipo, la consolidación y la plantilla (CHANGELOG 0.1–0.3,
25 de octubre de 2026). No se deducen años adicionales de fechas de commits.

El encargo del titular del 25 de octubre de 2026 confirma sus facultades sobre
los componentes originales de Precálculo, Bases de Datos, Inteligencia Artificial
y UStudyOpen Design, incluidos los desarrollados con ChatGPT/Codex. Autoriza MIT
para el software propio o autorizado del sistema y la plantilla, y MIT adicional
para los componentes propios extraídos de los tres cursos. La autorización no
abarca obras de terceros. Los permisos previos de los cursos se conservan.

El texto íntegro de MIT está en `LICENSE`. Cubre software original y autorizado:
extensión (SCSS, JS, Lua, configuración, SVG), galería, herramientas, pruebas,
workflows, scaffolding y documentación técnica propia del sistema. Para el
símbolo U se concede el permiso de copyright; no se ofrece una licencia de marca.

No cubre las bibliotecas incorporadas por Quarto al resultado ni las cargadas
por CDN: sus rutas, versiones, titulares y textos están en
`THIRD-PARTY-NOTICES.md` y `LICENSES/`. Los CSS generados combinan componentes
propios MIT y componentes upstream; no se atribuye su totalidad a ngulloa.
Los avisos/banners de terceros se conservan. MIT del sistema no cambia la
licencia académica de un curso que lo utiliza.

## Canales

La extensión instalable contiene LICENSE, LICENSING, PROVENANCE, avisos y textos
upstream dentro de `_extensions/ustudyopen-design/`. La instalación Quarto copia
ese directorio completo. `tooling/sync_course.py` copia la extensión y distribuye
la licencia de herramientas/workflows a `tests/LICENSE-platform.txt` y
`.github/workflows/LICENSE-platform.txt`, con hashes en ambos manifiestos.
`tooling/legal_distribution.py` prepara `_site/legal/` desde estos textos y los
avisos locales del curso, después del render. Es una preparación local; no
modifica `docs/` ni habilita publicación. Véase `docs/LICENCIAS.md`.
