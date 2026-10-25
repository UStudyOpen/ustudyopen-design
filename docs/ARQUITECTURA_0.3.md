# Arquitectura local 0.3.0

Esta versión es una instantánea local identificada por manifiestos SHA-256. No existe una etiqueta ni release 0.3.0 publicada por este trabajo. Quarto se fija en **1.10.18**; no se cambia la identidad aprobada de la versión 0.2.

## Responsabilidades

- `_extensions/ustudyopen-design/`: marca clara/oscura, tokens, SCSS, componentes y mejoras accesibles. El selector y la persistencia del tema pertenecen a Quarto. No observa el tema ni reinicializa actividades.
- `tooling/`: compilación aislada, controles de integridad, estados, rutas y publicación; instalador CI con checksum y sincronización de versiones.
- `workflows/`: plantillas comunes de validación y despliegue. Se distribuyen como archivos revisables; hoy no se añade un repositorio de infraestructura ni una dependencia remota a una rama mutable.
- Curso: contenido, bibliografía, registro `course.yml`, geometría de visualizaciones y algoritmos. Sus pruebas académicas no se extraen al repositorio central.
- `ustudyopen-template`: punto de partida para asignaturas nuevas; no actualiza cursos existentes.

## Componentes y compatibilidad

Clases públicas: `.uso-hero`, `.uso-actions`, `.topic-grid`, `.topic-card`, `.uso-status`, `.uso-definition`, `.uso-theorem`, `.uso-academic`, `.uso-example`, `.uso-exercise`, `.uso-solution`, `.uso-formula`, `.formula-grid`, `.formula-card`, `.uso-summary`, `.uso-simulator`, `.uso-field`, `.uso-table-wrap`. Se conservan alias históricos (`.schema-box`, `.summary-box`, `.concept-box`, etc.) para no reescribir lecciones ni alterar sus anclas. Las soluciones nuevas deben usar `details/summary` nativos.

Los chips de atributos usan texto semántico sobre `--uso-inline-code-bg`. Las etiquetas de conceptos usan `--uso-text` sobre `--uso-primary-soft`: no utilizan texto blanco sobre fondos claros. Los SVG especializados solo se adaptan desde CSS con ámbito de la actividad; no existe una regla global de colores para SVG.

`course.yml` contiene JSON válido como YAML (objeto `course`), para validarlo con la biblioteca estándar de Python y cargarlo con Quarto sin dependencias adicionales. Contiene temario, objetivos, páginas obligatorias y temas futuros explícitos. Cada página declara además `ustudy-status` y `ustudy-reviewed`; el validador exige concordancia. Un curso solo puede declararse `lista` si todas sus páginas y temas previstos obligatorios están listos y revisados. Las comprobaciones técnicas no otorgan revisión académica.

El filtro Lua presenta una etiqueta textual accesible. No se agregan secciones vacías a las lecciones. Los cuerpos originales, algoritmos y bibliografías se comprueban mediante `tests/academic-integrity.json`; las correcciones de atributos ARIA, foco y conservación de title/desc SVG se registran como reemplazos de presentación reversibles: el validador reconstruye los bytes originales y comprueba su hash, sin cambiar ecuaciones ni algoritmos; las URL y anclas originales mediante `tests/route-baseline.json`. Para cambios académicos futuros, actualizar esos registros únicamente como parte de una revisión explícita.

## Instalar, actualizar y revertir

1. Guardar las modificaciones locales y revisar su procedencia. La herramienta rechaza cambios independientes en archivos gestionados.
2. Desde la raíz de `ustudyopen-design`, ejecutar `python3 tooling/sync_course.py ../nombre-del-curso`.
3. Revisar `design-vendor.json` y `platform-vendor.json`, incluidos versión anterior/nueva y hashes. Los bytes de las copias deben corresponder al origen central.
4. En el curso: `python3 tests/render_clean.py`, `python3 tests/run_course.py`, `python3 tests/platform_validate.py` y sus suites de navegador. Comparar capturas claras/oscuras y casos móviles.
5. Preparar posteriormente un PR independiente por curso con versiones, archivos, compatibilidad, resultados y comparaciones. Este trabajo no crea PR ni automatización de actualizaciones masivas.

