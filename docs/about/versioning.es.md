# Versionado y estabilidad

## Qué cuenta como API pública

En un repositorio de datos, la API no es la firma de una función. Es:

1. **Las rutas de archivo.** La gente pone URLs a fuego en su código.
2. **Los nombres y tipos de las propiedades.** La gente escribe código contra
   `feature.properties.shapeName`.
3. **La identidad de las features.** Los valores de `shapeISO` — y, desde
   v1.0.0, el `id` de Feature — se usan como claves de join.

Cambiar cualquiera de estas cosas rompe a los consumidores en silencio — sin
error de compilación, sin excepción, solo un mapa que se dibuja vacío o un join
que no encuentra nada.

La geometría es distinta. Los refinamientos de límites, los vértices añadidos y
las costas corregidas son esperables dentro de una misma versión.

## Versionado semántico

| Cambio | Incremento |
|---|---|
| Renombrar o mover un archivo | **Mayor** |
| Renombrar una propiedad, o cambiar su tipo | **Mayor** |
| Cambiar valores de `shapeISO` | **Mayor** |
| Eliminar un dataset | **Mayor** |
| Añadir un país o un nivel | Menor |
| Añadir una propiedad opcional | Menor |
| Refinar geometría | Parche |
| Corregir un nombre o una errata | Parche |

Las releases son etiquetas de git. **Todavía no existe ninguna**: `v1.0.0` es
la primera prevista, en cuanto esté en su sitio el contrato de datos de la
[Hoja de ruta](roadmap.md). Hasta entonces la única referencia es `main`, a
través de URLs crudas:

```
https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/<ruta>
```

Una vez etiquetada `v1.0.0`, **fija la etiqueta en producción** — la misma URL
cruda con la etiqueta en lugar de `main`, o la forma `@etiqueta` de jsDelivr:

```
https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v1.0.0/<ruta>
https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0/<ruta>
```

`main` sigue la rama por defecto, así que una corrección de límites aguas
arriba llega a tu aplicación sin previo aviso.

!!! note "jsDelivr puede rechazar este repositorio"

    jsDelivr documenta límites de 150 MB por repositorio y 20 MB por archivo
    para su endpoint de GitHub, y este repositorio supera los 150 MB. Las URLs
    crudas, o un sparse checkout de git de los directorios de país que
    necesites, son la vía fiable hoy.

Desde v1.0.0, cada release publica además **zips por país** como assets de la
GitHub Release — un archivo por territorio con sus archivos y su manifiesto —
para quien prefiera una descarga a un clon o un CDN.

## Los archivos heredados de la raíz

Chile vive ahora en `data/earth/CHL/` bajo el esquema estándar de propiedades,
construido desde la DPA 2023 de IDE Chile. Los archivos antiguos siguen en la
raíz del repositorio y están obsoletos:

| Obsoleto | Reemplazo |
|---|---|
| `/main/regiones.geojson`, `/main/regiones.json` | `/main/data/earth/CHL/CHL_ADM1.geojson` |
| `/main/comunas.geojson`, `/main/comunas.json` | `/main/data/earth/CHL/CHL_ADM3.geojson` |
| `properties.Region` / `properties.Comuna` | `properties.shapeName` |
| `properties.cod_comuna` (número) | `properties.shapeISO` (cadena, con ceros) |

Los reemplazos no son equivalentes byte a byte. Vienen de otra fuente (la DPA
2023 de IDE Chile en vez del conjunto vectorial más antiguo de BCN), llevan otro
esquema de propiedades, contienen 345 comunas en vez de 343 y están
simplificados a una tolerancia documentada de 100 m. Trátalo como una
migración, no como un movimiento de archivos.

### Ventana de obsolescencia

Los cuatro archivos de la raíz — `regiones.geojson`, `regiones.json`,
`comunas.geojson`, `comunas.json` — **se quedan donde están, sin cambios,
durante toda la serie 1.x, y se retiran en v2.0.0.**

No es por prolijidad. Alguien ahí fuera tiene
`raw.githubusercontent.com/…/main/comunas.geojson` en producción. Moverlo
devuelve un 404 sin explicación, y no existe mecanismo de redirección para URLs
de datos crudos — `mkdocs-redirects` solo maneja páginas de documentación. La
única ruta de migración decente es dejar los archivos antiguos donde están y
anunciar el movimiento.

Se eliminarán en una release etiquetada, no en silencio sobre `main`.

## Por qué no Git LFS

La reacción obvia ante un archivo de 72 MB, y una trampa.

- **Cuota de ancho de banda.** El tier gratuito de GitHub permite 1 GB/mes de
  ancho de banda LFS. Un repositorio de datos público y popular la agota en
  días, y a partir de ahí **las descargas fallan para todo el mundo** hasta que
  alguien compre paquetes de datos.
- **Rompe los CDNs.** jsDelivr y la mayoría de los espejos sirven el archivo
  puntero de LFS — un stub de texto de 132 bytes — en lugar de los datos.
- **Complica los clones parciales.** `--filter=blob:none` y el sparse checkout
  interactúan mal con LFS.
- **No hace falta.** El tamaño empaquetado del repositorio es de unos 56 MiB
  para un working tree de unos 309 MB, 164 MB de ellos bajo `data/`. El JSON
  comprime bien y Git lo está manejando sin problema.

La solución real al tamaño de archivo es minificar y recortar la precisión de
coordenadas, y los archivos nuevos ya la aplican: una feature por línea con seis
decimales deja `CHL_ADM3.geojson` en 7 MB donde el `comunas.geojson` heredado
pesa 72 MB.

## Versionado de las bibliotecas

Las bibliotecas cliente previstas en la Fase 3 de la
[Hoja de ruta](roadmap.md) — Python `world-geojson`, TypeScript
`@world-geojson/core` — se versionan **con independencia de los datos**:

- El semver de una biblioteca describe su propia API. Su mayor sube cuando se
  rompe la firma de una función, no cuando se mueve un límite.
- Cada biblioteca declara qué `schema_version` de datos (del manifiesto y de
  `index.json`) soporta, y fija por defecto una etiqueta de datos, para que una
  release de datos nunca llegue a una aplicación sin aviso a través de una
  actualización de la biblioteca.
- Una menor de datos (un país nuevo, un nivel nuevo) no necesita cambios en la
  biblioteca. Una mayor de datos que cambie el esquema necesita una release de
  la biblioteca que declare soportarla.

## Dar de baja un dataset

Un dataset cuya fuente deje de ser utilizable — cambio de licencia, retirada —
se marca como `"status": "deprecated"` en su manifiesto y se señala en su
página de catálogo, con un puntero al reemplazo si existe. Se elimina en la
siguiente release mayor.

Los datos no se borran de la historia de git. Reescribir la historia rompe
todos los clones y forks existentes, y para un repositorio de datos público ese
coste supera con mucho al beneficio.

--8<-- "abbreviations.md"
