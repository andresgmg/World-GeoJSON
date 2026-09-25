# Python client

`geoworld` on [PyPI](https://pypi.org/project/geoworld/). Python ≥ 3.11, zero
dependencies; the source lives in
[`packages/python/geoworld`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/python/geoworld).

```bash
pip install geoworld
pip install "geoworld[geopandas]"   # adds to_geopandas()
```

## Constructing a client

```python
from geoworld import GeoWorld

world = GeoWorld("1.0.0")
```

| Argument | Default | Meaning |
|---|---|---|
| `version` | `"1.0.0"` (`geoworld.DEFAULT_DATA_VERSION`) | A data release tag without the `v`, or `"main"` |
| `base_url` | `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v{version}` | Any static host with the repository layout, including `file:///…` |
| `cache_dir` | platform cache dir (see below) | Where files are stored, as `<cache_dir>/<version>/<path>` |
| `cache` | `True` | `False` keeps files in memory only |
| `verify` | `True` | Hash every download and cached read against the index |
| `timeout` | `30.0` | Seconds per request |

Passing `version="main"` follows the branch: it warns and disables the disk
cache, because a cached `main` would be stale within days.

The default cache directory is `$GEOWORLD_CACHE` if set, else
`%LOCALAPPDATA%\geoworld` on Windows, `~/Library/Caches/geoworld` on macOS and
`$XDG_CACHE_HOME/geoworld` (`~/.cache/geoworld`) elsewhere.
`world.cache_dir` tells you where this client writes; `world.clear_cache()`
empties it for this data version.

## Reading the index

None of these download GeoJSON; they answer from `data/index.json`, fetched
once per client.

```python
world.index()                    # the whole index (dict), schema_version, totals, countries
world.countries()                # [{"iso_a3": "ABW", "name": {…}, "levels": [...], "features": 1, …}, …]
world.country("CHL")             # the full entry: source, licence, terms, datasets
world.levels("CHL")              # ["ADM0", "ADM1", "ADM2", "ADM3"]
world.dataset("CHL", "ADM3")     # the level's entry: path, bytes, sha256, bbox, license, …
world.bbox("CHL", "ADM3")        # [-109.449861, -56.525107, -66.416176, -17.498399]
world.parts("USA", "ADM2")       # ["US-AK", "US-AL", …, "unassigned"]
world.url("CHL", "ADM1")         # ".../v1.0.0/data/earth/CHL/CHL_ADM1.geojson"
world.url("USA", "ADM2", "US-CA")
world.url("CHL", "ADM3", preview=True)
```

`country()["terms"]` holds what the tiers are called locally
(`{"adm1": {"en": "Region", "es": "Región"}, …}`), when the registry knows.

## Reading files

```python
fc = world.get("CHL", "ADM1")            # FeatureCollection (dict), verified, cached
fc["features"][0]["id"]                  # "CHL:ADM1:CL-CO"
fc["features"][0]["properties"]          # shapeName, shapeISO, shapeGroup, shapeType, parentID, …

world.get_part("USA", "ADM2", "US-CA")   # one part of a split level
for code, fc in world.iter_parts("BRA", "ADM2"):
    ...                                  # every part, in index order

for feature in world.features("BRA", "ADM2"):
    ...                                  # every feature, from the file or across parts

world.preview("CHL", "ADM3")             # simplified, ≤ 2 MB; only shapeName, shapeISO, shapeType
```

A level published as parts only (Brazil's ADM2, 33 MB combined) raises
`NoCombinedFile` from `get()`; use `iter_parts()` or `features()`.

Returned objects are plain dicts, cached in memory and shared between calls:
copy before mutating.

## Navigating

Every feature has a stable `id` (`{ISO3}:{LEVEL}:{key}`) and every
sub-national feature a `parentID`; see
[Property dictionary](../reference/properties.md).

```python
world.find("CHL:ADM3:01402")             # one feature; loads only the part it lives in when it can
world.parent("CHL:ADM3:01402")           # the province (Feature), or None at ADM0
world.children("CHL:ADM1:CL-TA")         # the provinces of Tarapacá
world.search("santiago", "CHL", "ADM3")  # accent- and case-insensitive on shapeName; exact on shapeISO
world.search("valpar", "CHL")            # all levels of the territory
```

`children()` uses the next *published* level: for a territory without ADM1
(Puerto Rico), the children of ADM0 are its ADM2 units.

## GeoPandas

```python
gdf = world.to_geopandas("CHL", "ADM1")            # GeoDataFrame, EPSG:4326, `id` as the first column
gdf = world.to_geopandas("USA", "ADM2", part="US-CA")
```

Needs `pip install "geoworld[geopandas]"`. A parts-only level is
concatenated unless `part` is given.

## Errors

All inherit from `geoworld.GeoWorldError`:

| Error | When |
|---|---|
| `UnknownCountry`, `UnknownLevel`, `UnknownPart`, `UnknownFeature` | Not in this data version (`KeyError` subclasses) |
| `InvalidFeatureId` | Not a `{ISO3}:{LEVEL}:{key}` string (`ValueError` subclass) |
| `NotSplit` | Parts asked of a single-file level |
| `NoCombinedFile` | `get()` on a parts-only level |
| `NoPreview` | The level has no preview |
| `DownloadError` | Network or HTTP failure; `.status` carries the code |
| `ChecksumMismatch` | The bytes do not hash to the index's `sha256` |
| `UnsupportedSchema` | The index is newer than `geoworld.SUPPORTED_SCHEMA_VERSION` |

## Offline and mirrors

Any directory with the repository layout works as a source: a checkout, or
an unzipped `world-geojson-v1.0.0-all.zip` from the
[release assets](../get-started/download.md).

```python
GeoWorld("1.0.0", base_url="file:///opt/world-geojson")
GeoWorld("1.0.0", base_url="https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0")
```

The `version` names the cache namespace; keep it equal to what the mirror
holds.

## Types

`geoworld.types` declares `TypedDict`s for the index (`Index`, `Country`,
`Dataset`, `Part`), the summaries (`CountrySummary`) and GeoJSON (`Feature`,
`FeatureCollection`), written from the
[JSON Schemas](../reference/index-json.md#schemas). The package ships
`py.typed`.

--8<-- "abbreviations.md"