Para una futura versión publicada, usar SemVer: patch para correcciones compatibles, minor para componentes y capacidades compatibles, major para clases/tokens o requisitos incompatibles. Fijar una etiqueta inmutable aprobada y registrar también su commit y hashes. Nunca depender de `main` como versión. La instalación estándar de Quarto admite `quarto add UStudyOpen/ustudyopen-design@<etiqueta-aprobada>`; no ejecutarla ahora contra una versión inexistente. La sincronización local instala también herramientas y workflows, que `quarto add` por sí solo no distribuye.

Para revertir una actualización, restaurar el conjunto completo anterior de extensión, herramientas, workflows y ambos manifiestos desde la instantánea revisada, sin restaurar ni sobrescribir contenido del curso. Recompilar y ejecutar las mismas pruebas. No usar `git reset --hard` ni regenerar manifiestos para ocultar diferencias. En esta etapa los respaldos auditados del workspace incluyen también modificaciones previas del usuario; extraerlos primero en una carpeta separada y comparar antes de copiar.

## Dependencias y CI

CI usa Ubuntu 24.04, Python 3.14.8, Node 24.21.0 y Quarto 1.10.18. El instalador descarga el tarball oficial, verifica SHA-256 `afad071b5bd22c02f2d300695743189d3650e0537a53073e654b630cff2b0c73` obtenido del API oficial de la release, extrae mediante el filtro seguro de Python y no requiere root. No ejecuta instaladores remotos ni instala dependencias de notebooks.

