# Validación de v0.2

Evaluación local del **25 de octubre de 2026**, America/Santiago. Se conserva Quarto **1.10.18**, Bootstrap **5.3.1**, Brave **155.1.97.59** / Chromium **155.0.8059.85**, Deno **2.7.14** y Python **3.14.8**. No se instalaron paquetes, herramientas de auditoría ni frameworks.

El navegador conectado de la aplicación no estuvo disponible. Se utilizó Brave headless aislado, mediante CDP y los scripts del repositorio. Las comprobaciones de teclado usan eventos reales del protocolo; la revisión visual consiste en inspeccionar las capturas indicadas, no en un recorrido manual completo de la UI.

## Resultados finales

<!-- V02:RESULTS -->
| Validación | Resultado | Evidencia local |
|---|---|---|
| Compilación Quarto 1.10.18 | **5/5 páginas** | [render.log](../artifacts/v0.2/render.log) |
| Integridad estática | **5 páginas, 278 referencias locales, 2 hojas, 25 entradas de búsqueda; 0 errores**; excepciones nativas registradas | [static-results.json](../artifacts/v0.2/static-results.json) |
| Navegador principal | **71 aprobadas, 0 fallidas**; 40 casos, 49 capturas | [browser-results.json](../artifacts/v0.2/browser-results.json) |
| Callouts nativos | **109 aprobadas, 0 fallidas**; 15 ejemplares × 3 anchos × 2 temas, 26 capturas | [callouts-after.json](../artifacts/v0.2/callouts-after.json) |
| Múltiples instancias | **7 aprobadas, 0 fallidas** | [instances-results.json](../artifacts/v0.2/instances-results.json) |
| Prefijo local de publicación | **45 aprobadas, 0 fallidas**; 20 casos, 23 capturas | [subpath-results.json](../artifacts/v0.2/subpath-results.json) |
| Sandbox real del navegador | **Namespace, PID/red y Seccomp-BPF activos** | [sandbox-results.json](../artifacts/v0.2/sandbox-results.json) |
| Higiene de repositorio | **0 errores**; permisos, exclusiones y patrones de secretos revisados | [hygiene-results.json](../artifacts/v0.2/hygiene-results.json) |
| Alcance | **261 archivos versionados idénticos**, tres repositorios limpios | [scope-results.json](../artifacts/v0.2/scope-results.json) |

**232 comprobaciones funcionales aprobadas, 0 fallidas**, más la verificación de sandbox. **104 capturas:** 49 de la matriz principal, 23 bajo prefijo, 26 específicas de callouts y 6 de la referencia anterior. Las 90 observaciones de callouts cubren 15 ejemplares × 3 anchos × 2 temas; no se confunden con 90 comprobaciones independientes.

| Callouts: mínimo observado | Texto/título/enlace (≥4.5) | Icono/flecha (≥3) | Bordes/franja (≥3) |
|---|---|---|---|
| Claro | 6.70:1 | 4.40:1 | 3.17:1 |
| Oscuro | 8.36:1 | 4.32:1 | 3.50:1 |

Los números de la tabla se muestran redondeados; las aserciones utilizan los valores completos. La cabecera informativa oscura alcanza **8.36:1** para el título y **4.32:1** para el icono. Los ratios de todos los tipos y estados están en el JSON.
<!-- /V02:RESULTS -->

La matriz principal contiene **5 páginas × 4 anchos (320, 390, 768 y 1440 CSS px) × 2 temas = 40 casos**. Bajo el prefijo local `/ustudyopen-design/` se repiten las 5 páginas a 390 y 1440 px en ambos temas: **20 casos**. El viewport tiene 1000 CSS px de alto y escala de dispositivo 1; no son pruebas en un teléfono físico ni zoom real.

## Cobertura ejecutada

- Preferencia oscura del sistema, tema explícito persistido al navegar/recargar y conservación de valores, apuntes, nodo y geometría SVG al cambiar de tema.
- Salto al contenido, foco visible, Espacio/Enter del selector y desplegables, rango con flechas y solución nativa con Enter. Movimiento reducido emulado.
- Búsqueda con resultados desde la página anidada; sidebar, TOC, navegación anterior/siguiente y menús móviles abiertos. En cada caso: reflujo sin scroll global, CSS cargado, selector visible y tamaño de 44 px, ausencia de IDs duplicados en el **cuerpo tras la mejora progresiva**.
- Formulario ilustrativo con respuesta incorrecta/correcta, foco en el error y reset del gráfico. Dos gráficos y dos formularios en una fixture desechable, usando exactamente el include de la galería y asociaciones de IDs distintas: independencia de controles, mensajes, foco y reset; validación obligatoria y borrado de mensajes obsoletos al editar.
- **15 callouts nativos:** note, tip, important, caution y warning, cada uno estático, cerrado y abierto al inicio. Ratios de estilos calculados (texto, fondo, borde e iconos/flechas pseudo-elemento), teclado y puntero en ambos temas a 320, 390 y 1440 px. Capturas de cada tipo y sus estados a 390/1440, además de la comparación del aviso original.
- Integridad estática: rutas y fragmentos, referencias ARIA/etiquetas, ambas hojas, índice de búsqueda, ausencia de recursos de pruebas/credenciales en la salida y aislamiento del código demostrativo en la página del laboratorio.
- Higiene de fuentes: probes de `.gitignore`, permisos y symlinks de la extensión, diff sin errores de espacios y búsqueda limitada de patrones de credenciales de alta confianza. No equivale a una auditoría exhaustiva de secretos.
- Ausencia de excepciones JS no capturadas y fallos de red observados durante las visitas finales. La prueba de sandbox consulta la página interna del navegador y guarda su estado.

