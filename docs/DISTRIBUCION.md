# Distribución centralizada propuesta

Esta es una propuesta técnica. No se han creado releases, workflows, PR, commits, accesos a otros repositorios ni actualizaciones de asignaturas. La primera publicación queda pendiente de la revisión de procedencia y licencia descrita en [LICENCIAS.md](LICENCIAS.md).

## Un origen, copias locales versionadas

Mantener `UStudyOpen/ustudyopen-design` como origen de la extensión y su galería. Publicar versiones semánticas explícitas: `0.2.0` para esta iteración; parches para correcciones compatibles y versiones menores para cambios de contrato mientras la API siga en 0.x. No actualizar Quarto y el diseño en la misma PR. Mantener Quarto **1.10.18**; el rango declarado continúa `>=1.10.18 <1.11.0`, sin afirmar que se probaron todas esas versiones.

Cada release aprobada tendrá:

- Tag `vX.Y.Z` asociado a un commit concreto; registrar ambos. No mover tags publicados.
- Changelog, contrato de tokens, requisitos de Quarto y notas de compatibilidad.
- Archivo `ustudyopen-design-vX.Y.Z.tar.gz` con una raíz `_extensions/ustudyopen-design/`. Construirlo desde una lista permitida de archivos del commit, nunca archivando el workspace completo.
- Solo `_extension.yml`, `brand/`, `scss/`, `assets/`, licencia aprobada y procedencia. Excluir galería, pruebas, informes, `_site`, cachés, perfiles, credenciales y `.git`.
- Manifiesto SHA-256 de todos los archivos instalables, suma del archivo y resultados CI. Proteger la release contra reemplazo; el checksum publicado junto al archivo comprueba integridad, pero por sí solo no acredita autenticidad. Verificar además el origen y el commit aprobado.

Quarto admite repositorios GitHub, tags y archivos de extensión: [distribución oficial](https://quarto.org/docs/extensions/distributing.html). Para mantener la ruta sin namespace que usa este prototipo, se propone el **archivo de release** como vía uniforme. Comando ilustrativo, **no ejecutable aún porque esa release no está publicada**:

```sh
quarto add https://github.com/UStudyOpen/ustudyopen-design/releases/download/v0.2.0/ustudyopen-design-v0.2.0.tar.gz
```

Descargar primero el archivo, verificar su hash contra el manifiesto de una release aprobada e instalar desde el archivo local es preferible en el actualizador. `quarto add UStudyOpen/ustudyopen-design@v0.2.0` es otra vía, pero la instalación GitHub puede introducir un namespace organizacional; habría que validar las rutas resultantes de marca y formato antes de usarla. No alternar ambas convenciones entre asignaturas.

## Contrato de incorporación por curso

Versionar la copia instalada de `_extensions/ustudyopen-design/` en cada repositorio. No cargar CSS ni JS del diseño desde una URL móvil en tiempo de ejecución. El sitio continúa funcionando con su versión hasta que una persona apruebe una PR.

```yaml
# Fragmento de referencia; no se ha aplicado a ninguna asignatura.
brand:
  light: _extensions/ustudyopen-design/brand/_brand.yml
  dark: _extensions/ustudyopen-design/brand/_brand-dark.yml
format:
  ustudyopen-design-html: default
```

La navegación, el currículo, los formularios, gráficos, simuladores y recursos específicos permanecen en el curso. No copiar `gallery/laboratorio.html` a la extensión ni sobrescribir `_quarto.yml` completo. En la primera incorporación, resolver conflictos de estilos con una PR específica de migración; esto requiere autorización posterior.

Guardar un pequeño manifiesto de dependencia del curso con `version`, `source_tag`, `source_commit`, `archive_sha256`, `quarto` y hashes de archivos instalados. Quarto copia extensiones al repositorio; no ofrece por sí solo un lockfile que cubra este contrato. Detectar modificaciones locales antes de actualizar. Si hay divergencias, abrir una incidencia/PR para revisión; no sobrescribirlas silenciosamente.

## PR de actualización con aprobación humana obligatoria

Después de la aprobación de esta estrategia, elegir un piloto autorizado. Cada asignatura tendrá un workflow **optativo** que se ejecute manualmente o por calendario y consulte solo releases aprobadas, con una lista explícita de repositorios participantes. La publicación central no debe escribir directamente en todas las ramas principales.

Flujo propuesto por repositorio:

1. Consultar una release estable permitida y el manifiesto; comprobar versión, tag/commit, hashes, compatibilidad y condiciones de licencia. No seguir `main` ni instalar `latest` sin fijar versión.
2. Crear una rama `chore/design-vX.Y.Z`. Rechazar rutas fuera de `_extensions/ustudyopen-design/` y del manifiesto de dependencia; revisar symlinks, rutas `..` y rutas absolutas antes de extraer archivos.
3. Actualizar únicamente la copia compartida y el manifiesto. Generar un diff legible, notas de cambio y comparativas clara/oscura para el curso. No tocar texto académico ni configuración de publicación.
4. Ejecutar render con Quarto fijado, validación de enlaces/recursos y pruebas de interacción del curso, además de móvil/escritorio, callouts y temas. Publicar evidencias de CI con retención limitada y sin perfiles/CDP ni secretos.
5. Abrir o actualizar **una PR por curso y versión**; deduplicar ejecuciones. Incluir versión anterior/nueva, commit y hashes, diff de archivos, resultados, capturas, riesgos y pasos de rollback. Solicitar revisión a responsables humanos del curso y del diseño.
6. La persona revisora decide cuándo fusionar. **No habilitar auto-merge, no aprobar mediante bots y no fusionar por el solo hecho de pasar CI.**

Proteger la rama principal con PR obligatoria, al menos una aprobación de responsable humano, CODEOWNERS apropiado, invalidación de aprobaciones al cambiar el diff, checks obligatorios y restricción de bypass incluso para administradores. CODEOWNERS no sustituye la regla de aprobación. Es una configuración que deberá aplicarse y comprobarse en GitHub, no una garantía proporcionada por este documento. Consultar [protección de ramas](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches).

El workflow de cada curso debe tener permisos mínimos: lectura para detectar versiones; `contents: write` y `pull-requests: write` únicamente en el job que crea su rama/PR. Preferir el token del propio repositorio; si se opta por una GitHub App central, limitar su instalación a los repositorios autorizados y evitar PAT personales amplios. Fijar acciones externas por SHA, no ejecutar código de PR no confiable con secretos y no usar `pull_request_target` para compilar cambios externos. Revisar cómo se dispararán los checks de las PR creadas con `GITHUB_TOKEN`, que tiene restricciones de encadenamiento de workflows; si fuera necesario, usar una App con permisos acotados o ejecutar los checks de manera explícita. No conceder capacidad de aprobación al actualizador.

## Despliegue gradual y reversión

Validar primero la galería, después el curso piloto autorizado y finalmente incorporar cursos de uno en uno. Mantener un registro por asignatura de versión instalada, PR, aprobación y resultado. Detener la expansión ante regresiones. Revertir la PR de dependencia para recuperar la copia anterior; no cambiar contenido académico ni forzar la nueva versión en todos los cursos.

**Estado de esta entrega:** extensión local v0.2.0 preparada; estrategia documentada. No hay piloto, migración, release pública ni actualizador implementado.
