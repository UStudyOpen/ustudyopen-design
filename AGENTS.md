# UStudyOpen Design

Fuente autorizada de presentación y herramientas comunes. Preservar la identidad 0.2 y la procedencia; no relicenciar sin autorización. No incluir algoritmos académicos de los cursos. El selector de tema y su persistencia pertenecen a Quarto; cambiar tema no reinicializa actividades.

Editar únicamente aquí los archivos compartidos, distribuir mediante `python3 tooling/sync_course.py ../curso` y revisar manifiestos, diferencias y regresiones antes de integrar. No editar las copias vendor. Los tests académicos permanecen en cada curso. Fijar acciones por SHA, comprobar sus dependencias transitivas y conservar publicación desactivada. `docs/` en este repositorio contiene documentos fuente: no borrarlo ni confundirlo con artefactos de cursos. No crear commits, tags, releases, PR, push ni despliegues sin autorización.

Validar la galería con `quarto render`, `python3 tests/check_site.py` y `python3 tests/check_repository.py`. Para cambios compartidos ejecutar también compilación aislada, suites de los cursos, comparación móvil y ambos temas. Los resultados históricos documentados no acreditan una ejecución actual.

Validar modificaciones de herramientas con `python3 tests/test_tooling.py` antes de sincronizar. No sobrescribir archivos ajenos a los manifiestos ni seguir enlaces simbólicos en destinos. No borrar carpetas de recuperación de una actualización incompleta sin examinar sus respaldos.