La primera ejecución de la fixture de múltiples instancias encontró un favicon ausente y una aserción que interpretaba como contenido el salto de línea de un mensaje vacío generado por Quarto. Se corrigió la **fixture/prueba** (favicon de datos y `.trim()`); el foco y aislamiento del código de producto funcionaban. Los resultados finales sustituyen esos intentos, sin declararlos aprobados.

## Contraste y excepciones explícitas

Los callouts se validan con texto/enlaces ≥4.5:1, iconos/flecha/franja/contornos ≥3:1 contra los fondos adyacentes pertinentes, sin redondear para decidir si pasan. Se exige opacidad 1 y una máscara visible para los iconos. [CALLOUTS.md](CALLOUTS.md) detalla los criterios y las reglas originales de Quarto.

La matriz general de tokens conserva la excepción v0.1: `emphasis` claro sobre `surface-alt` ronda 4.41:1 y se admite **solo como trazo gráfico**, nunca como texto normal. Para los nuevos títulos/acciones verdes se usa `emphasis-ink`; también se prueban sus fondos suaves. El cálculo de tokens no acredita todos los colores de sintaxis ni todas las combinaciones que pueda crear un autor.

Quarto 1.10.18 genera IDs repetidos en las hojas de ambos temas y en los dos TOC de `right-body`. La comprobación estática registra **esas excepciones precisas** en `native_quarto_duplicate_ids`, sin silenciar duplicados de contenido o componentes. La extensión cambia los IDs del índice móvil y elimina su referencia ARIA al título retirado. En ejecución no quedan duplicados en el cuerpo; las repeticiones nativas del `head` se conservan porque el gestor de tema las consulta mediante clases e IDs. El HTML original sin JS mantiene los duplicados nativos del TOC; no se declara validación HTML estricta perfecta.

## Reproducir

Desde `ustudyopen-design/`, sin renders concurrentes:

```sh
quarto --version  # 1.10.18
quarto render
python3 tests/check_site.py
python3 tests/check_repository.py
bash tests/run-browser.sh
```

El último comando inicia dos servidores **solo en 127.0.0.1**, un navegador con un perfil `mktemp` de permisos privados dentro de `artifacts/v0.2/` y CDP solo en loopback. Puertos: 4850 (sitio), 4851 (prefijo/fixture) y 9228 (CDP). Si están ocupados, falla antes de conectarse; no reutiliza un navegador personal. Al terminar, detiene los procesos que creó y elimina ese perfil.

Usa Deno con `--no-config --no-lock`, `--allow-net` limitado a los puertos requeridos y `--allow-write=artifacts/v0.2`. No se concede `--allow-all`, lectura de perfiles personales, ejecución de subprocesos ni acceso a variables de entorno desde las pruebas. Estos permisos limitan el proceso Deno; el navegador puede descargar los recursos CDN de la página.

Opciones de la instalación local:

```sh
USO_BROWSER_BIN=/ruta/a/chromium USO_DENO_BIN=/ruta/a/deno bash tests/run-browser.sh
# Tras cambios en una prueba concreta:
bash tests/run-browser.sh callouts  # browser, instances, subpath o sandbox
```

La captura `before` se obtuvo antes de modificar los estilos, sobre el render v0.1. No se debe regenerar con la extensión actual. Para repetirla hay que recuperar aquella revisión en una copia aislada; los archivos originales de esta sesión no se comprometieron a Git. El script admite `tests/callouts.mjs BASE before CDP` para esa copia, con los mismos permisos limitados.

## Sandbox y permisos

`tests/run-browser.sh` **no contiene `--no-sandbox`** y no aplica cambios de permisos a binarios del sistema. En este equipo existe un helper `chrome-sandbox` instalado por el administrador y el sistema permite namespaces; la página interna informa los mecanismos realmente activos en `sandbox-results.json`.

La receta v0.1 desactivaba el sandbox por defecto. Esa práctica se retira. En CI conviene un runner no privilegiado, con los mecanismos de aislamiento del Chromium empaquetado configurados por su administrador, y directorios de trabajo/artefactos aislados. No ejecutar el navegador como root, no añadir `--privileged` ni cambiar a ciegas el bit setuid de un archivo descargado. Si el host impide arrancar con sandbox, la prueba queda **sin ejecutar** hasta proporcionar un entorno compatible; el script no recurre automáticamente a `--no-sandbox`. Su uso excepcional solo tendría sentido en un entorno desechable y aislado con aprobación consciente del operador; no forma parte de esta validación.

Los fuentes y scripts se mantienen sin permisos ejecutables innecesarios: `bash tests/run-browser.sh` no requiere `chmod +x`. Todos los archivos de evidencia y perfiles se excluyen de Git y de Quarto. No publicar el directorio `artifacts/` completo; seleccionar solo informes/capturas revisados si se requiere una PR remota.

## Límites pendientes

No se declara conformidad WCAG 2.2 AA del sitio completo. **No realizados:** recorrido manual completo Tab/Shift+Tab, zoom real 200%/400%, lector de pantalla, anuncios dinámicos y matemática accesible, contraste forzado, almacenamiento bloqueado, Safari, Firefox, dispositivos táctiles reales, impresión, JavaScript desactivado y fallo de red. La emulación a 320 px no sustituye el zoom real. No se ejecutó axe.

La revisión visual de capturas no garantiza legibilidad perceptual en todas las pantallas ni comportamiento de tecnologías de asistencia. Los modos de callout `simple`, sin icono y combinaciones arbitrarias de estilos de un curso no tienen una matriz específica en esta iteración. Las licencias y la publicación/migración de asignaturas requieren decisiones posteriores.
