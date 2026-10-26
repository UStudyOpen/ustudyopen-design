# Contraste del código inline y etiquetas de atributos

Corrección local del 25 de octubre de 2026, sobre el snapshot de trabajo 0.2.0. No se crea una versión, tag, commit ni release.

## Diagnóstico antes de modificar el estilo

En Bases de Datos los nombres `rut`, `nombre`, `carrera`, `codigo`, `creditos` y `semestre` son backticks Markdown, renderizados como `<code>` sin clases. Se encuentran, por ejemplo, en `.schema-box > p > code` de `index.qmd` y en el párrafo introductorio de `fundamentos/relaciones-nombradas.qmd`. No son `.concept-tag`, `.badge` ni un `span` de atributo. Hay 86 apariciones inline de esos seis nombres en el HTML inicial del curso.

La hoja Bootstrap generada por Quarto 1.10.18 define `p code:not(.sourceCode), li code:not(.sourceCode), td code:not(.sourceCode)` con especificidad **(0,1,2)**, fondo `rgba(233,236,239,.65)` y padding `.2em`. La extensión definía `p code, li code, td code`, especificidad **(0,0,2)**, con texto `--uso-text` y fondo `--uso-surface-alt`. Aunque se compila después, perdía el fondo por especificidad. El texto claro de la extensión sí ganaba. El fallo ya existía en el prototipo: no nace de un override de Bases de Datos.

La cascada efectiva, registrada antes de editar en `artifacts/inline-code/before.json`, incluye el fondo genérico `code` de Quarto `#f8f9fa`, después la regla más específica semitransparente y la regla de texto compartida. El contenedor `.schema-box` utiliza `--uso-primary-soft` (`#eff6ff` / `#213656`); la prosa está sobre `--uso-bg` (`#f4f6fa` / `#111827`). No hay borde ni sombra efectivos en estos chips. El padding es 2,8 px, el radio 4 px y la fuente 14 px en las capturas a escala CSS normal.

`styles/concepts.css` solo aplica a las etiquetas de conceptos. `styles/compatibility.css` determina el fondo y la geometría del esquema, pero no sobreescribe estos chips. Los antiguos `styles/base.css`, `styles/components.css` y `theme.scss` no están activos. No se elimina ningún override local: ninguno era redundante o conflictivo para este componente.

## Fuente autorizada y alcance

- `_extensions/ustudyopen-design/brand/_brand.yml` y `_brand-dark.yml`: valor de marca `uso-inline-code-bg`, claro `#e2e8f0` y oscuro `#475569`.
- `scss/uso.scss`: publica `--uso-inline-code-bg` y el alias `--uso-inline-code-text: var(--uso-text)`. El texto conserva la identidad existente: `#243247` / `#e8eef7`.
- `scss/_base.scss`: aplica ambos tokens mediante `:where(main.content) :is(p, li, td) > code:not(.sourceCode)`. Su especificidad **(0,1,2)** empata la regla nativa y gana por orden. No usa `!important`.
- `componentes.qmd`: muestra el componente junto al código SQL y los estados editoriales para revisarlo en contexto.

El componente compartido es código inline en la prosa de Quarto. Atributos, identificadores como `Data` y fragmentos SQL inline utilizan el mismo HTML y reciben la corrección coherentemente. No se detectan nombres académicos mediante JavaScript, ni se cambian las fuentes del curso. Los hijos directos excluyen código dentro de `pre` y código envuelto en enlaces; `.sourceCode` queda excluido expresamente. El alcance `main.content` evita la navegación externa al contenido; `:where` no incrementa la especificidad. Los selectores de navegación nativos conservan mayor especificidad. Badges, etiquetas de conceptos, controles y estados editoriales no se modifican.

Se mantiene el padding, tipografía, tamaño y radio nativos. Borde `0 none`, sombra `none`: la superficie pizarra aporta separación sin cambiar dimensiones. No se cambia el token global `surface-alt`, utilizado por bloques y otros componentes.

