# Changelog

## 0.2.0 — 2026-10-25

- Corregida la especificidad frente a Quarto 1.10.18, opacidad e iconos de los cinco tipos nativos de callout; cabecera informativa azul pizarra en oscuro y tokens semánticos por intención.
- Desplegables con foco, rol, nombre visible y operación por Enter/Espacio conservando Bootstrap.
- Refuerzo discreto del azul y verde azulado en navegación, ejercicios, títulos académicos, fórmulas, resúmenes y acciones secundarias; identidad y contenido académico conservados.
- Separado el JS del laboratorio del include compartido; consultas por raíz y pruebas con múltiples instancias.
- Ampliadas exclusiones Git/Quarto, validación de HTML y repositorio, pruebas de contraste efectivo y capturas antes/después. Navegador aislado con sandbox habilitado y permisos Deno mínimos.
- Documentadas procedencia, propuesta MIT pendiente y distribución por versiones con PR y aprobación humana obligatoria. Sin releases, migraciones, commits ni despliegues.

## 0.1.0 — 2026-10-25

Primer prototipo de evaluación: extensión de formato HTML, marca clara/oscura, tokens, componentes académicos y galería de cinco páginas con controles y gráfico de muestra. Validado con Quarto 1.10.18. No migra las asignaturas existentes.


## 0.3.0 · instantánea local, 2026-10-25

- Se mantienen los colores, tipografía y correcciones de contraste aprobados.
- Presentación académica, chips, fichas de fórmulas y portadas compartidas, con alias compatibles.
- Estado textual desde metadatos y control explícito de revisión humana.
- MathJax 4.1.3 fijado; herramientas de compilación aislada e integridad de contenido/rutas.
- Distribución por manifiestos, plantilla y workflows SHA fijados, con publicación desactivada.
- Sin cambios de licencia, tags ni releases; ver procedencia y arquitectura.


### Continuación local de 0.3.0

- Corregido el actualizador para rechazar archivos ajenos y enlaces simbólicos en cualquier componente del destino, incluidos manifiestos y carpetas de plataforma.
- Preparación completa, detección de cambios concurrentes y restauración de archivos/manifiestos ante fallos de actualización; respaldos retenidos si la restauración falla.
- Reemplazo de `_site/` después de copiar completamente el sitio nuevo, con restauración del anterior ante fallos; docs permanece intacto.
- Validador con rutas acotadas y rechazo de fuentes enlazadas o actualizaciones incompletas. Pruebas de regresión mediante fixtures temporales, sin dependencias nuevas.
- Enlaces permanentes de títulos visibles al recibir foco y con nombre en español; se omite el área vacía redundante de navegación móvil en la secuencia de tabulación.
- Navegación anterior/siguiente adaptable al ampliar texto. Los cursos conservan sus propias regiones de gráficos desplazables y sus comprobaciones de teclado.
- Sin cambios de identidad, contenido académico, algoritmos, revisión declarada, licencias o activación de despliegues.
