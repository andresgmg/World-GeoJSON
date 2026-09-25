# Bibliotecas cliente

Dos clientes ligeros, una API, un nombre: **`geoworld`** en
[PyPI](https://pypi.org/project/geoworld/) y en
[npm](https://www.npmjs.com/package/geoworld). No incluyen datos. Cada uno lee
`data/index.json` de una [release de datos](../about/versioning.md) fijada,
descarga los archivos que pides, los cachea y verifica su `sha256` contra el
índice.

=== "Python"

    ```bash
    pip install geoworld
    ```

    ```python
    from geoworld import GeoWorld

    world = GeoWorld("1.0.0")
    regions = world.get("CHL", "ADM1")        # una FeatureCollection GeoJSON (dict)
    regions["features"][0]["id"]              # "CHL:ADM1:CL-CO"
    ```

=== "JavaScript / TypeScript"

    ```bash
    npm install geoworld
    ```

    ```ts
    import { createClient } from "geoworld";

    const world = createClient({ version: "1.0.0" });
    const regions = await world.get("CHL", "ADM1");   // una FeatureCollection GeoJSON
    regions.features[0].id;                           // "CHL:ADM1:CL-CO"
    ```

Cada uno tiene su página completa: [Python](python.md) y
[JavaScript](javascript.md). Tres adaptadores ponen el cliente JavaScript en
un mapa o en un árbol de componentes: [MapLibre](maplibre.md),
[Leaflet](leaflet.md) y [React](react.md).

| Paquete | Qué es | Deps en runtime |
|---|---|---|
| `geoworld` (PyPI) | Cliente Python | ninguna |
| `geoworld` (npm) | Cliente JavaScript/TypeScript | ninguna |
| `geoworld-maplibre` | `addBoundaries`, feature state por id estable, `fitToBounds` | ninguna (peer `maplibre-gl`) |
| `geoworld-leaflet` | `withLeaflet(L).addBoundaries`, `layerById`, `toLatLngBounds` | ninguna (peer opcional `leaflet`) |
| `geoworld-react` | `GeoWorldProvider`, `useBoundaries`, `useCountry`, `useChildren`, … | ninguna (peer `react`) |

## Qué hacen — y qué no

- **Leen el índice una vez.** `data/index.json` lista cada territorio, nivel,
  archivo, tamaño, checksum y licencia. `countries()`, `levels()`, `bbox()` y
  `url()` responden desde él sin descargar ningún GeoJSON.
- **Descargan bajo demanda.** `get()` trae un nivel de un territorio. Los
  niveles demasiado grandes para un solo archivo (los municipios de Brasil)
  vienen en partes, una por división de primer nivel: `get_part()` /
  `getPart()` e `iter_parts()` / `iterParts()`.
- **Cachean.** Python escribe en el directorio de caché de la plataforma;
  JavaScript guarda los archivos en memoria y, en Node, puede persistirlos con
  `geoworld/node`. La disposición es la misma, `geoworld/<versión>/<ruta>`,
  así que ambos pueden compartir un directorio.
- **Verifican.** Cada archivo de resolución completa se hashea tras
  descargarlo y cada lectura de caché se vuelve a hashear; una discrepancia es
  un error, nunca se usa en silencio.
- **Navegan.** Cada feature tiene un `id` estable y cada feature subnacional
  un `parentID`, así que `find()`, `parent()`, `children()` y `search()`
  funcionan entre niveles sin comparar nombres.
- **Nada del lado del servidor.** Las bibliotecas hablan con archivos
  estáticos — `raw.githubusercontent.com` en la etiqueta de la release por
  defecto, o cualquier host que indiques en `base_url` / `baseUrl`, incluido un
  directorio local o un [asset de release](../get-started/download.md)
  descomprimido.

No son un SIG: sin reproyección, sin operaciones geométricas, sin render.
Pásale la FeatureCollection a GeoPandas, Leaflet, MapLibre o lo que ya uses.
(`to_geopandas()` existe en Python por comodidad.)

## La misma API en ambos

| Python | JavaScript | Devuelve |
|---|---|---|
| `GeoWorld(version, base_url=, cache_dir=, cache=, verify=)` | `createClient({ version, baseUrl, cache, fetch, verify })` | un cliente |
| `index()` | `index()` | todo el `index.json` |
| `countries()` | `countries()` | un resumen por territorio |
| `country(iso3)` | `country(iso3)` | la entrada completa del índice |
| `levels(iso3)` | `levels(iso3)` | `["ADM0", "ADM1", …]` |
| `dataset(iso3, level)` | `dataset(iso3, level)` | la entrada de un nivel |
| `bbox(iso3, level)` | `bbox(iso3, level)` | `[oeste, sur, este, norte]` |
| `parts(iso3, level)` | `parts(iso3, level)` | códigos de parte de un nivel dividido |
| `url(iso3, level, part=, preview=)` | `url(iso3, level, { part, preview })` | la URL del archivo |
| `get(iso3, level)` | `get(iso3, level)` | FeatureCollection |
| `get_part(iso3, level, code)` | `getPart(iso3, level, code)` | FeatureCollection |
| `iter_parts(iso3, level)` | `iterParts(iso3, level)` | pares `(código, FeatureCollection)` |
| `features(iso3, level)` | `features(iso3, level)` | cada feature, a través de las partes si hace falta |
| `preview(iso3, level)` | `preview(iso3, level)` | la FeatureCollection simplificada |
| `find(id)` | `find(id)` | una Feature |
| `parent(id)` | `parent(id)` | la Feature padre, o ninguna |
| `children(id)` | `children(id)` | Features del siguiente nivel |
| `search(text, iso3, level=)` | `search(text, iso3, level?)` | Features que coinciden |
| `clear_cache()` | `clearCache()` | — |
| `to_geopandas(iso3, level)` | — | un GeoDataFrame |

En JavaScript todo es `async`. Los errores están tipados igual en ambos lados
(`UnknownCountry`, `UnknownLevel`, `NoCombinedFile`, `ChecksumMismatch`,
`UnsupportedSchema`, …) y todos extienden `GeoWorldError`.

Ambos clientes se prueban contra los mismos fixtures y deben producir el mismo
`fixtures/expected/fixtures.json` byte a byte, así que lo que uno calcula lo
calcula el otro.

## Versiones

Las versiones de las bibliotecas y las de los datos son independientes
([por qué](../about/versioning.md#versionado-de-las-bibliotecas)). Cada
release de biblioteca declara el `schema_version` de datos que entiende y una
release de datos por defecto:

| | Biblioteca | Datos por defecto | Soporta esquema |
|---|---|---|---|
| Python | `geoworld` 0.1.0 | `1.0.0` | 1 |
| JavaScript | `geoworld` 0.2.0, y los tres adaptadores en la misma versión | `1.0.0` | 1 |

Los paquetes JavaScript avanzan en bloque: un número de versión, una etiqueta,
y cada adaptador declara `geoworld` como peer en esa menor.

Fija la versión de datos contra la que probaste. `version="main"` sirve para
experimentar pero avisa: la rama se mueve y nada se cachea en disco.

## Publicación

Los mantenedores publican desde etiquetas: `python-vX.Y.Z` ejecuta
`publish-python.yml` (PyPI, trusted publishing) y `js-vX.Y.Z` ejecuta
`publish-js.yml`, que publica `geoworld` y luego los tres adaptadores con
procedencia, saltando los que ya estén en el registro con esa versión. Ambos
workflows rechazan una etiqueta que no coincida con las versiones de los
paquetes.

--8<-- "abbreviations.md"
