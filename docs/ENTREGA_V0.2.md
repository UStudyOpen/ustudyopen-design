# UStudyOpen Design v0.2 — entrega local

**Iteración incremental completada sobre la identidad aprobada de v0.1.** Se mantiene Quarto 1.10.18 y el rango de compatibilidad declarado. La implementación, evidencias y documentación se limitan a `ustudyopen-design/`. No se hacen commits, push, releases, despliegues ni migraciones.

## Prototipo

Ejecutar desde la raíz del proyecto:

```sh
quarto render
quarto preview --host 127.0.0.1 --port 4848 --no-browser
```

Abrir <http://127.0.0.1:4848/>. La salida compilada local está en `_site/index.html`; usar HTTP para probar búsqueda y navegación. El laboratorio incluye sus propias interacciones y el resto de páginas recibe solo el JavaScript compartido.

La extensión declara **0.2.0**. Se conservan layout, tipografía, radios y los colores primarios de v0.1. La cabecera informativa oscura usa azul pizarra `#354b69`, título claro e icono azul legible. Los cinco tipos nativos conservan su semántica y comportamiento Bootstrap, añadiendo teclado donde Quarto 1.10.18 no daba foco al control. [Diagnóstico de especificidad y solución](CALLOUTS.md).

El refuerzo cromático se limita a títulos académicos, ejercicios, bordes de fichas/resúmenes, botones secundarios y navegación activa. No se cambian enunciados, soluciones ni modelos de muestra; solo se añaden ejemplares técnicos de los callouts al catálogo.

## Resumen de archivos

Esta comparación se refiere al **estado local v0.1 recibido**, no a `git diff HEAD`: al comenzar, Git solo registraba README y casi todo el prototipo ya era untracked. No se ha añadido nada al índice ni creado un commit.

| Archivo / grupo | Cambio de v0.2 |
|---|---|
| `_extensions/ustudyopen-design/scss/_callouts.scss` **nuevo** | Selectores específicos compatibles con Quarto, opacidad, contornos, máscaras de iconos y flecha semántica. |
| `_extensions/ustudyopen-design/brand/_brand.yml`, `_brand-dark.yml` | Roles para cabeceras, contorno y texto verde azulado; paleta base conservada. |
| `_extensions/ustudyopen-design/scss/uso.scss` | Publica los roles e importa callouts. |
| `_extensions/ustudyopen-design/scss/_base.scss` | Foco con suficiente especificidad, retirando su `!important`. |
| `_extensions/ustudyopen-design/scss/_layout.scss` | Acentos de navegación activa. |
| `_extensions/ustudyopen-design/scss/_components.scss` | Acentos académicos y botón secundario; elimina reglas de callout insuficientes. |
| `_extensions/ustudyopen-design/assets/after-body.html` | Solo mejoras compartidas; teclado de callouts e IDs propios del TOC móvil. |
| `gallery/laboratorio.html` **nuevo** | Extrae la lógica ilustrativa; campo por `name`, estado por raíz y limpieza de mensajes al editar. |
| `laboratorio.qmd` | Incluye únicamente en esta página el comportamiento demostrativo. |
| `componentes.qmd` | Muestras de los cinco tipos, estáticos y con ambos estados iniciales; contenido anterior conservado. |
| `_extensions/ustudyopen-design/_extension.yml`, `_quarto.yml`, `index.qmd`, `sistema.qmd` | Versión 0.2.0 / etiquetas v0.2; sin cambios curriculares. |
| `.gitignore`, `.quartoignore` | Excluyen artefactos, perfiles, cachés, configuración local, credenciales y archivos comprimidos. |
| `tests/browser.mjs`, `tests/check_site.py`, `tests/README.md` | Timeout, IDs/ARIA, aislamiento de scripts, publicación, estilos reales y documentación. |
| `tests/{cdp,callouts,instances,sandbox}.mjs` **nuevos** | Cliente y comprobaciones de integración específicas. |
| `tests/{make_fixtures,check_repository}.py`, `tests/run-browser.sh` **nuevos** | Instancias independientes, higiene y ejecución aislada con sandbox y permisos mínimos. |
| `_extensions/ustudyopen-design/PROVENANCE.md` **nuevo** | Nota de procedencia que acompaña la extensión, sin aplicar licencia nueva. |
| `README.md`, `CHANGELOG.md`, `docs/{ARQUITECTURA,COMPONENTES,TOKENS,PRUEBAS,REVISION_VISUAL}.md` | Contratos y resultados actualizados. |
| `docs/{CALLOUTS,COMPARACION_VISUAL,DISTRIBUCION,LICENCIAS,ENTREGA_V0.2}.md` **nuevos** | Entregables de diagnóstico, comparación, riesgos y propuestas. |
| `artifacts/v0.2/` **local, ignorado** | Logs, JSON, hashes de alcance y capturas reales antes/después. |

