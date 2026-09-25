# Client libraries

Two thin clients, one API, one name: **`geoworld`** on
[PyPI](https://pypi.org/project/geoworld/) and on
[npm](https://www.npmjs.com/package/geoworld). They ship no data. Each reads
`data/index.json` from a pinned [data release](../about/versioning.md),
downloads the files you ask for, caches them and verifies their `sha256`
against the index.

=== "Python"

    ```bash
    pip install geoworld
    ```

    ```python
    from geoworld import GeoWorld

    world = GeoWorld("1.0.0")
    regions = world.get("CHL", "ADM1")        # a GeoJSON FeatureCollection (dict)
    regions["features"][0]["id"]              # "CHL:ADM1:CL-CO"
    ```

=== "JavaScript / TypeScript"

    ```bash
    npm install geoworld
    ```

    ```ts
    import { createClient } from "geoworld";

    const world = createClient({ version: "1.0.0" });
    const regions = await world.get("CHL", "ADM1");   // a GeoJSON FeatureCollection
    regions.features[0].id;                           // "CHL:ADM1:CL-CO"
    ```

Both are documented in full on their own pages: [Python](python.md) and
[JavaScript](javascript.md). Three adapters put the JavaScript client on a
map or in a component tree: [MapLibre](maplibre.md), [Leaflet](leaflet.md)
and [React](react.md).

| Package | What it is | Runtime deps |
|---|---|---|
| `geoworld` (PyPI) | Python client | none |
| `geoworld` (npm) | JavaScript/TypeScript client | none |
| `geoworld-maplibre` | `addBoundaries`, feature state by stable id, `fitToBounds` | none (`maplibre-gl` peer) |
| `geoworld-leaflet` | `withLeaflet(L).addBoundaries`, `layerById`, `toLatLngBounds` | none (`leaflet` optional peer) |
| `geoworld-react` | `GeoWorldProvider`, `useBoundaries`, `useCountry`, `useChildren`, … | none (`react` peer) |

## What they do — and do not do

- **Read the index once.** `data/index.json` lists every territory, level,
  file, size, checksum and licence. `countries()`, `levels()`, `bbox()` and
  `url()` answer from it without downloading any GeoJSON.
- **Download on demand.** `get()` fetches one level of one territory. Levels
  too big for a single file (Brazil's municipalities) come as parts, one per
  first-level division: `get_part()` / `getPart()` and `iter_parts()` /
  `iterParts()`.
- **Cache.** Python writes to the platform cache directory; JavaScript keeps
  files in memory and, in Node, can persist them with `geoworld/node`. The
  layout is the same, `geoworld/<version>/<path>`, so the two can share a
  directory.
- **Verify.** Every full-resolution file is hashed after download and every
  cached read is re-hashed; a mismatch is an error, never silently used.
- **Navigate.** Every feature has a stable `id` and every sub-national feature
  a `parentID`, so `find()`, `parent()`, `children()` and `search()` work
  across levels without matching on names.
- **Nothing server-side.** The libraries talk to static files —
  `raw.githubusercontent.com` at the release tag by default, or any host you
  point `base_url` / `baseUrl` at, including a local directory or an unzipped
  [release asset](../get-started/download.md).

They are not a GIS: no reprojection, no geometry operations, no rendering.
Hand the FeatureCollection to GeoPandas, Leaflet, MapLibre or whatever you
already use. (`to_geopandas()` exists in Python as a convenience.)

## The same API in both

| Python | JavaScript | Returns |
|---|---|---|
| `GeoWorld(version, base_url=, cache_dir=, cache=, verify=)` | `createClient({ version, baseUrl, cache, fetch, verify })` | a client |
| `index()` | `index()` | the whole `index.json` |
| `countries()` | `countries()` | one summary per territory |
| `country(iso3)` | `country(iso3)` | the full index entry |
| `levels(iso3)` | `levels(iso3)` | `["ADM0", "ADM1", …]` |
| `dataset(iso3, level)` | `dataset(iso3, level)` | the index entry of one level |
| `bbox(iso3, level)` | `bbox(iso3, level)` | `[west, south, east, north]` |
| `parts(iso3, level)` | `parts(iso3, level)` | part codes of a split level |
| `url(iso3, level, part=, preview=)` | `url(iso3, level, { part, preview })` | the file's URL |
| `get(iso3, level)` | `get(iso3, level)` | FeatureCollection |
| `get_part(iso3, level, code)` | `getPart(iso3, level, code)` | FeatureCollection |
| `iter_parts(iso3, level)` | `iterParts(iso3, level)` | `(code, FeatureCollection)` pairs |
| `features(iso3, level)` | `features(iso3, level)` | every feature, across parts if needed |
| `preview(iso3, level)` | `preview(iso3, level)` | the simplified FeatureCollection |
| `find(id)` | `find(id)` | one Feature |
| `parent(id)` | `parent(id)` | the parent Feature, or none |
| `children(id)` | `children(id)` | Features of the next level |
| `search(text, iso3, level=)` | `search(text, iso3, level?)` | matching Features |
| `clear_cache()` | `clearCache()` | — |
| `to_geopandas(iso3, level)` | — | a GeoDataFrame |

Everything in JavaScript is `async`. Errors are typed the same way on both
sides (`UnknownCountry`, `UnknownLevel`, `NoCombinedFile`, `ChecksumMismatch`,
`UnsupportedSchema`, …) and all extend `GeoWorldError`.

Both clients are tested against the same fixtures and must produce the same
`fixtures/expected/fixtures.json` byte for byte, so what one computes the other
computes too.

## Versions

The libraries' versions and the data's versions are independent
([why](../about/versioning.md#library-versioning)). Each library release
declares the data `schema_version` it understands and a default data release:

| | Library | Default data | Supports schema |
|---|---|---|---|
| Python | `geoworld` 0.1.0 | `1.0.0` | 1 |
| JavaScript | `geoworld` 0.2.0, and the three adapters at the same version | `1.0.0` | 1 |

The JavaScript packages move in lockstep: one version number, one tag, and
each adapter declares `geoworld` as a peer at that minor.

Pin the data version you tested against. `version="main"` works for
experiments but warns: the branch moves, and nothing is cached on disk.

## Releasing

Maintainers publish from tags: `python-vX.Y.Z` runs `publish-python.yml`
(PyPI, trusted publishing) and `js-vX.Y.Z` runs `publish-js.yml`, which
publishes `geoworld` and then the three adapters with provenance, skipping
any of them already on the registry at that version. Both workflows refuse a
tag that does not match the versions in the packages.

--8<-- "abbreviations.md"
