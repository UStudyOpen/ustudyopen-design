# Corrección incremental de callouts en v0.2

## Causa comprobada en Quarto 1.10.18

El archivo instalado `share/formats/html/bootstrap/_bootstrap-rules.scss` genera:

| Regla | Especificidad | Efecto |
|---|---|---|
| `.callout.callout-style-default > .callout-header` (v0.1) | `(0,3,0)` | Intentaba aplicar `surface-alt`, pero perdía frente a la regla siguiente. |
| `div.callout-note.callout-style-default > .callout-header` (Quarto) | `(0,3,1)` | Azul nativo oscurecido un 70% en fondo oscuro; no usa los colores de marca de UStudyOpen. |
| `.callout.callout-style-default > div.callout-header` (Quarto) | `(0,3,1)` | `opacity: .85` sobre toda la cabecera, incluidos texto e iconos. |
| `div.callout-note.callout` (Quarto) | `(0,2,1)` | El borde nativo ganaba al selector `div.callout-note` de v0.1. |
| `div.callout-note.callout-titled .callout-icon::before` (Quarto) | `(0,3,2)` | SVG con un fill propio en el data URI; cambiar `color` no lo recolorea. |

La pseudoforma `::before` cuenta como selector de tipo en la última fila. En los cinco tipos, Quarto produce variantes equivalentes. La versión inicial calculaba en oscuro `rgb(4, 33, 76)` para la cabecera informativa, con opacidad .85. Los valores de la captura inicial se guardan en `artifacts/v0.2/callouts-before.json`.

## Solución compartida

`scss/_callouts.scss` se importa después de las reglas nativas y **iguala** sus selectores específicos por tipo. La posición posterior resuelve el empate. No se edita `_site`, no se depende de una clase de tema añadida por JavaScript y no se usa `!important` en los callouts.

- La marca define `--uso-callout-note-header`: `#eff6ff` en claro y **`#354b69` azul pizarra** en oscuro. El cuerpo conserva `--uso-surface`.
- Cabeceras con `opacity: 1`, texto `--uso-heading`, borde exterior `--uso-callout-border` y franja/icono por intención: primary, emphasis, danger o warning. Caution y warning comparten la familia ámbar, conservando título e icono nativos distintos.
- Los cinco iconos usan sus formas del mapa SCSS de Quarto como máscaras CSS; el color efectivo procede de `--uso-callout-accent`. La flecha usa una máscara sencilla con `currentColor`; las rotaciones de Quarto se conservan.
- Los desplegables mantienen Bootstrap, `aria-controls`, `aria-expanded` y sus objetivos generados. La extensión hace accesible por teclado la cabecera `div`, con `role="button"`, `tabindex="0"`, Enter y Espacio. Se retira su nombre genérico inglés para utilizar el título visible. No se reconstruyen los callouts ni se asignan IDs fijos.
- Los estados se prueban con un ejemplar estático, otro cerrado y otro abierto inicialmente para cada tipo (15 en total). La galería añade solamente muestras técnicas; los enunciados y soluciones anteriores no cambian.

La extensión usa el mapa interno `$callouts` de Quarto para evitar copiar las formas de los iconos. **Riesgo:** es una dependencia de implementación, cubierta en 1.10.18; revisar al actualizar el generador. No se amplía el rango de compatibilidad.

## Criterios de contraste

Se mide el CSS calculado, incluyendo `::before`, opacidad y los fondos adyacentes. Objetivos: texto, títulos y enlaces **4.5:1**; iconos, flecha, franjas y contornos funcionales **3:1**. Se comprueban también los fondos a ambos lados de la franja y los bordes exteriores frente a cuerpo/cabecera. El contraste entre dos superficies decorativas no exige por sí mismo 3:1: la identificación y el estado del control dependen de su título, foco y flecha. Fuentes: [WCAG 2.2, 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) y [1.4.11](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html).

Los resultados y mínimos reales, sin redondear para decidir si pasan, están en [PRUEBAS.md](PRUEBAS.md). La diferenciación visual del azul pizarra se revisa con capturas; no se presenta como una certificación WCAG de todo el sitio.
