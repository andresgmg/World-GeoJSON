# Cuerpos planetarios

La Luna y Marte rompen casi todos los supuestos que hace el resto de esta
referencia. Esta página explica exactamente cómo, porque equivocarse aquí
produce datos que parecen correctos y están desplazados de forma silenciosa y
sistemática.

## El problema de fondo

[RFC 7946 §4](https://www.rfc-editor.org/rfc/rfc7946#section-4) dice que las
coordenadas GeoJSON están en WGS 84 — un datum definido por un elipsoide
ajustado a la Tierra — y eliminó el miembro `crs` que permitiría a un archivo
decir otra cosa.

Marte no es la Tierra. Sus coordenadas no son WGS 84 y no pueden serlo. Pero un
archivo GeoJSON conforme no tiene forma de decirlo.

!!! danger "Los archivos planetarios aquí tienen *forma de* RFC 7946, pero no son *conformes*"

    Es una desviación deliberada y documentada del estándar, no un descuido.

    Un archivo de Marte en este repositorio es GeoJSON sintácticamente válido
    que cualquier parser leerá. Sus coordenadas son grados. Pero son grados en
    Marte, y **el archivo no puede decírtelo**. Un consumidor que asuma WGS 84
    — cosa a la que la especificación le da derecho — colocará el Monte Olimpo
    en algún punto del Pacífico.

    Por eso la declaración autoritativa de CRS vive en
    [`manifest.json`](manifest.md), y leerla es **obligatorio** antes de usar
    datos planetarios. No hay alternativa dentro del archivo.

## Sistemas de referencia

Las coordenadas planetarias usan marcos body-fixed del grupo de trabajo IAU/IAG
sobre coordenadas cartográficas y elementos de rotación, cuyo informe de 2015
es la referencia actual. Están registrados en PROJ bajo la autoridad
`IAU_2015`.

| Cuerpo | Marco | Radio de referencia |
|---|---|---|
| Luna | `IAU_2015:30100` | 1 737 400 m (esfera) |
| Marte | `IAU_2015:49900` | 3 396 190 m ecuatorial |

En un manifiesto:

```json
"crs": {
  "authority": "IAU_2015",
  "code": "49900",
  "body": "mars",
  "proj": "+proj=longlat +R=3396190 +no_defs",
  "note": "Latitud planetocéntrica, longitud este-positiva, -180..180"
}
```

Se incluye la cadena `proj` para que los consumidores puedan pasarla
directamente a GDAL, PROJ, `pyproj` o `rasterio` sin buscar nada.

## Los dos errores que todo el mundo comete

### Latitud planetocéntrica frente a planetográfica

Hay dos definiciones distintas de "latitud" en uso activo para Marte:

- **Planetocéntrica** — el ángulo desde el centro del cuerpo. Lo que usa este
  proyecto.
- **Planetográfica** — el ángulo de la normal a la superficie respecto al plano
  ecuatorial.

En una esfera perfecta son idénticas. Marte es lo bastante achatado como para
que difieran **hasta unos 0,3°**, que son aproximadamente 18 km en el ecuador.
Suficiente para situar una feature en el cráter equivocado, y lo bastante poco
como para que nada parezca roto.

**Este proyecto guarda latitud planetocéntrica.** Los datasets que lleguen en
planetográfica deben convertirse antes de mergearse, y el manifiesto registra
qué convención aplica.

### Longitud este-positiva frente a oeste-positiva

Los mapas históricos de Marte usaban longitud oeste-positiva. La práctica
moderna, y la recomendación de la IAU para Marte, es **este-positiva**. Los
datos lunares también son este-positivos.

Mezclar ambas refleja tu mapa respecto al meridiano de origen. Como muchas
features planetarias tienen una distribución aproximadamente simétrica, a
menudo no se nota a simple vista.

**Este proyecto guarda longitud este-positiva en el dominio −180…180**, por
consistencia con los datos terrestres y porque la mayoría de las bibliotecas de
mapas web lo asumen. Las fuentes que usen el dominio 0…360 deben convertirse.

## No hay ISO 3166 para otros mundos

No existe registro de "países" para la Luna ni para Marte, y bajo el Tratado
del Espacio Exterior es poco probable que llegue a haberlo. Así que la
convención de nombres sustituye:

- **Código de cuerpo** en lugar de código de país — `MOON`, `MARS`. Se eligen
  de cuatro caracteres para que nunca puedan colisionar con un ISO 3166-1
  alpha-3 de tres caracteres, presente o futuro.
- **`QUAD`** en lugar de nivel administrativo, para los esquemas de cuadrángulos
  del USGS, que son lo más parecido a una subdivisión sistemática de una
  superficie planetaria.
- **Nombres de features** del
  [IAU Gazetteer of Planetary Nomenclature](https://planetarynames.wr.usgs.gov/),
  que es el registro autoritativo de nombres aprobados para accidentes
  superficiales. No inventes nombres ni uses apodos informales de misiones.

```
data/moon/MOON/MOON_QUAD.geojson
data/mars/MARS/MARS_QUAD.geojson
```

`shapeGroup` lleva el código del cuerpo; `shapeType` es `QUAD`.

## Mapas base

No existen servicios de teselas en Web Mercator para cuerpos planetarios. USGS
Astrogeology publica endpoints WMS equirectangulares, así que los mapas de
preview de estos cuerpos usan plate carrée al estilo `EPSG:4326` en vez del Web
Mercator que usan los mapas terrestres.

Por eso `geojson-map.js` lee un atributo `data-body`: de ahí selecciona tanto
el mapa base como la proyección.

## Estado

**Todavía no se ha añadido nada planetario.** Esta página se escribe primero, a
propósito. Las convenciones de arriba son las caras de cambiar una vez que
existen archivos — en particular la de latitud, que no se puede detectar a
posteriori a partir de los propios datos.

--8<-- "abbreviations.md"
