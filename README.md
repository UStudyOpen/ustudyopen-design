# UStudyOpen Design

Estado actual: **0.3.0, instantánea local sin etiqueta ni release**, con identidad 0.2 preservada e integración en los tres cursos. Consultar [arquitectura y distribución actual](docs/ARQUITECTURA_0.3.md). Los apartados de la entrega 0.2 que siguen conservan su contexto histórico; la consolidación actual se documenta al final.

## Antecedente visual 0.2

Mejora incremental de la identidad aprobada en v0.1. Galería local y extensión compartida para Quarto; esta entrega no migra asignaturas. Quarto **1.10.18** es la versión validada. El rango declarado sigue `>=1.10.18 <1.11.0`; no se ha validado toda la serie.

Callouts con cabecera azul pizarra en oscuro, contraste comprobado y desplegables accesibles por teclado; acentos azules y verde azulado discretos; JavaScript demostrativo separado; pruebas con sandbox y documentación de distribución/licencia.

## Revisar la entrega

- [Informe v0.2, archivos, comparación visual y riesgos](docs/ENTREGA_V0.2.md).
- [Resultados y reproducción de pruebas](docs/PRUEBAS.md).
- [Causa CSS y corrección de los callouts](docs/CALLOUTS.md).
- [Distribución por versiones y PR con aprobación humana](docs/DISTRIBUCION.md).
- [Procedencia y propuesta de licencia](docs/LICENCIAS.md).
- [Estabilización: diagnóstico del ZIP y compilación reproducible](docs/ESTABILIZACION_V0.2.md).

## Ejecutar

Desde esta carpeta:

```sh
quarto --version  # 1.10.18
quarto render
quarto preview --host 127.0.0.1 --port 4848 --no-browser
```

Abrir <http://127.0.0.1:4848/>. `Ctrl+C` detiene la vista previa. Servir por HTTP para validar búsqueda y navegación. No ejecutar renders simultáneos sobre `_site/`.

Renderizar no requiere npm, frameworks adicionales ni ejecutar los bloques Python/SQL ilustrativos. La fuente tipográfica es del sistema y los recursos de Quarto son locales. La plantilla nativa carga **MathJax desde jsDelivr y un polyfill ES6 desde cdnjs** en páginas con matemática; no se garantiza funcionamiento matemático sin red. Se conservan las dependencias de Quarto 1.10.18; su fijación exacta, alojamiento local y política CSP/SRI están pendientes.

## Validar

```sh
python3 tests/clean_render.py
python3 tests/check_site.py
python3 tests/check_repository.py
bash tests/run-browser.sh
```

El navegador de prueba requiere Brave/Chromium y Deno existentes. El script usa por defecto las rutas de esta instalación; pueden configurarse con `USO_BROWSER_BIN` y `USO_DENO_BIN`. Usa los puertos locales 4850, 4851 y 9228, comprueba que estén libres, crea un perfil desechable y lo elimina al terminar. **Mantiene el sandbox** y falla si el entorno no permite ejecutarlo. No requiere privilegios ni instalación de paquetes. Consultar [pruebas](docs/PRUEBAS.md) para límites y ejecución por suite.

## Estructura

```text
_quarto.yml                         # Solo la galería: navegación, marca, salida
_extensions/ustudyopen-design/
  _extension.yml                    # Formato ustudyopen-design-html 0.2.0
  brand/_brand{,-dark}.yml           # Única fuente de colores semánticos
  scss/uso.scss                     # Entrada y tokens --uso-*
  scss/_callouts.scss               # Cascada, iconos y variantes nativas
  scss/_{base,layout,components}.scss
  assets/after-body.html            # Mejoras compartidas de accesibilidad
  assets/favicon.svg
  PROVENANCE.md                     # Procedencia y licencia pendiente
gallery/laboratorio.html           # JS exclusivo del laboratorio
index.qmd, unidades/, *.qmd          # Contenido de muestra
docs/                              # Contratos, resultados y propuestas
tests/                             # Python estándar y Deno/CDP sin paquetes
artifacts/                         # Evidencia local y perfiles, ignorados
_site/, .quarto/                    # Salida/caché generada, ignorada
```

[Arquitectura](docs/ARQUITECTURA.md), [tokens](docs/TOKENS.md) y [componentes](docs/COMPONENTES.md) describen los contratos. El tema y su persistencia siguen siendo de Quarto; la extensión no decide el currículo, las rutas ni la publicación de un curso.

`artifacts/` está excluido tanto de Git como del render. Las capturas antes/después se conservan localmente; si se necesitan en una revisión remota, seleccionar únicamente la evidencia aprobada, nunca subir perfiles ni el directorio completo. `.gitignore` reduce errores accidentales, pero no sustituye revisar el contenido a publicar ni elimina archivos que ya estén versionados.

No se ha aplicado una licencia nueva. La propuesta MIT está condicionada a resolver derechos de los estilos de origen. La entrega inicial v0.2 no migró asignaturas.

La estabilización posterior conserva esta identidad, verifica dos compilaciones limpias idénticas y prepara el [piloto local de Bases de Datos](../base-de-datos/review/DESIGN_V0.2.md). El trabajo queda en ramas locales, sin commits, push ni despliegue. Inteligencia Artificial y Precálculo permanecen sin cambios. El ZIP original se conserva como evidencia; `_site/` contiene la compilación corregida.


## Consolidación local 0.3.0

La arquitectura compartida, los estados y los workflows para cursos están documentados en [ARQUITECTURA_0.3.md](docs/ARQUITECTURA_0.3.md). La identidad 0.2 se conserva. La nueva versión es una instantánea local por SHA-256, sin tag, release ni nueva licencia. Para instalar o actualizar un curso con metadatos existentes:

```sh
python3 tooling/sync_course.py ../nombre-del-curso
```

La herramienta rechaza modificaciones independientes de archivos gestionados. Revisar los dos manifiestos y las diferencias antes de integrar. La documentación histórica v0.2 y sus resultados se conserva como referencia, sin presentarlos como pruebas de esta iteración.

La continuación de la revisión añade comprobaciones de rutas, protección frente a archivos ajenos y restauración de actualizaciones o de `_site/` que fallen. Antes de distribuir herramientas, ejecutar también `python3 tests/test_tooling.py`; consultar las garantías y límites de recuperación en [ARQUITECTURA_0.3.md](docs/ARQUITECTURA_0.3.md).

## Licencias adoptadas

MIT para software y documentación propia/autorizada; [alcance](LICENSING.md),
[procedencia](_extensions/ustudyopen-design/PROVENANCE.md) y
[terceros](THIRD-PARTY-NOTICES.md). Contenido académico de los cursos: CC BY-NC 4.0.
