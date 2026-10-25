# Tokens v0.2

Colores de la sección 7 de la auditoría. Fuente autorizada: `brand/_brand.yml` y `brand/_brand-dark.yml` dentro de la extensión. SCSS consume `$brand-uso-*` en reglas y publica `--uso-*`; no se repiten mapas de colores en los componentes.

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--uso-bg` | `#f4f6fa` | `#111827` | Fondo del sitio |
| `--uso-surface` | `#ffffff` | `#1b2638` | Lectura y controles |
| `--uso-surface-alt` | `#eef2f8` | `#243247` | Código y superficies secundarias |
| `--uso-inline-code-bg` | `#e2e8f0` | `#475569` | Código inline en prosa, incluidas etiquetas de atributos; rol separado del código en bloque. |
| `--uso-inline-code-text` | Alias de `--uso-text` (`#243247`) | Alias de `--uso-text` (`#e8eef7`) | Texto sobre `inline-code-bg`; contraste 10,50:1 / 6,50:1. |
| `--uso-text` | `#243247` | `#e8eef7` | Texto principal |
| `--uso-heading` | `#182b49` | `#f5f8ff` | Encabezados |
| `--uso-muted` | `#58677b` | `#b3bfd0` | Texto secundario |
| `--uso-primary` | `#2563eb` | `#93b4ff` | Acciones, selección y serie principal |
| `--uso-on-primary` | `#ffffff` | `#111827` | Texto sobre acción primaria |
| `--uso-primary-hover` | `#1d4ed8` | `#b7ceff` | Acción en hover |
| `--uso-link` | `#1d4ed8` | `#a8c7ff` | Enlaces en prosa |
| `--uso-primary-soft` | `#eff6ff` | `#213656` | Selección suave |
| `--uso-emphasis` | `#147d78` | `#64d8cf` | Acento de aprendizaje y segunda serie |
| `--uso-emphasis-soft` | `#e7f4f2` | `#173d3c` | Fondo académico suave |
| `--uso-success` | `#18734b` | `#80d5a6` | Confirmación |
| `--uso-warning` | `#98620a` | `#f4c46a` | Advertencia |
| `--uso-danger` | `#c03642` | `#ff9ba7` | Error |
| `--uso-border` | `#dce3ed` | `#40516a` | Divisor decorativo |
| `--uso-control-border` | `#7a899b` | `#8192a9` | Contorno funcional |
| `--uso-focus` | `#2563eb` | `#93b4ff` | Foco visible |
| `--uso-series-3` | `#674ea7` | `#c4b5fd` | Serie adicional opcional |

## Escala y alias

| Tokens | Valores / contrato |
|---|---|
| `--uso-space-0` … `--uso-space-8` | `0`, `.25`, `.5`, `.75`, `1`, `1.5`, `2`, `3`, `4rem` |
| `--uso-radius-control` | `.375rem` |
| `--uso-radius-panel` | `.625rem` |
| `--uso-radius-hero` | `.875rem`, reservado; la portada actual usa separador sencillo |
| `--uso-font-body` | `system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif` |
| `--uso-font-code` | `"SFMono-Regular", Consolas, "Liberation Mono", monospace` |
| `--uso-shadow` | `0 .25rem 1rem rgb(0 0 0 / 6%)`, reservado para elevación necesaria |
| `--uso-reading-width` | `70ch`, referencia para futuras superficies; el layout actual usa grilla nativa de Quarto |
| `--uso-chart-axis` | Alias de `--uso-control-border` |
| `--uso-chart-grid` | Alias de `--uso-border`, decorativo |
| `--uso-series-1` / `--uso-series-2` | Alias de `--uso-primary` / `--uso-emphasis` |

Base 1rem, interlineado 1.7. H1 fluido 2–2.5rem; H2 1.6rem; H3 1.25rem; H4 1.1rem. Los componentes se adaptan al ancho sin reescribir la grilla `.page-columns` de Quarto.