En claro se elige un pizarra claro algo más marcado que `surface-alt`: su contraste de superficie es 1,13:1 sobre el esquema y 1,14:1 sobre el párrafo, frente a 1,06:1 y 1,12:1 anteriores. En oscuro es 1,60:1 sobre el esquema y 2,01:1 sobre el párrafo. Estos valores describen separación visual de una etiqueta estática; no son el criterio de contraste de texto ni el de controles interactivos.

## Contraste y evidencia

La prueba `tests/inline-code.mjs` compone el alfa sobre los fondos reales antes de calcular luminancia sRGB y contraste WCAG. El objetivo de texto normal de WCAG 2.2 AA es 4,5:1; esto no es una declaración de conformidad de todo el sitio.

| Contexto | Fondo anterior efectivo RGB | Texto anterior y actual | Contraste anterior | Fondo actual | Contraste actual |
|---|---|---|---|---|---|
| Esquema, claro | `(235.1, 239.5, 244.6)` | `#243247` | 11,25:1 | `#e2e8f0` | 10,50:1 |
| Párrafo, claro | `(240.7, 242.65, 244.6)` | `#243247` | 11,60:1 | `#e2e8f0` | 10,50:1 |
| Esquema, oscuro | `(163, 172.3, 185.45)` | `#e8eef7` | 1,96:1 | `#475569` | 6,50:1 |
| Párrafo, oscuro | `(160.9, 166.7, 174.95)` | `#e8eef7` | 2,08:1 | `#475569` | 6,50:1 |

Las capturas antes de la corrección son del render real inicial de Bases de Datos. La muestra del prototipo anterior se inserta en el DOM de prueba con el mismo HTML posteriormente añadido a la galería, usando el CSS anterior; no se retoca el CSS ni se simula el defecto. Las capturas nuevas usan los renders completos corregidos. Se prueban anchos de 320, 390, 768 y 1440 px en ambos temas. Las imágenes se guardan a 390 y 1440 px. Los JSON conservan estilos calculados, reglas coincidentes, contraste y dimensiones.

El recorrido adicional de las 27 páginas abre las soluciones `details` antes de medir: Chromium puede devolver colores cacheados del tema anterior para descendientes de un `details` cerrado, que no se pintan. Se espera a la hoja y al estilo efectivo del componente. No se modifica el comportamiento de los desplegables en el producto.

| Tema | Antes (390 px) | Después (390 px) | Antes (1440 px) | Después (1440 px) |
|---|---|---|---|---|
| Oscuro | [Esquema](../artifacts/inline-code/before-schema-dark-390.png) | [Esquema](../artifacts/inline-code/after-schema-dark-390.png) | [Esquema](../artifacts/inline-code/before-schema-dark-1440.png) | [Esquema](../artifacts/inline-code/after-schema-dark-1440.png) |
| Claro | [Esquema](../artifacts/inline-code/before-schema-light-390.png) | [Esquema](../artifacts/inline-code/after-schema-light-390.png) | [Esquema](../artifacts/inline-code/before-schema-light-1440.png) | [Esquema](../artifacts/inline-code/after-schema-light-1440.png) |

En la misma carpeta se conservan pares `attributes` (párrafo) y `prototype`. La evidencia se mantiene local e ignorada por Git y el render.

El [comparador local](../artifacts/inline-code/comparison.html) presenta juntas las 24 capturas: tres contextos, dos temas, dos anchos y dos estados.

## Reutilización y distribución

La copia de `base-de-datos/_extensions/ustudyopen-design` debe ser idéntica byte por byte al origen central. `base-de-datos/design-vendor.json` registra los SHA-256 del snapshot local, sin presentarlo como release publicada. Una versión futura debe distribuir la extensión completa con su marca y SCSS, siguiendo [DISTRIBUCION.md](DISTRIBUCION.md). Los cursos solo necesitan la extensión y su configuración de marca existente: no necesitan rediseñar estos chips ni copiar colores a sus hojas locales. Esta corrección no inicia actualizaciones de otros repositorios.

## Archivos de esta corrección

En el sistema central cambian los cuatro archivos de marca/SCSS indicados arriba, la muestra de `componentes.qmd` y las guías `docs/TOKENS.md` y `docs/COMPONENTES.md`. Se añaden esta guía y `tests/inline-code.mjs`. El render `_site/` y la evidencia `artifacts/` son salidas locales ignoradas.

