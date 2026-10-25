# Decisión: extensión de formato HTML

Se conserva `ustudyopen-design-html`, derivado de HTML, sobre un proyecto `website`. Quarto 1.10.18 renderiza la marca declarativa clara/oscura, Bootstrap 5, SCSS común y navegación del proyecto en una sola configuración. La prueba incluye cinco páginas y una página anidada. La evidencia se registra en [PRUEBAS.md](PRUEBAS.md) y `artifacts/`.

La [documentación de formatos de Quarto](https://quarto.org/docs/extensions/formats.html) permite agrupar opciones y estilos. La [marca declarativa](https://quarto.org/docs/authoring/brand.html) permite dos archivos de marca y acceso a sus colores desde SCSS. Se utiliza una única entrada SCSS `[default, brand, scss/uso.scss]` en ambas ramas del tema. Quarto compila dos hojas y activa la apropiada.

## Responsabilidades

- **Marca:** dos archivos, una identidad, sin fuentes remotas. Colores de la sección 7 de la auditoría.
- **Extensión:** apariencia, tokens, opciones comunes y mejoras progresivas.
- **Proyecto website:** curso, enlaces, orden, buscador, sidebar, TOC y pie. Permanece fuera de la extensión para no imponer un currículo.
- **Galería:** contenido nuevo de muestra y una interacción mínima sin modelos ni simuladores copiados.

No se necesitó la alternativa de extensión de marca con SCSS por separado. Introducirla ahora exigiría configurar más piezas por proyecto sin resolver una incompatibilidad real.

## Hallazgos de la prueba

1. Los valores `$brand-uso-*` están disponibles en la sección `scss:rules`. Referenciarlos desde los defaults del SCSS de mayor prioridad produjo `Undefined variable` por el orden de capas de Quarto. Se resolvió manteniendo el mapeo Bootstrap nativo de la marca y emitiendo los tokens en reglas; no se duplicaron mapas de color.
2. Los includes mantienen JavaScript incorporado, sin rutas de recursos que reconstruir. Desde v0.2 hay dos responsabilidades: `assets/after-body.html` aporta únicamente mejoras compartidas y `gallery/laboratorio.html` se incluye solo en el front matter del laboratorio. Quarto combina ambos includes; se valida que el código demostrativo esté ausente en las otras cuatro páginas.
3. `theme.light` y `theme.dark` generan las clases y hojas nativas de Quarto. El SVG utiliza propiedades CSS, por lo que no necesita escuchar cambios de tema ni volver a montarse.
4. El selector nativo se mantiene en las herramientas de la cabecera. Solo se añade su nombre en español y activación por Espacio/Enter sobre el control existente. Su acción, preferencia del sistema y persistencia siguen siendo de Quarto.
5. Las fórmulas usan MathJax incluido por el generador mediante CDN. No se descarga ni versiona una copia en esta fase. La dependencia de red queda explícita.

## Configuración mínima de utilización

Receta de referencia para un proyecto de prueba que ya tenga una copia local de `_extensions/ustudyopen-design/`; no es una instrucción de migración autorizada:

```yaml
project:
  type: website
brand:
  light: _extensions/ustudyopen-design/brand/_brand.yml
  dark: _extensions/ustudyopen-design/brand/_brand-dark.yml
format:
  ustudyopen-design-html: default
website:
  title: UStudyOpen
  navbar:
    left:
      - href: index.qmd
        text: Inicio
```

La extensión no instala paquetes ni modifica GitHub Pages. Su rango declarado es `>=1.10.18 <1.11.0`; el único entorno verificado es 1.10.18. Mantener esa versión para evaluar esta entrega. La versión del sistema es 0.2.0; su API aún puede cambiar con la revisión visual.

## Límites deliberados

No hay filtro Lua, catálogo automático, sincronización de preferencias entre dominios, modelos compartidos, adaptadores para cursos existentes, actualizador de repositorios ni flujo de publicación. Las definiciones y teoremas usan encabezados explícitos; no se promete numeración ni referencias automáticas. La geometría del SVG es una demostración de presentación, no una extracción académica.

## Navegación en móvil

Quarto oculta el índice lateral en pantallas estrechas. Se configura su opción nativa `toc-location: right-body`, que genera también un índice en el cuerpo. Una mejora progresiva mueve ese índice generado a un `details` nativo «En esta página» y oculta esta variante desde 992 px; no mantiene enlaces de secciones escritos a mano. Sin JavaScript, el índice generado permanece en el cuerpo en móvil.

La [opción right-body](https://quarto.org/docs/output-formats/html-basics.html#table-of-contents) proporciona la fuente del índice. El SCSS ajusta únicamente el espacio horizontal y orden de las herramientas de la navbar para que buscador y tema permanezcan en una fila a 320 px, con el tema en el extremo derecho. No se cambia la grilla interna de Quarto. Los controles de colapso de tipo enlace sin `href` reciben activación por teclado sobre la misma acción Bootstrap existente.

## Separación del JavaScript en v0.2

La extensión conserva salto al contenido, TOC móvil, nombres de controles, activación por teclado de los controles nativos y acceso al scroll de código. Los IDs `quarto-document-content`, `TOC-body` y `quarto-search` son contratos nativos de integración de página, no identificadores de componentes repetibles. El índice móvil recibe IDs propios en sus enlaces para evitar duplicar los del TOC lateral; sus `href` siguen apuntando a las secciones originales.

El laboratorio conserva sus modelos y resultados de muestra, ahora fuera de la extensión. Gráficos y formularios buscan controles dentro de cada raíz `data-uso-demo` / `data-uso-form`; el campo se selecciona por `name="answer"`, sin `#uso-answer` en el comportamiento. Los IDs HTML solo relacionan etiquetas, ayuda, títulos y descripciones: deben ser únicos por instancia. La fixture de prueba duplica ambos componentes con IDs nuevos y verifica su independencia ejecutando el mismo include del laboratorio, sin duplicar algoritmos en el test.

El tema continúa siendo responsabilidad de Quarto. Ningún script del sistema compartido conoce respuestas académicas, geometría del gráfico, formularios de evaluación ni persistencia de apuntes.