## Combinaciones de uso y contraste

Texto principal, secundario, títulos y enlaces se contrastan frente a `bg`, `surface` y `surface-alt`. Los botones primarios usan `on-primary`; no blanco fijo en el tema oscuro. Los contornos funcionales y el foco tienen objetivo mínimo 3:1 sobre las superficies donde se usan.

**Restricción:** `--uso-emphasis` claro sobre `--uso-surface-alt` alcanza aproximadamente **4.41:1**. No usar esa pareja para texto normal; sí puede usarse para trazos de gráfico (objetivo 3:1). El texto de énfasis de la galería está sobre `surface` o `bg`. Para texto sobre fondos secundarios usar `text` o `link`. El color original `#147d78` se conserva conforme a la identidad aprobada. La matriz de contraste distingue este uso gráfico del textual.

`--uso-border` separa zonas de forma decorativa; no sustituye `--uso-control-border` para identificar entradas o ejes. Las series combinan color, línea continua/discontinua, marcadores y leyendas. El significado de una serie no equivale a éxito/error.

Los contrastes calculados cubren pares de tokens, no toda combinación arbitraria, antialiasing ni el conjunto de estados de Bootstrap. Consultar [PRUEBAS.md](PRUEBAS.md) para resultados y límites. No se declara conformidad WCAG completa.

## Ejemplo de consumo

```css
.mi-componente {
  color: var(--uso-text);
  background: var(--uso-surface);
  border: 1px solid var(--uso-border);
  padding: var(--uso-space-5);
}
.mi-componente .serie {
  stroke: var(--uso-series-1);
}
```

El cambio de tema activa las hojas de Quarto; no se agrega un segundo mapa a `body` ni un gestor de tema propio.

La fuente y el alcance del componente inline se documentan en [INLINE_CODE.md](INLINE_CODE.md). No sustituir estos tokens por overrides de curso ni alterar `surface-alt` para corregir etiquetas: esa superficie también pertenece a bloques de código y otros componentes.

## Roles añadidos en v0.2

La paleta azul y verde azulado original se conserva. Se añaden roles específicos, no una sustitución general de los colores.

| Token | Claro | Oscuro | Uso |
|---|---|---|---|
| `--uso-emphasis-ink` | `#106b67` | `#64d8cf` | Texto de énfasis sobre superficies y fondos académicos suaves; evita la pareja de 4.41:1 del acento original. |
| `--uso-callout-note-header` | `#eff6ff` | `#354b69` | Cabecera informativa, azul pizarra en oscuro. |
| `--uso-callout-tip-header` | `#e7f4f2` | `#244b49` | Cabecera de consejo. |
| `--uso-callout-important-header` | `#fff0f2` | `#4a303c` | Cabecera de importante. |
| `--uso-callout-warning-header` | `#fff5df` | `#443b29` | Cabecera de warning/caution. |
| `--uso-callout-border` | `#7a899b` | `#93a4bb` | Borde exterior, contrastado también contra la cabecera pizarra. |

Cada `div.callout` publica alias locales `--uso-callout-header`, `--uso-callout-accent`, `--uso-callout-heading` y `--uso-callout-body`. Los tipos modifican solo el encabezado y el acento. El texto del encabezado usa `heading` y el cuerpo usa `text` sobre `surface`. Los iconos usan el acento y la flecha hereda el texto.

Los ejercicios utilizan `primary-soft`, títulos de ejercicio `link`, títulos académicos `emphasis-ink`, y las fichas/resúmenes incorporan una línea superior de acento. La navegación activa refuerza el azul mediante fondo suave, peso y subrayado; no comunica el estado exclusivamente por color.

[CALLOUTS.md](CALLOUTS.md) explica la cascada y la decisión de máscaras. No añadir colores literales en componentes para corregir un tema: definir el rol en ambos archivos de marca.