No se modifican `unidades/fundamentos.qmd` ni `assets/favicon.svg`. Los tres repositorios académicos se comprueban con estado Git y hashes de todos sus archivos versionados antes/después.

## Comparación visual

[Comparación antes/después en claro, oscuro y móvil](COMPARACION_VISUAL.md), con las imágenes incrustadas y enlaces a los cinco tipos y sus estados. Las capturas iniciales se tomaron antes de editar CSS. No son imágenes sintéticas ni aproximaciones reconstruidas.

La inspección visual se realizó sobre capturas de ambos temas y resoluciones móviles/de escritorio. **No equivale a una prueba manual completa de accesibilidad.**

## Resultados

<!-- V02:SUMMARY -->
- **Render:** 5/5 páginas con Quarto 1.10.18.
- **Integridad e higiene:** 0 errores; 278 referencias locales verificadas, 2 hojas de tema y 25 entradas de búsqueda. Se registran las excepciones de IDs generadas por Quarto.
- **Navegador:** 71 comprobaciones principales, 109 de callouts, 7 de múltiples instancias y 45 bajo prefijo: **232 aprobadas, 0 fallidas**. Sandbox adicional aprobado.
- **Resoluciones:** 320, 390, 768 y 1440 px; ambos temas. 60 casos de página/ancho/tema contando raíz y prefijo, además de la matriz específica de callouts.
- **Evidencia visual:** 104 capturas locales; 6 anteriores y 98 de v0.2.
- **Contraste de callouts:** los pares medidos superan los umbrales pertinentes. En el informativo oscuro, título **8.36:1**, icono **4.32:1**; no se usa `!important` para esos estilos.
- **Alcance:** los hashes de **261 archivos versionados** de las tres asignaturas son idénticos y sus estados Git siguen limpios.
<!-- /V02:SUMMARY -->

[PRUEBAS.md](PRUEBAS.md) incluye comandos reproducibles, cobertura, excepciones nativas de Quarto y límites. Los únicos `!important` propios conservados son los tres de la preferencia de movimiento reducido: deben prevalecer sobre transiciones/animaciones de Bootstrap y estilos de autor para respetar esa preferencia. No se añaden en la corrección de callouts.

## Riesgos pendientes

| Riesgo | Tratamiento / pendiente |
|---|---|
| Derechos de los estilos de origen | BD e IA declaran CC BY-NC 4.0; Precálculo no tiene LICENSE localizado. MIT se propone solo para código propio/autorizado. Falta trazabilidad granular y autorización de titulares antes de publicar. Ninguna licencia existente cambia. |
| JavaScript remoto de Quarto | MathJax por jsDelivr y polyfill ES6 por cdnjs, sin fijación completa ni SRI. No se garantiza matemática sin red. Evaluar distribución local, versiones exactas y CSP con las subdependencias en una iteración separada. |
| Acoplamiento al generador | Las formas de iconos usan `$callouts`, mapa interno de Quarto; el DOM también depende de 1.10.18. Mantener versión fijada y volver a validar antes de actualizar. |
| HTML nativo con IDs repetidos | Se registran las excepciones exactas de hojas y TOC emitidas por Quarto. El índice móvil se corrige al ejecutar JS; el HTML sin JS conserva duplicados nativos del TOC. No se promete validación HTML estricta completa. |
| Accesibilidad sin evaluación humana completa | Pendientes lector de pantalla, recorrido completo, zoom real, contraste forzado, dispositivos táctiles y otros motores. Los ratios aprobados cubren las parejas medidas; no todo el sitio ni estilos arbitrarios. |
| Controles sin JavaScript / entorno sin red | Tienen respaldo textual/estático, pero esos escenarios no se probaron en esta iteración. No se presenta conformidad completa de mejora progresiva. |
| Automatización futura | Aún no hay release ni reglas verificadas de protección de ramas. La obligatoriedad de aprobación humana debe configurarse y comprobarse antes de habilitar un actualizador. |
| Evidencia y secretos | Todo `artifacts/` queda fuera de Git/render; no subir perfiles. El escaneo ejecutado detecta patrones comunes, no certifica ausencia de cualquier secreto. |

## Propuesta técnica de distribución

[DISTRIBUCION.md](DISTRIBUCION.md) propone un origen central, tags inmutables y archivo de release limitado a la extensión, con manifiesto y hashes. Cada curso guarda una copia fijada y recibe su propia PR de actualización con diff, pruebas y capturas. La rama principal exige revisión humana y checks; el bot no aprueba ni fusiona. Se contempla un piloto autorizado, despliegue gradual y rollback por reversión de la PR.

[LICENCIAS.md](LICENCIAS.md) propone MIT condicionada a resolver la procedencia y autorización; no se aplica automáticamente a material CC BY-NC ni a fuentes sin licencia.

**La iteración termina aquí.** No se inicia la migración de ninguna asignatura ni una actualización masiva sin aprobación posterior.
