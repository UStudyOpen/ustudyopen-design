# Automatización incremental de licencias — política 1.0.0

## Auditoría y decisiones

Verificación inicial: 20 commits locales alcanzables y `git fsck --full` en los
cinco repositorios. Diseño: 5; BD: 4; IA: 4; Precálculo: 5; plantilla: 2.
El inventario previo de 474 decisiones y los documentos aprobados se conservaron.
La evidencia inicial y los hashes de páginas/docs están en
`../../review/automatizacion-licencias-2026-10-25/baseline.json` (evidencia local,
no dependencia de la herramienta). BD ya tenía cambios sin commit en docs/review.

- Correcto: MIT propio/autorizado, CC BY-NC académico, atribución ngulloa,
  procedencia de extracciones, Apache-2.0/Unlicense preservados; extensión autónoma;
  hashes vendor; sincronización transaccional y distribución HTML.
- Implementado sin automatizar: elección legal al crear cursos e inventario de altas.
- Duplicado: documentos narrativos e inventarios históricos por consumidor.
  Se conservan íntegros como evidencia; el nuevo canal compartido y la política se
  sincronizan. No se convierten excepciones históricas en política global.
- Nuevo: política versionada, configuración local mínima, REUSE incremental,
  generador de cursos, comprobación de procedencia y propuestas locales de actualización.

Las ocho regresiones legales previas cubren: curso con elección propia, extensión
instalable, reproducibilidad HTML, licencia omitida del output, aviso fuente ausente,
texto upstream alterado y enlaces simbólicos de origen/destino. No se sustituyeron.

## Fuente única y canales

`LICENSES/policy.json` es la fuente autorizada de categorías, versión, titular,
SPDX, compatibilidad y distribución. Las autorizaciones originales siguen en
LICENSING y PROVENANCE. `LICENSES/upstream.json` y el inventario de la extensión
conservan versión, URL, licencia, rutas y hash de textos externos ya verificados;
no se reescriben ni sustituyen. La política referencia ese inventario.

La copia `tests/licensing-policy.json` es administrada y tiene hash en
`platform-vendor.json`. No editarla. La extensión conserva licencia, alcance,
procedencia, terceros y textos íntegros; su REUSE.toml se distribuye junto a ella.
`LICENSES/SHARED-NOTICES.md` distribuye los avisos comunes desde Diseño.
Los textos SPDX normalizados se añaden únicamente para las licencias pertinentes
(MIT, elección académica y dependencias registradas; la plantilla incluye el código
legal académico predeterminado). Los originales upstream nunca se reemplazan.

`licensing.json` es local: grupos de originales autorizados, excepciones,
recursos propios externos y decisiones pendientes. Para grupos académicos se derivan
atribución y licencia de `course.yml`; no se duplica esa información en las reglas.
`original_rights_authorization` registra la autorización y su alcance original.
Las reglas de lecciones se limitan a los directorios homogéneos aprobados;
un nuevo directorio se declara una vez, nunca una modificación legal por lección.
Importaciones en vendor/, third_party/ o assets/vendor/ exigen inventario propio.

`legacy_review` contiene archivos preexistentes pendientes de metadatos REUSE,
con hash y motivo. No concede derechos ni permite modificar esos archivos sin
revisión de procedencia. Las licencias aprobadas siguen vigentes según LICENSING.
No se afirma cumplimiento REUSE completo de los cinco repositorios.

## REUSE y SPDX

Se usa REUSE 6.2.0 con especificación 3.3, TOML v1 y `precedence = closest`.
Referencias: https://reuse.software/spec/ y https://pypi.org/project/reuse/6.2.0/.
Las dependencias Python directas y transitivas se fijan en
`tooling/requirements-licensing.txt`; REUSE aporta parser y lint reales en vez de
inventar un comprobador SPDX. La versión se verificó instalándola y ejecutándola.
Los textos SPDX se obtuvieron con `reuse download`; CC BY-NC se reutilizó byte a
byte de los textos ya aprobados. No se añadieron encabezados a páginas existentes.

`python tests/licensing.py --reuse` ejecuta el lint real sobre un directorio temporal
que contiene los archivos con procedencia y metadatos acreditados y sus textos SPDX.
Los textos upstream originales con nombres históricos no son identificadores SPDX:
se conservan y comprueban por hash, sin renombrarlos ni atribuirles MIT propio.
La salida explica el alcance incremental. `reuse lint` sobre un repositorio entero
sigue mostrando deuda histórica; esa deuda no se oculta ni se presenta como aprobada.

`OR` expresa permisos alternativos explícitos; `AND`, obligaciones simultáneas.
La autorización MIT adicional sobre extracciones no impone CC BY-NC AND MIT a la
extensión. Un CSS compilado puede incorporar MIT propio AND obligaciones upstream;
no recibe una etiqueta simplificada como si todo fuera ngulloa. Los recursos de
terceros exclusivos mantienen su licencia. Procedencia desconocida bloquea el alta.
Una excepción de fragmento o permiso no expresable requiere registro humano; no
se deriva automáticamente una expresión jurídica.

## Crear una asignatura

Desde Diseño, instalar el entorno de validación una vez:

```sh
python3 -m venv /tmp/uso-legal-env
/tmp/uso-legal-env/bin/pip install -r tooling/requirements-licensing.txt
/tmp/uso-legal-env/bin/python tooling/create_course.py /tmp/curso-ejemplo \
  --author 'Titular verificado' --name 'Curso de ejemplo' \
  --authorize-original-content
```

