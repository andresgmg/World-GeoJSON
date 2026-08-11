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

## Reportar un problema

[Abre un issue](https://github.com/andresgmg/World-GeoJSON/issues). Los reportes
útiles incluyen el dataset, la feature concreta y qué esperabas. Una captura de
la geometría incorrecta vale mucho.

Los huecos ya conocidos están en la [Hoja de ruta](../about/roadmap.md) —
conviene mirarla antes de abrir uno.

## Reglas básicas

Aplica el [Código de conducta](code-of-conduct.md). Aquí no es texto de
relleno: un repositorio de fronteras nacionales atrae disputas de soberanía, y
esas conversaciones tienen que mantenerse en lo técnico.

--8<-- "abbreviations.md"
