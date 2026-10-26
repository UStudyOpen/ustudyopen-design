# Publicación autorizada al integrar un PR

La decisión humana de publicar se realiza al revisar e integrar el PR en `main`.
En los cursos migrados y autorizados, ese merge dispara `deploy.yml` sin otra
confirmación ni aprobación del entorno. No se publica desde PR ni otras ramas.
`validate.yml` sigue siendo el check obligatorio del PR y no dispone de permisos
de publicación. Con un único administrador, la integración manual es la decisión
de aprobación: se exige PR y checks, pero cero aprobaciones de una segunda cuenta.
No hay bypass de administradores, force push ni eliminación de main.

## Controles y sincronización

- `USO_PAGES_ENABLED=true` es el interruptor remoto; no basta para habilitar push.
- `course.pages_automation_approved: true` debe ser un booleano y requiere haber
  verificado antes la migración y publicación real mediante Actions.
- `tooling/sync_course.py` añade `push: branches: [main]` exclusivamente para esos
  cursos. Los demás y la plantilla conservan únicamente `workflow_dispatch`.
- `tests/pages_authorization.py` vuelve a comprobar evento, rama, interruptor y
  metadatos antes de compilar. Un manual exige exactamente `PUBLICAR`.
- El checkout usa `github.sha` y comprueba HEAD. Repite licencias, integridad,
  compilación Quarto 1.10.18 aislada, regresiones académicas y validación de salida.
- Solo se archiva `_site/` validado, con licencias y avisos. `deploy` depende del
  éxito completo de `build` y consume el artefacto de esa misma ejecución.
- Solo `deploy` recibe `pages: write` e `id-token: write`; los demás permisos son
  de lectura. Las credenciales del checkout no persisten. No se escriben commits.
- `github-pages` admite exclusivamente la rama main, sin revisores obligatorios
  ni bypass administrativo. Se preservan las demás restricciones.
- Concurrency `github-pages`, sin cancelar la ejecución activa, impide desplegar
  simultáneamente. GitHub puede sustituir ejecuciones pendientes; no garantiza
  FIFO. Antes de publicar se rechaza un SHA que ya no sea HEAD remoto de main.
  Un merge posterior durante un despliegue activo se publicará en su ejecución.
- No se toca `docs/`, no se crea `gh-pages` y no hay `pull_request_target`.

Sincronizar con `python3 tooling/sync_course.py /ruta/curso` y comprobar con
`--check`. El manifiesto contiene el hash del workflow efectivo para cada curso,
no el de la plantilla antes de aplicar su autorización. Nunca editar vendor.
Integrar primero el PR central y después los PR de los cursos. La plantilla
no se habilita y las nuevas asignaturas no heredan autorización automática.

## Verificación y reversión

`python3 tests/test_pages_automation.py` comprueba 432 combinaciones de eventos,
ramas, interruptor y confirmación, además de sincronización, hashes e idempotencia.
Ejecutar también `tests/test_tooling.py`, actionlint, licencias, compilaciones y
suites de cada curso. Las simulaciones no acreditan un despliegue real.

Para detener publicaciones futuras: `gh variable set USO_PAGES_ENABLED --body false
-R UStudyOpen/curso` (en una sola línea); cancelar además ejecuciones ya iniciadas
si se necesita detenerlas inmediatamente. La versión servida permanece publicada.
Para volver al modo manual, cambiar el metadato a false, sincronizar desde el
central y presentar un PR; su merge retira el trigger push. Restablecer revisores
del entorno es opcional si se quiere recuperar la segunda aprobación. Para
revertir una versión del sitio, revertir su cambio mediante PR y merge: se genera
un artefacto nuevo de ese commit. No hacer push directo a main.
