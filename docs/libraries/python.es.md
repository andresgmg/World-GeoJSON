# Cliente Python

`geoworld` en [PyPI](https://pypi.org/project/geoworld/). Python ≥ 3.11, cero
dependencias; el código vive en
[`packages/python/geoworld`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/python/geoworld).

```bash
pip install geoworld
pip install "geoworld[geopandas]"   # añade to_geopandas()
```

## Construir un cliente

```python
from geoworld import GeoWorld

world = GeoWorld("1.0.0")
```

| Argumento | Por defecto | Significado |
|---|---|---|
| `version` | `"1.0.0"` (`geoworld.DEFAULT_DATA_VERSION`) | Una etiqueta de release de datos sin la `v`, o `"main"` |
| `base_url` | `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v{version}` | Cualquier host estático con la disposición del repositorio, incluido `file:///…` |
| `cache_dir` | directorio de caché de la plataforma (abajo) | Dónde se guardan los archivos, como `<cache_dir>/<versión>/<ruta>` |
| `cache` | `True` | `False` mantiene los archivos solo en memoria |
| `verify` | `True` | Hashea cada descarga y cada lectura de caché contra el índice |
| `timeout` | `30.0` | Segundos por petición |

Pasar `version="main"` sigue la rama: avisa y desactiva la caché en disco,
porque un `main` cacheado quedaría obsoleto en días.

El directorio de caché por defecto es `$GEOWORLD_CACHE` si está definido; si
no, `%LOCALAPPDATA%\geoworld` en Windows, `~/Library/Caches/geoworld` en macOS
y `$XDG_CACHE_HOME/geoworld` (`~/.cache/geoworld`) en el resto.
`world.cache_dir` dice dónde escribe este cliente; `world.clear_cache()` lo
vacía para esta versión de datos.

## Leer el índice

Ninguno de estos descarga GeoJSON; responden desde `data/index.json`, leído
una vez por cliente.

```python
world.index()                    # todo el índice (dict): schema_version, totals, countries
world.countries()                # [{"iso_a3": "ABW", "name": {…}, "levels": [...], "features": 1, …}, …]
world.country("CHL")             # la entrada completa: fuente, licencia, términos, datasets
world.levels("CHL")              # ["ADM0", "ADM1", "ADM2", "ADM3"]
world.dataset("CHL", "ADM3")     # la entrada del nivel: path, bytes, sha256, bbox, license, …
world.bbox("CHL", "ADM3")        # [-109.449861, -56.525107, -66.416176, -17.498399]
world.parts("USA", "ADM2")       # ["US-AK", "US-AL", …, "unassigned"]
world.url("CHL", "ADM1")         # ".../v1.0.0/data/earth/CHL/CHL_ADM1.geojson"
world.url("USA", "ADM2", "US-CA")
world.url("CHL", "ADM3", preview=True)
```

`country()["terms"]` guarda cómo se llaman los niveles localmente
(`{"adm1": {"en": "Region", "es": "Región"}, …}`), cuando el registro lo sabe.

## Leer archivos

```python
fc = world.get("CHL", "ADM1")            # FeatureCollection (dict), verificada, cacheada
fc["features"][0]["id"]                  # "CHL:ADM1:CL-CO"
fc["features"][0]["properties"]          # shapeName, shapeISO, shapeGroup, shapeType, parentID, …

world.get_part("USA", "ADM2", "US-CA")   # una parte de un nivel dividido
for code, fc in world.iter_parts("BRA", "ADM2"):
    ...                                  # cada parte, en el orden del índice

for feature in world.features("BRA", "ADM2"):
    ...                                  # cada feature, del archivo o a través de las partes

world.preview("CHL", "ADM3")             # simplificado, ≤ 2 MB; solo shapeName, shapeISO, shapeType
```

Un nivel publicado solo en partes (el ADM2 de Brasil, 33 MB combinado) lanza
`NoCombinedFile` desde `get()`; usa `iter_parts()` o `features()`.

Los objetos devueltos son dicts normales, cacheados en memoria y compartidos
entre llamadas: copia antes de modificar.

## Navegar

Cada feature tiene un `id` estable (`{ISO3}:{NIVEL}:{clave}`) y cada feature
subnacional un `parentID`; ver
[Diccionario de propiedades](../reference/properties.md).

```python
world.find("CHL:ADM3:01402")             # una feature; carga solo la parte donde vive cuando puede
world.parent("CHL:ADM3:01402")           # la provincia (Feature), o None en ADM0
world.children("CHL:ADM1:CL-TA")         # las provincias de Tarapacá
world.search("santiago", "CHL", "ADM3")  # sin distinguir acentos ni mayúsculas en shapeName; exacto en shapeISO
world.search("valpar", "CHL")            # todos los niveles del territorio
```

`children()` usa el siguiente nivel *publicado*: para un territorio sin ADM1
(Puerto Rico), los hijos del ADM0 son sus unidades ADM2.

## GeoPandas

```python
gdf = world.to_geopandas("CHL", "ADM1")            # GeoDataFrame, EPSG:4326, `id` como primera columna
gdf = world.to_geopandas("USA", "ADM2", part="US-CA")
```

Necesita `pip install "geoworld[geopandas]"`. Un nivel solo en partes se
concatena salvo que se indique `part`.

## Errores

Todos heredan de `geoworld.GeoWorldError`:

| Error | Cuándo |
|---|---|
| `UnknownCountry`, `UnknownLevel`, `UnknownPart`, `UnknownFeature` | No está en esta versión de datos (subclases de `KeyError`) |
| `InvalidFeatureId` | No es una cadena `{ISO3}:{NIVEL}:{clave}` (subclase de `ValueError`) |
| `NotSplit` | Se pidieron partes de un nivel de un solo archivo |
| `NoCombinedFile` | `get()` sobre un nivel solo en partes |
| `NoPreview` | El nivel no tiene preview |
| `DownloadError` | Fallo de red o HTTP; `.status` lleva el código |
| `ChecksumMismatch` | Los bytes no hashean al `sha256` del índice |
| `UnsupportedSchema` | El índice es más nuevo que `geoworld.SUPPORTED_SCHEMA_VERSION` |

## Sin conexión y espejos

Cualquier directorio con la disposición del repositorio sirve como fuente: un
checkout, o un `world-geojson-v1.0.0-all.zip` descomprimido de los
[assets de la release](../get-started/download.md).

```python
GeoWorld("1.0.0", base_url="file:///opt/world-geojson")
GeoWorld("1.0.0", base_url="https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0")
```

La `version` nombra el espacio de caché; mantenla igual a lo que contiene el
espejo.

## Tipos

`geoworld.types` declara `TypedDict`s para el índice (`Index`, `Country`,
`Dataset`, `Part`), los resúmenes (`CountrySummary`) y GeoJSON (`Feature`,
`FeatureCollection`), escritos a partir de los
[JSON Schemas](../reference/index-json.md#esquemas). El paquete incluye
`py.typed`.

--8<-- "abbreviations.md"
