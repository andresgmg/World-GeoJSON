# Contribuir

Hay dos tipos de contribución y funcionan de forma bastante distinta.

## Corregir la documentación

Pulsa el icono :material-pencil: en la parte superior de cualquier página. Abre
ese archivo en GitHub; edita, describe el cambio y envíalo. No hace falta
configurar nada localmente.

Si quieres previsualizar los cambios antes, ver
[Editar la documentación](docs.md).

!!! note "Las páginas del catálogo no se editan directamente"

    Las páginas bajo **Catálogo** se generan desde el `manifest.json` de cada
    dataset. Su botón de edición apunta al manifiesto, que es lo que hay que
    cambiar. Editar la página generada es imposible — no existe en disco.

## Añadir o corregir datos

Este proceso es más largo, porque un archivo de límites tiene un peso legal y
factual que una errata de documentación no tiene.

1. **Verifica la licencia primero.** No al final.
   [Fuentes aprobadas y licencias](sources.md) tiene la lista
   verde/ámbar/roja. Es el paso que más probablemente termine con una
   contribución, así que hacerlo primero te ahorra todo el resto del trabajo.
2. Sigue [Añadir un país](add-a-country.md) de principio a fin.
3. Repasa el [Checklist de revisión](checklist.md) antes de abrir el PR.

### Qué hace que se rechace un PR

Siendo directos, porque la alternativa es hacerte perder el tiempo:

- **Una licencia de origen incompatible.** GADM en particular es la fuente
  global más cómoda y no es utilizable aquí. Ver
  [fuentes](sources.md#rojo-no-usar).
- **Sin fuente declarada.** "Lo encontré en internet" no es procedencia. El
  bloque `source` del manifiesto es obligatorio.
- **Geometría editada para reflejar una posición política.** Ver
  [Fronteras disputadas](../about/disputed-boundaries.md).
- **Archivos que ignoran las convenciones** de
  [Referencia](../reference/index.md). Esto suele ser corregible — espera
  comentarios de revisión, no un rechazo.

## Reportar un problema, proponer un país

[Abre un issue](https://github.com/andresgmg/World-GeoJSON/issues/new/choose).
Tres formularios piden lo que una revisión necesita:

- **País o territorio nuevo** — la fuente, su licencia SPDX y dónde consta
  esa licencia. Lee antes [Fuentes aprobadas](sources.md): ahí es donde
  fallan la mayoría de las propuestas.
- **Problema de datos** — la ruta del dataset, el `id` de la feature
  (`CHL:ADM3:01402`), la versión de datos de la que lo leíste y evidencia.
  Una captura de la geometría incorrecta vale mucho.
- **Bug de biblioteca** — el paquete, su versión, tu runtime y una
  reproducción mínima.

Los huecos ya conocidos están en la [Hoja de ruta](../about/roadmap.md) —
conviene mirarla antes de abrir uno. Los pull requests traen una plantilla con
las comprobaciones que ejecuta CI; marcarlas antes de abrirlo ahorra una vuelta.

## Reglas básicas

Aplica el [Código de conducta](code-of-conduct.md). Aquí no es texto de
relleno: un repositorio de fronteras nacionales atrae disputas de soberanía, y
esas conversaciones tienen que mantenerse en lo técnico.

--8<-- "abbreviations.md"
