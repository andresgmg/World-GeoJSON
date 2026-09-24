# Descarga y CDN

Hay varias formas de obtener los datos. No son intercambiables.

## CDN de jsDelivr

Rápido, cacheado globalmente, con cabeceras CORS correctas — cuando sirve el
repositorio.

```
https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@main/<ruta>
```

!!! danger "jsDelivr puede rechazar este repositorio"

    jsDelivr documenta dos límites para su endpoint de GitHub: **20 MB por
    archivo** y **150 MB por repositorio**. Todos los archivos bajo `data/`
    están por debajo del primero — el más grande pesa 14,9 MB, y los niveles
    que lo superarían se parten por ADM1. El repositorio en conjunto supera
    actualmente el segundo, así que jsDelivr puede negarse a servirlo. Trata
    el CDN como una optimización que probar, no como una dependencia: las URLs
    raw de GitHub son la ruta fiable hoy, y los
    [assets de la release](#assets-de-la-release) lo son a partir de v1.0.0.

    El `comunas.geojson` heredado de 72 MB en la raíz del repositorio supera
    el límite por archivo en cualquier caso. Usa
    `data/earth/CHL/CHL_ADM3.geojson`.

**Fija una etiqueta en producción.** `@main` sigue la rama por defecto, así que
una corrección de límites que se mergee aguas arriba cambia lo que recibe tu
aplicación, en silencio.

=== "Fijado (cuando exista la etiqueta v1.0.0)"

    ```
    https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0/<ruta>
    ```

    `v1.0.0` se etiqueta desde el merge del contrato de datos — ver
    [Versionado y estabilidad](../about/versioning.md). Hasta entonces solo
    resuelve `@main`. A partir de v1.0.0, los zips por país adjuntos a la
    GitHub Release son la descarga fijada recomendada.

=== "Última versión"

    ```
    https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@main/<ruta>
    ```

## Raw GitHub

```
https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/<ruta>
```

Funciona con archivos de cualquier tamaño y envía
`Access-Control-Allow-Origin: *`, así que `fetch` desde el navegador funciona.
Pero **no es un CDN**: sin caché de borde, y con límite de peticiones. Bien
para desarrollo, scripts y descargas desde servidor; mal para tráfico de
navegador en producción.

La misma URL con una etiqueta en lugar de `main` fija una versión de los datos
— una vez etiquetada `v1.0.0`:

```
https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v1.0.0/<ruta>
```

## Assets de la release

Cada etiqueta `vX.Y.Z` publica una GitHub Release con los datos como assets
descargables — el canal para descargas masivas y sin conexión, y el respaldo
cuando un CDN rechaza el repositorio por su tamaño:

| Asset | Contenido |
|---|---|
| `world-geojson-vX.Y.Z-{ISO3}.zip` | Uno por territorio: la carpeta del país con sus archivos, `manifest.json` y `preview/` |
| `world-geojson-vX.Y.Z-all.zip` | Todo lo que hay bajo `data/` |
| `index.json` | El [índice global](../reference/index-json.md) |
| `SHA256SUMS` | Hashes de todos los assets |

La primera es `v1.0.0`, etiquetada desde el merge del contrato de datos:
<https://github.com/andresgmg/World-GeoJSON/releases/tag/v1.0.0>. Las notas
de la release son la sección correspondiente del
[Registro de cambios](../about/changelog.md).

## El índice global

Descarga primero `data/index.json` y después solo los archivos que necesites:
enumera cada territorio y dataset con `path`, `bytes`, `sha256`, `bbox` y
licencia, e incrusta todos los manifiestos, en 340 KB (39 KB con gzip). Se
sirve desde las mismas URLs que los datos —

```
https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/index.json
```

— y va adjunto a cada release. Su forma, y fragmentos que lo usan, están en
[Índice global y esquemas](../reference/index-json.md).

## Previews

Para un mapa en el navegador rara vez quieres el archivo completo. Cada
dataset tiene un compañero simplificado en

```
data/earth/{ISO3}/preview/{ISO3}_{LEVEL}.preview.geojson
```

— como máximo 2 MB y normalmente unos cientos de KB, coordenadas con cuatro
decimales y solo `shapeName`, `shapeISO` y `shapeType` — servido desde las
mismas URLs que los archivos completos y apto para cargarlo directamente. Las
345 comunas de Chile pesan 425 KB como preview frente a 7 MB completas.

## Git

Para trabajar con los datos localmente o en un pipeline.

El pack del repositorio pesa unos 56 MiB y el working tree unos 309 MB —
166 MB bajo `data/` y casi todo el resto los cuatro archivos heredados de la
raíz. Un clon completo no es enorme, pero un sparse checkout de un solo país es
bastante más pequeño.

=== "Todo"

    ```bash
    git clone https://github.com/andresgmg/World-GeoJSON.git
    ```

=== "Un país (sparse)"

    ```bash
    git clone --filter=blob:none --sparse https://github.com/andresgmg/World-GeoJSON.git
    cd World-GeoJSON
    git sparse-checkout set data/earth/CHL
    ```

    `--filter=blob:none` hace que el clon obtenga el contenido de los archivos
    de forma perezosa, así que solo descargas los blobs de los que realmente
    haces checkout.

=== "Solo metadatos"

    ```bash
    git clone --filter=blob:none --no-checkout https://github.com/andresgmg/World-GeoJSON.git
    cd World-GeoJSON
    git sparse-checkout set --no-cone '/*' '!/data/**' '/data/**/manifest.json'
    git checkout main
    ```

    Obtiene todos los manifiestos sin un solo archivo GeoJSON. Es exactamente
    lo que hace el CI de este sitio — el build de documentación solo lee
    manifiestos.

## Checksums

Cada página del catálogo muestra los primeros 16 caracteres hexadecimales del
SHA-256 del archivo; el hash completo está en el `manifest.json` del país — y
por tanto en `data/index.json` — en `datasets[].sha256` y, para los niveles
partidos, en `parts[].sha256`. Los assets de la release traen un `SHA256SUMS`
que `sha256sum -c SHA256SUMS` comprueba de una vez, y un checkout completo se
verifica con `wgj validate --checksums`, que vuelve a
calcular el hash de cada archivo contra su manifiesto. Verifica una descarga
suelta con:

=== "PowerShell"

    ```powershell
    Get-FileHash .\CHL_ADM1.geojson -Algorithm SHA256
    ```

=== "Bash"

    ```bash
    sha256sum CHL_ADM1.geojson
    ```

!!! warning "Los finales de línea romperán tu checksum"

    Git normaliza los finales de línea al hacer checkout. En Windows, un
    `.geojson` con CRLF es un byte por línea más grande que el mismo archivo en
    Linux — para el `comunas.geojson` heredado de 72 MB, con una coordenada
    por línea, eso son 1,8 MB de diferencia y un hash completamente distinto.

    El `.gitattributes` del repositorio fija `*.geojson` a LF precisamente para
    que los checksums publicados coincidan en todas partes. Si tu hash no
    cuadra, revisa `git config core.autocrlf` antes de suponer que el archivo
    está corrupto.

--8<-- "abbreviations.md"