En Bases de Datos cambian únicamente los mismos cuatro archivos de la copia de la extensión, `design-vendor.json`, el render completo `docs/` (referencias a las hojas nuevas y CSS compilado) y la nota `review/INLINE_CODE_CONTRAST.md`. Las hojas compiladas reemplazan las anteriores, sin acumular temas obsoletos. No se editan los estilos propios del curso.

Los hashes del estado inicial y la comparación del alcance se conservan en `artifacts/inline-code/initial-files.json` y `scope-audit.json`. Se comprueba que las fuentes académicas, configuraciones de Quarto y publicación, y ambos repositorios excluidos permanecen iguales al inicio de esta tarea. Los cambios locales que ya existían se conservan.

## Verificaciones ejecutadas

| Comprobación | Resultado |
|---|---|
| `tests/clean_render.py` del sistema central | Dos renders limpios completos con Quarto 1.10.18; 25 archivos idénticos, 5 páginas. |
| `tests/render_clean.py` del curso | Render limpio completo; 27 páginas. |
| `check_site.py` de ambos proyectos | Sin enlaces locales rotos: 278 referencias locales en el prototipo, 3325 en el curso y su recurso CSS local. |
| `check_repository.py` y `check_design.py` | Sin errores; 11 archivos vendor verificados, 41 fuentes académicas intactas, 27 rutas y dos hojas de tema coherentes. |
| `node --test tests/*.test.js` del curso | 67/67 pruebas académicas correctas, sin omisiones. |
| `tests/sql_examples.py` | Ejemplos compatibles con SQLite correctos; MERGE/TRUNCATE no se ejecutan porque no son ejemplos SQLite. |
| `tests/inline-code.mjs after` | 24 casos en tres contextos, cuatro anchos y dos temas; dimensiones idénticas a la línea base. Código en bloque y resaltado, enlaces, navegación, badges, conceptos y estados sin cambios de estilos calculados. |
| Recorrido adicional del código inline del curso | 27 páginas × 2 temas; 969 muestras por tema; mínimo 6,50:1 en oscuro y 10,50:1 en claro. Sin errores JS ni fallos de recursos. |
| `tests/run-browser.sh` del prototipo | 71 comprobaciones generales, 109 de callouts, 7 de instancias y 45 de subruta correctas; sandbox activo, sin errores JS/red. |
| Simuladores del curso en ambos temas | Ocho suites B+, hashing, planes y buffer; 3044 estados y 50 capturas, sin errores de consola/JS ni recursos fallidos. |
| Auditoría general del curso | 395 comprobaciones correctas, 0 fallos; 216 combinaciones de 27 páginas × 4 anchos × 2 temas, 72 verificaciones de estado de simuladores y 40 capturas. Sin errores JS/red. |
| Impresión y regiones de planes del curso | 18/18 comprobaciones de impresión, 0 errores; cuatro capturas de regiones de planes conservan el mismo estado al cambiar de tema. |

Los informes de la prueba focalizada están en `artifacts/inline-code/{before,after}.json`; los generales del prototipo en `artifacts/v0.2/` y los del curso en `base-de-datos/artifacts/design-v0.2/`. Los logs académicos de esta tarea usan prefijo `inline-code-`. `git diff --check` de las fuentes pasa. Al incluir el HTML generado de Bases de Datos se señalan espacios finales emitidos por la plantilla de Quarto; no se normaliza manualmente el render.

## Reproducir la prueba focalizada

Con los dos renders completos disponibles, servir `base-de-datos/docs` en `127.0.0.1:4860` y `ustudyopen-design/_site` en `127.0.0.1:4861`. Desde el repositorio de diseño ejecutar `node tests/inline-code.mjs after`, con el Node y Playwright ya instalados en este entorno. `PLAYWRIGHT_MODULE` y `BROWSER_EXECUTABLE` permiten usar otras rutas existentes. El navegador se lanza con sandbox. No se instalan dependencias. `before.json` es una línea base histórica local: no regenerarla con el estilo corregido. La comprobación comparativa necesita esa línea base; las suites generales de ambos proyectos siguen siendo independientes de ella.
