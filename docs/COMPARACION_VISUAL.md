# Comparación visual v0.1 → v0.2

Las capturas `before` se tomaron sobre el render inicial, **antes de editar la extensión**. Las `after` muestran v0.2. Misma página (`componentes.html`), viewport de 1440 × 1000, escala 1 y desplazamiento centrado en el aviso informativo; fuentes y MathJax inicializados. Se conserva su texto original. El añadido de muestras al final de la página cambia la longitud del TOC, no el contenido comparado.

| Tema | Antes | Después |
|---|---|---|
| Claro | ![Antes, claro](../artifacts/v0.2/comparison/before-1440-light.png) | ![Después, claro](../artifacts/v0.2/comparison/after-1440-light.png) |
| Oscuro | ![Antes, oscuro](../artifacts/v0.2/comparison/before-1440-dark.png) | ![Después, oscuro](../artifacts/v0.2/comparison/after-1440-dark.png) |

En oscuro, el azul nativo `rgb(4, 33, 76)` con opacidad .85 se sustituye por azul pizarra **`#354b69` opaco**. El icono pasa al azul de marca `#93b4ff` y el título a `#f5f8ff`. El cuerpo conserva `#1b2638`. En claro se aproxima la cabecera al azul suave ya presente en el sistema y se elimina la opacidad heredada. No se alteran las dimensiones del aviso estático.

En el resto de la interfaz se añade un fondo suave a los ejercicios, color verde azulado a sus títulos relacionados y acciones secundarias, y algo más de presencia al estado activo de navegación. Se mantienen tipografía, radios, grilla y jerarquía de v0.1. No se añaden tarjetas decorativas.

## Comparación móvil

| Ancho / tema | Antes | Después |
|---|---|---|
| 390 claro | [PNG](../artifacts/v0.2/comparison/before-390-light.png) | [PNG](../artifacts/v0.2/comparison/after-390-light.png) |
| 390 oscuro | [PNG](../artifacts/v0.2/comparison/before-390-dark.png) | [PNG](../artifacts/v0.2/comparison/after-390-dark.png) |
| 320 claro | [PNG](../artifacts/v0.2/comparison/before-320-light.png) | [PNG](../artifacts/v0.2/comparison/after-320-light.png) |
| 320 oscuro | [PNG](../artifacts/v0.2/comparison/before-320-dark.png) | [PNG](../artifacts/v0.2/comparison/after-320-dark.png) |

El viewport móvil tiene también 1000 px de alto. El cuerpo no genera scroll horizontal global; fórmulas, tablas, código y gráficos conservan su desplazamiento local. No se simuló un teléfono real.

## Cinco tipos y estados iniciales

Cada captura muestra el ejemplar cerrado y el abierto al inicio, con los tipos adyacentes cuando caben. El mismo recorrido abre con Enter, cierra con Espacio y activa por puntero el ejemplar inicialmente abierto.

| Tipo | Escritorio claro | Escritorio oscuro | Móvil claro | Móvil oscuro |
|---|---|---|---|---|
| note | [PNG](../artifacts/v0.2/comparison/states-note-1440-light.png) | [PNG](../artifacts/v0.2/comparison/states-note-1440-dark.png) | [PNG](../artifacts/v0.2/comparison/states-note-390-light.png) | [PNG](../artifacts/v0.2/comparison/states-note-390-dark.png) |
| tip | [PNG](../artifacts/v0.2/comparison/states-tip-1440-light.png) | [PNG](../artifacts/v0.2/comparison/states-tip-1440-dark.png) | [PNG](../artifacts/v0.2/comparison/states-tip-390-light.png) | [PNG](../artifacts/v0.2/comparison/states-tip-390-dark.png) |
| important | [PNG](../artifacts/v0.2/comparison/states-important-1440-light.png) | [PNG](../artifacts/v0.2/comparison/states-important-1440-dark.png) | [PNG](../artifacts/v0.2/comparison/states-important-390-light.png) | [PNG](../artifacts/v0.2/comparison/states-important-390-dark.png) |
| caution | [PNG](../artifacts/v0.2/comparison/states-caution-1440-light.png) | [PNG](../artifacts/v0.2/comparison/states-caution-1440-dark.png) | [PNG](../artifacts/v0.2/comparison/states-caution-390-light.png) | [PNG](../artifacts/v0.2/comparison/states-caution-390-dark.png) |
| warning | [PNG](../artifacts/v0.2/comparison/states-warning-1440-light.png) | [PNG](../artifacts/v0.2/comparison/states-warning-1440-dark.png) | [PNG](../artifacts/v0.2/comparison/states-warning-390-light.png) | [PNG](../artifacts/v0.2/comparison/states-warning-390-dark.png) |

Estas imágenes son evidencia local ignorada por Git y excluida de la publicación Quarto. La revisión se limita a capturas; las pruebas manuales pendientes se enumeran en [PRUEBAS.md](PRUEBAS.md).
