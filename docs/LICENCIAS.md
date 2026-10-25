# Propuesta de licencia para el código compartido

Se propone **MIT** para el código propio y autorizado de `ustudyopen-design`, por su sencillez y facilidad de reutilización entre cursos. MIT exige conservar sus avisos de licencia y copyright; permite uso comercial y distribución de modificaciones. Fuente: [texto y condiciones de MIT](https://choosealicense.com/licenses/mit/).

**No se ha añadido un LICENSE ni se ha relicenciado ningún archivo.** La aprobación de la identidad visual no equivale a autorización para cambiar condiciones de reutilización.

## Procedencia comprobada localmente

| Origen | Evidencia leída | Condición / pendiente |
|---|---|---|
| Bases de Datos | `../base-de-datos/LICENSE`, `styles/{base,layout,components}.css` | CC BY-NC 4.0; reconocer fuente, conservar restricciones y declarar cambios para material derivado. |
| Inteligencia Artificial | `../inteligencia-artificial/LICENSE`, familia `styles/` | CC BY-NC 4.0; mismas condiciones declaradas. |
| Precálculo | `../precalculo/styles/custom.css`, inventario de archivos | Sin LICENSE localizado; determinar autoría y permiso antes de redistribuir material derivado. |
| Prototipo v0.1 | Fuentes locales previas a esta iteración y auditoría de UStudyOpen | La mayoría de fuentes todavía no están registradas en Git; falta atribución granular e historial verificable. |
| Quarto / Bootstrap e iconos | Recursos de Quarto 1.10.18 instalados | Conservar avisos de terceros; no incluir `_site/site_libs` como código propio de la extensión. |

La semejanza y la relación con la auditoría no bastan para certificar que toda la implementación sea independiente de los estilos anteriores. La nueva [nota de procedencia instalada con la extensión](../_extensions/ustudyopen-design/PROVENANCE.md) registra fuentes y cambios, pero no declara despejados todos los derechos.

## Antes de una primera publicación

1. Inventariar por archivo los fragmentos copiados/adaptados, titular, versión de origen y permiso. Completar la atribución nominal cuando se identifique al titular; el nombre de la organización por sí solo puede ser insuficiente.
2. Solicitar a los titulares autorización expresa para ofrecer bajo MIT los derivados que se quieran incluir. Alternativa: excluirlos o mantenerlos separados con sus condiciones y avisos originales. No se puede convertir todo el conjunto en MIT por añadir un archivo nuevo.
3. Resolver la procedencia de Precálculo. Mantener el contenido académico y sus licencias fuera del alcance de la licencia del código compartido.
4. Con aprobación, añadir el texto de licencia y avisos **dentro de `_extensions/ustudyopen-design/`**, pues Quarto no instala los archivos superiores a `_extensions/`. Añadir también una referencia en la raíz del repositorio y verificar el paquete final.

Creative Commons [desaconseja sus licencias para software](https://creativecommons.org/faq/#can-i-apply-a-creative-commons-license-to-software). Esto respalda la propuesta futura de una licencia de software, pero no elimina los términos ya aplicados. Las obligaciones de material derivado se consultan en [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).
