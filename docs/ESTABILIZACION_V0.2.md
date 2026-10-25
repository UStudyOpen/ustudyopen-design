# Estabilización de la compilación v0.2

Evaluación local del 25 de octubre de 2026. Quarto **1.10.18**, sin cambios de identidad visual.

## Diagnóstico del ZIP recibido

`ustudyopen-design.zip` contiene cinco páginas, cuatro hojas Bootstrap de tema y
la caché `.quarto/`. `index.html` y `sistema.html` referencian el par
`b9496e33889faf98dbfbba3985e455a7` / `dark-2c44e887fd691e7fad8e72a7a12ea7d7`;
las otras tres páginas referencian
`695881a9f5374700d35cb714eaf1fcca` / `dark-4b56ad18b24ece4f15a4b3e5e7169427`.
Los primeros CSS tienen fecha ZIP 01:18:08 y los segundos 01:24:52.

La diferencia entre ambos pares está en el selector del botón secundario. La
fuente actual usa `.uso-button.uso-button--secondary`, con especificidad para
prevalecer sobre las reglas genéricas del botón; el segundo par contiene
`.uso-button--secondary` y una declaración adicional `color:var(--uso-link)`.
Una compilación aislada de las fuentes actuales produce el primer par.

La evidencia identifica una salida formada por renders de distintas revisiones
del SCSS: los nombres incluyen hashes distintos y los HTML conservan referencias
a ambas revisiones. Es compatible con renders parciales posteriores a cambios de
estilo; el ZIP no permite reconstruir los comandos exactos ni su orden. La
presencia de `.quarto` no demuestra por sí misma un fallo de caché de Quarto.
El problema comprobado es distribuir una salida incremental sin reconstruirla
íntegramente ni comprobar que todas las páginas usan el mismo par.

## Corrección y reproducción

```sh
python3 tests/clean_render.py
python3 tests/check_site.py
python3 tests/check_repository.py
bash tests/run-browser.sh
```

`clean_render.py` exige Quarto 1.10.18, copia exclusivamente las fuentes del
prototipo a dos directorios temporales vacíos y usa una caché XDG nueva en cada
uno. No copia `.quarto`, `_site` ni resultados anteriores. Compara SHA-256 de
todos los archivos publicados entre ambas compilaciones y solo entonces
reemplaza `_site/`. Conserva logs y manifiesto en `artifacts/stabilization/`.
No altera la extensión aprobada ni el ZIP recibido, que queda como evidencia.

`check_site.py` comprueba ahora las cinco rutas exactas y el par referenciado por
cada página, además de exigir dos hojas compiladas. Así detecta una salida
mezclada incluso si alguien elimina las hojas sobrantes.
Se ejecutó el comprobador actualizado contra una extracción temporal del ZIP:
rechazó correctamente sus cuatro hojas y los pares incoherentes (código 1).
El resultado esperado está en `artifacts/stabilization/zip-regression.json`;
esta prueba negativa no es un fallo del sitio reconstruido.

Los resultados de esta ejecución y el punto de paso a la integración piloto se
registran en el informe de revisión del workspace. Los resultados históricos de
`PRUEBAS.md` no sustituyen esta nueva ejecución.

## Distribución

Para una futura entrega, preparar los fuentes sin cachés ni perfiles. Si se
incluye `_site`, generarlo con la receta limpia y ejecutar todas las
comprobaciones antes de empaquetarlo. No producir un ZIP a partir de un
directorio de preview activo. Esta tarea no publica ni modifica GitHub Pages.
