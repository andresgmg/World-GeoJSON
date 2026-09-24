# geoworld

A thin Python client for [World GeoJSON](https://github.com/andresgmg/World-GeoJSON):
open, versioned administrative boundaries (countries, first-level divisions,
municipalities) as GeoJSON.

The library ships no data. It reads `data/index.json` from a pinned data
release, downloads the files you ask for, caches them on disk and verifies
their `sha256` against the index. Zero dependencies.

```bash
pip install geoworld
pip install "geoworld[geopandas]"   # adds to_geopandas()
```

```python
from geoworld import GeoWorld

world = GeoWorld("1.0.0")                     # a data release; the library has its own version

world.countries()                             # every territory: levels, licence, feature counts
world.country("CHL")["terms"]                 # {"adm1": {"en": "Region", "es": "Región"}, …}
world.levels("CHL")                           # ["ADM0", "ADM1", "ADM2", "ADM3"]
world.bbox("CHL", "ADM1")                     # [west, south, east, north] — no download

regions = world.get("CHL", "ADM1")            # a GeoJSON FeatureCollection (dict)
regions["features"][0]["id"]                  # "CHL:ADM1:CL-CO"

world.get_part("USA", "ADM2", "US-CA")        # one part of a split level
for code, counties in world.iter_parts("BRA", "ADM2"):
    ...                                       # levels too big for one file come as parts

world.preview("CHL", "ADM3")                  # simplified (≤ 2 MB) for maps
world.find("CHL:ADM3:01402")                  # one feature by id
world.parent("CHL:ADM3:01402")                # its province
world.children("CHL:ADM1:CL-TA")              # the provinces of Tarapacá
world.search("santiago", "CHL", "ADM3")       # accent- and case-insensitive

world.url("CHL", "ADM1")                      # the file's URL, if you would rather fetch it yourself
world.to_geopandas("CHL", "ADM1")             # with the geopandas extra
```

Every feature has a stable `id` (`{ISO3}:{LEVEL}:{key}`), and every
sub-national feature a `parentID`, so joins and hierarchies work without
string matching on names.

## Where the files come from

By default `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v{version}/`.
Pass `base_url` to read from any static host with the same layout, including a
local checkout or an unzipped release asset:

```python
GeoWorld("1.0.0", base_url="file:///opt/world-geojson")
```

Downloads are cached under the platform cache directory
(`~/.cache/geoworld/<version>/…` on Linux, `~/Library/Caches` on macOS,
`%LOCALAPPDATA%` on Windows; override with `cache_dir=` or `$GEOWORLD_CACHE`).
Cached files are re-hashed on read; a mismatch is refetched.

## Versions

The library's version and the data's version are independent. Each release of
the library declares the data schema it understands
(`geoworld.SUPPORTED_SCHEMA_VERSION`) and a default data release
(`geoworld.DEFAULT_DATA_VERSION`); a newer index raises `UnsupportedSchema`.

## Documentation

- [Library guide](https://andresgmg.github.io/World-GeoJSON/libraries/python/)
- [Data reference](https://andresgmg.github.io/World-GeoJSON/reference/) — properties, levels, the index
- [Licensing](https://andresgmg.github.io/World-GeoJSON/about/license/) — the code is MIT; each dataset carries its own permissive licence, listed in the index

The same API exists for JavaScript and TypeScript as
[`geoworld` on npm](https://www.npmjs.com/package/geoworld).