Las acciones se fijan por SHA completo en `workflows/action-pins.json`. El artefacto Pages se empaqueta como `artifact.tar` y se sube con `actions/upload-artifact` fijada por SHA; se evita la dependencia transitiva mutable `actions/upload-artifact@v4` del composite oficial `upload-pages-artifact@v3`. El despliegue usa la acción oficial `actions/deploy-pages`. El formato tar y sus restricciones siguen la [documentación oficial de artefactos Pages](https://github.com/actions/upload-pages-artifact).

`tests/post_render.py` elimina exclusivamente el tag del polyfill ES6 obsoleto y sin versión que inserta Quarto 1.10.18. Los navegadores modernos requeridos ya soportan ES6. MathJax se fija en 4.1.3; todavía se carga desde jsDelivr y requiere red. No se afirma funcionamiento completamente offline ni verificación SRI de recursos CDN. Bootstrap y demás dependencias incorporadas se fijan indirectamente mediante el tarball Quarto y conservan sus avisos.

Los workflows permanecen sin publicar: solo disparo manual, variable `USO_PAGES_ENABLED` requerida, referencia `refs/heads/main`, texto `PUBLICAR`, artefacto generado después de todos los checks y job `deploy` dependiente de `build`. Antes de activar se debe proteger `main` y configurar el entorno `github-pages` con revisión humana obligatoria. Los PR nunca reciben permisos Pages ni OIDC. Las pruebas locales y el lint no equivalen a una ejecución real en GitHub.

## Licencias

El titular autorizó MIT para software propio/autorizado del sistema y plantilla,
y MIT adicional para componentes propios extraídos de BD/IA/Precálculo.
Atribución pública: ngulloa. Los contenidos de los tres cursos utilizan
CC BY-NC 4.0. Véanse [alcance](../LICENSING.md), [licencias](LICENCIAS.md)
y el PROVENANCE instalado. Se conservan todos los permisos upstream.
Los informes de entregas 0.1/0.2 describen su estado histórico anterior a
esta autorización y no sustituyen el mapa actual.


La activación automática posterior debe prepararse como una actualización central revisada del workflow y distribuirse con sus manifiestos: editar una copia gestionada sin actualizarlos hace fallar CI deliberadamente. El validador solo admite un evento push de despliegue cuando `course.pages_automation_approved` sea el booleano `true`, declarado después de aprobación expresa. Este metadato no está activado en ningún curso ni en la plantilla; el workflow actual sigue sin trigger push. Los procedimientos MIGRATION.md incluyen el orden y las condiciones exactas de la transición.

## Continuación local: protección de actualizaciones y compilación

Las herramientas compartidas incorporan `safe_paths.py` (biblioteca estándar de Python). Antes de leer archivos declarados por un manifiesto o escribir destinos se rechazan rutas absolutas, recorridos `..`, rutas de Windows y enlaces simbólicos en cualquiera de sus componentes. La compilación tampoco sigue enlaces de las fuentes publicables; Git, docs heredados, cachés, artefactos y archivos de entorno permanecen excluidos.

El actualizador ya no tiene una excepción que permita sobrescribir un `tests/render_clean.py` ajeno. Tanto en una instalación inicial como al añadir nuevos archivos gestionados a una versión existente, los archivos ajenos provocan una salida con error antes de cambiar el curso. Conservar y comparar ese trabajo por separado; no borrar archivos para silenciar la protección.

La instalación prepara y verifica todos los archivos antes de modificar destinos y vuelve a comprobar sus hashes. Los archivos anteriores se respaldan mediante renombrados locales y los manifiestos se escriben al final. Un error de copia, de renombrado o una interrupción controlada restaura los archivos anteriores, incluyendo ambos manifiestos. No se promete una transacción indivisible entre todos los archivos frente a pérdida de energía o SIGKILL, ni uso concurrente con compilaciones.

Si la restauración también falla, se conserva `.ustudyopen-sync-*/recovery.json` junto con `backup/` y se muestra su ruta. Examinar esos archivos, comparar los hashes y recuperar solo los archivos gestionados necesarios; no borrar la carpeta ni sobrescribir cambios posteriores sin revisar. Una carpeta de actualización incompleta bloquea la validación deliberadamente. Los fallos normales que se restauran correctamente limpian su carpeta temporal.

La salida `_site/` también se copia por completo antes de sustituir el directorio anterior. Si falla la promoción se restaura el sitio previo; `docs/` no se utiliza como destino ni como respaldo temporal. Ante un fallo adicional de restauración se conserva la copia anterior y se informa de su ubicación.

Pruebas de estas garantías: `python3 tests/test_tooling.py` en el repositorio de diseño. Las pruebas utilizan únicamente carpetas temporales, simulan errores e interrupciones y no modifican cursos reales ni servicios remotos. La instantánea sigue siendo 0.3.0 local, sin etiqueta ni release; los nuevos manifiestos registran los bytes exactos de las herramientas actualizadas.

## Continuación local: foco y ampliación de texto

Los enlaces permanentes generados por AnchorJS conservan sus destinos y se hacen visibles con `:focus-visible`; reciben un nombre accesible en español después de la inicialización nativa de Quarto. El área vacía redundante de la navegación secundaria no se añade a la tabulación. Los botones reales y los desplegables mantienen sus manejadores nativos.

La navegación anterior/siguiente permite reducir y dividir sus textos dentro del espacio disponible al ampliar las fuentes. Las seis regiones de gráficos y del triángulo de Pascal en Precálculo se hacen alcanzables por teclado, con nombres específicos. Esos atributos pertenecen al curso y se registran como reemplazos de presentación reversibles, sin alterar cálculos ni los hashes de los originales reconstruidos.

La auditoría complementaria examina el árbol de accesibilidad de Chromium, transiciones reales de Tab y duplicación de la fuente raíz. Esta última es una prueba adicional de reflujo, no una ejecución de zoom nativo del navegador. El puntero no permite juzgar la superposición de voz de MathJax: sus focos se registran aparte para revisión con tecnologías de asistencia. Permanecen necesarias la comprobación con lector de pantalla y la revisión manual de accesibilidad; no se declara conformidad WCAG completa.
