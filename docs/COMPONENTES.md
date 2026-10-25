# Componentes v0.2

Se escriben con Markdown/QMD y HTML semántico. No requieren filtros propios ni un framework de interfaz. La extensión controla apariencia y accesibilidad de presentación; el autor mantiene títulos, instrucciones y significado.

| Componente | API visual | Contrato editorial |
|---|---|---|
| Definición / teorema | `.uso-academic` | Título real «Definición / Teorema · Nombre», contenido y condiciones. |
| Ejemplo | `.uso-academic.uso-example` | Pasos, resultado y título explícito. |
| Ejercicio | `.uso-academic.uso-exercise` | Enunciado e instrucciones; solución opcional. |
| Solución | `details.uso-solution > summary` | Texto del control que describe su propósito; teclado nativo. |
| Ficha de fórmula | `.uso-formula` | Encabezado, expresión y condiciones de uso. |
| Resumen | `.uso-summary` | Encabezado y lista corta de ideas. |
| Avisos | `.callout-note`, `.callout-tip`, `.callout-important`, `.callout-caution`, `.callout-warning` | Callouts nativos de Quarto con título. |
| Tabla | `.uso-table-wrap` | `role="region"`, nombre, `tabindex="0"`; tabla con caption y `scope`. |
| Código | Bloques cercados | Copia y sintaxis de Quarto; región de scroll con acceso por teclado. |
| Código inline / atributos | `main.content :is(p, li, td) > code:not(.sourceCode)` | Backticks Markdown en prosa, listas y celdas. Colores `--uso-inline-code-*`, sin clases específicas del curso. Véase [alcance y cascada](INLINE_CODE.md). |
| Estado | `.uso-status` + modificador | `--lista`, `--en-desarrollo`, `--proximamente`; texto y símbolo. No es un enlace. |
| Acción | `.uso-button`, `--secondary` | `<a>` para navegar; `<button>` para actuar. Altura objetivo 44 px. |
| Campo | `.uso-field` | `label` enlazado por `for/id`, ayuda con `aria-describedby`, error con `aria-invalid`. |
| Checkbox | `.uso-check` | Etiqueta clicable de al menos 44 px de alto, control de 24 px. |
| Gráfico | `.uso-chart-wrap`, `.uso-chart` | SVG con `title/desc`, leyenda textual, scroll local y resultado textual. |

## Bloques académicos

```markdown
::: {.uso-academic .uso-exercise}
### Ejercicio · Evaluar una función

Calcula $f(2)$ para $f(x)=x+1$.

<details class="uso-solution">
<summary>Ver solución</summary>

$f(2)=3$.

</details>
:::
```

Puede asignarse un ID con prefijo `uso-` al bloque para enlaces locales. Evitar prefijos reservados `def-`, `thm-`, etc. salvo que se quiera activar expresamente el sistema nativo de teoremas de Quarto. La galería usa encabezados explícitos, sin numeración automática. Los títulos permanecen en el nivel correcto de la página: H3 bajo secciones H2.

## Estados manuales

```html
<span class="uso-status uso-status--lista">
  <span aria-hidden="true">✓</span> Lista
</span>
<span class="uso-status uso-status--en-desarrollo">◐ En desarrollo</span>
<span class="uso-status uso-status--proximamente">○ Próximamente</span>
```

Los identificadores estables son `lista`, `en-desarrollo`, `proximamente`. La etiqueta visible usa ortografía natural en español. No se calculan estados ni se añade una falsa apariencia de enlace a unidades no disponibles.

## Tablas, matemática y código extensos

```html
<div class="uso-table-wrap" role="region"
     aria-label="Valores de la función; tabla desplazable" tabindex="0">
  <table>
    <caption>Entradas y salidas.</caption>
    <thead><tr><th scope="col">Entrada</th><th scope="col">Salida</th></tr></thead>
    <tbody><tr><th scope="row">2</th><td>3</td></tr></tbody>
  </table>
</div>
```

Las expresiones particularmente largas pueden envolverse en `.uso-math` con región etiquetada y `tabindex="0"`. La fórmula mantiene su escala y admite scroll local. No se reduce el texto matemático para hacer caber toda la expresión en móvil.

## Gráficos y formularios

Los gráficos usan `--uso-chart-axis`, `--uso-chart-grid` y `--uso-series-*`. No escriben colores hexadecimales ni escuchan cambios de tema. La línea continua, la referencia discontinua, el punto, la leyenda y la descripción no dependen solo del color. La cuadrícula es decorativa; los ejes tienen un color de contorno funcional.

El laboratorio mantiene el mismo nodo SVG y los valores de los controles al cambiar de tema. Tiene estado inicial estático y mejora progresiva. El botón de restablecer vuelve a `m=1` y activa la referencia. La actividad de comprobación usa validación nativa para campo obligatorio y mensajes asociados para respuesta incorrecta/correcta.

Los apuntes son volátiles; el prototipo no envía datos ni usa almacenamiento propio. Un curso futuro deberá definir el comportamiento académico y de persistencia que necesite.

## Avisos nativos y múltiples instancias

Quarto conserva `collapse="true"` (cerrado al inicio), `collapse="false"` (abierto al inicio), títulos, iconos, controles y ARIA generados. Ejemplo:

```markdown
::: {.callout-note title="Información" collapse="true"}
Texto del aviso.
:::
```

No copiar IDs generados por Quarto. Para repetir gráficos o formularios, usar una raíz por instancia, consultas locales y IDs distintos en cada asociación `for`, `aria-describedby` o `aria-labelledby`. Los IDs de `laboratorio.qmd` pertenecen a ese ejemplar de galería; no son API de la extensión. La extensión no instala su lógica de evaluación ni sus gráficos.