La autorización es obligatoria y no se infiere del nombre. Predeterminado:
CC-BY-NC-4.0; `--license CC-BY-4.0` permite elección distinta con texto revisado.
Otros identificadores SPDX válidos requieren incorporar primero su código legal
revisado en Diseño. El generador rechaza destinos existentes y publica el directorio
local solo después de validar. No inicia Git ni llama servicios remotos.

Los ejemplos heredados y herramientas conservan MIT de ngulloa. Las nuevas páginas
originales en `lecciones/` usan la elección del nuevo titular. Los metadatos de
estado académico siguen pendientes; licencia no equivale a revisión. Registrar cada
página en el currículo y configuración de render sigue siendo necesario para las
validaciones académicas. El comando configura nombre, licencia y pie inicial; no
reescribe muestras académicas. Copia también workflows, validadores y manifiestos.

## Altas de material

- Lección original en un grupo aprobado: agregar QMD sin tocar LICENSE ni generar
  archivos por página. Si cambia el titular, declarar un grupo o excepción específico.
- Script original autorizado: declaración deliberada en cabecera del script Python/JS
  con `UStudyOpen-Original-Authorized`, `SPDX-FileCopyrightText` y
  `SPDX-License-Identifier` con valor `MIT`, o grupo explícito revisado en licensing.json.
  La ausencia de SPDX nunca se interpreta como prueba de originalidad.
- Biblioteca, imagen, fuente o fragmento externo: registrar en `third_party` sus
  `paths`, `origin`, `version` (o referencia verificable no versionada), `license`
  SPDX, `copyright`, `license_file`, `sha256` del texto, `notice_files` (lista explícita
  de ruta bajo LICENSES y hash por NOTICE, vacía si se verificó su ausencia) y `reviewed: true` solo
  después de revisión humana de derechos, modificaciones y posibles NOTICE.
  Conservar físicamente los avisos/NOTICE requeridos en LICENSES y/o junto al recurso.
  Si no se conocen condiciones, `reviewed: false` bloquea validación.

Los indicadores de procedencia son declaraciones del colaborador, no un detector
de plagio: la revisión humana debe contrastar origen y derechos. Importar contenido
ajeno en un directorio declarado original no le concede la licencia del directorio.
Copyright/SPDX contradictorios se detectan; no se sobreescriben mediante precedence.

## Sincronización y futuras propuestas

```sh
python3 tooling/sync_course.py ../precalculo --dry-run
python3 tooling/sync_course.py ../precalculo
python3 tooling/sync_course.py ../precalculo --check
python3 tooling/plan_licensing_update.py ../base-de-datos ../inteligencia-artificial \
  ../precalculo ../ustudyopen-template > /tmp/propuestas.json
```

La previsualización es de solo lectura. La aplicación informa los archivos antes
de escribir, comprueba hashes, rechaza archivos ajenos o vendor modificados y
promueve cambios con los respaldos/rollback existentes. Los archivos idénticos
no se reescriben; tampoco los manifiestos idénticos. Los archivos legales estándar
preexistentes solo se adoptan cuando sus bytes coinciden exactamente con la fuente.
Las excepciones locales nunca se reemplazan. No seguir enlaces simbólicos.
Un rollback incompleto conserva recovery.json y sus respaldos para inspección.

La propuesta JSON identifica consumidores afectados y presenta políticas anterior y
nueva, archivos, comandos de validación y revisión obligatoria. Es preparatoria:
no crea ramas, PR ni credenciales; no hace push, merge o auto-merge. Para una futura
actualización autorizada: revisar propuesta, aplicar en checkout aislado de cada
consumidor, ejecutar regresiones, revisar diffs y solicitar aprobación del PR por
repositorio. Un cambio técnico de versión puede requerir avisos aunque no cambie
el texto de la política. No activar actualizaciones legales directas en main.

## CI y artefactos

Se amplía validate.yml existente con instalación fijada y validación de SPDX/REUSE
antes del render aislado. Mantiene contents: read, checkout sin credenciales y
acciones fijadas por SHA. No hace arreglos en fuentes ni publica en PR. El validador
académico verifica además licencias e integridad; el post-render reutilizado genera
`_site/legal/`, manifiesto, política y registro local de recursos, y enlaces por HTML.
La comprobación posterior compara sus bytes con fuentes. Escribir artefactos de
compilación/evidencia no equivale a modificar archivos fuente en el PR.

Los avisos distinguen dependencias físicamente incorporadas por Quarto y MathJax
por CDN. No se atribuyen bytes remotos al artefacto; las URLs, versiones de referencia
y condiciones permanecen en los avisos upstream. No se certifica contenido futuro
de un CDN. Autoalojar recursos exige nueva revisión de bytes, fuentes y avisos.

## Mantenimiento

Editar política y componentes compartidos solo en Diseño; validar, previsualizar,
sincronizar y revisar manifiestos. Mantener excepciones en cada consumidor.
Ejecutar las 24 pruebas del actualizador, ocho de distribución y 16 de automatización,
lint incremental, build limpio, suites académicas, navegador y actionlint.
No regenerar hashes académicos para ocultar cambios ni modificar docs históricos.
Toda nueva licencia, titular o condición necesita autorización verificable.
