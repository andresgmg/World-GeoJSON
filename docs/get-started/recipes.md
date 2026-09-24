# Recipes

Task-shaped snippets. All of them assume you have downloaded a dataset from
the [Catalog](../catalog/index.md); the examples use Chile's
`CHL_ADM1.geojson` (16 regions) and `CHL_ADM3.geojson` (345 communes).

## Filter to one region

Chile's communes carry `adm1ISO`, the ISO 3166-2 code of their region —
`CL-RM` is Región Metropolitana.

=== "Python"

    ```python
    import geopandas as gpd

    communes = gpd.read_file("CHL_ADM3.geojson")

    santiago = communes[communes["adm1ISO"] == "CL-RM"]
    santiago.to_file("santiago.geojson", driver="GeoJSON")   # 52 features
    ```

=== "mapshaper"

    ```bash
    npx mapshaper CHL_ADM3.geojson \
      -filter 'adm1ISO === "CL-RM"' \
      -o santiago.geojson
    ```

=== "jq"

    ```bash
    jq '{type, features: [.features[] | select(.properties.adm1ISO == "CL-RM")]}' \
      CHL_ADM3.geojson > santiago.geojson
    ```

!!! tip "Split levels are already filtered for you"

    Municipal tiers that have an ADM1 to split by ship one file per region
    alongside the combined file — for Chile,
    `data/earth/CHL/ADM3/CL-RM.geojson` is exactly the output above. Those
    part files carry `adm1ISO` in every country; the combined file carries
    it only for Chile today. v1.0.0 adds it everywhere.

## Simplify for the web

The single most useful thing you can do with this data. Three reductions
compound:

```bash
npx mapshaper CHL_ADM3.geojson \
  -simplify percentage=5% keep-shapes \
  -filter-fields shapeName,shapeISO,shapeType \
  -o precision=0.0001 comunas.min.geojson
```

| Flag | Effect |
|---|---|
| `-simplify percentage=5%` | Visvalingam simplification, keeping 5% of vertices |
| `keep-shapes` | Prevents small islands from vanishing entirely |
| `-filter-fields` | Drops the `src_*` source attributes the map does not need |
| `precision=0.0001` | Rounds coordinates to ~11 m |

Expect roughly 7 MB → a few hundred KB. Always check the result visually:
aggressive simplification creates slivers and can disconnect coastlines.

This is exactly how the committed previews are built — halving the percentage
until the file is under 800 KB — so before doing it yourself, check whether
`data/earth/{ISO3}/preview/{ISO3}_{LEVEL}.preview.geojson` is already what
you need. See [Simplification & previews](../contributing/previews.md).

!!! tip "Why precision alone helps so much"

    Files under `data/` are already trimmed to six decimals, roughly 11 cm.
    Four decimals (~11 m) is plenty for a map, and dropping the extra digits
    is free compression. The legacy root files, by contrast, store about
    **14 decimal places** (`-68.95020116247055`) — nanometre precision for
    administrative boundaries, all of it incompressible noise occupying real
    bytes.

## Convert to TopoJSON

TopoJSON stores shared borders once instead of twice, which matters a lot for
administrative units that tile a country.

```bash
npx mapshaper CHL_ADM3.geojson -o format=topojson CHL_ADM3.topojson
```

Reading it back in the browser needs `topojson-client`. The object is named
after the input file:

```js
import * as topojson from "topojson-client";

const topo = await fetch("CHL_ADM3.topojson").then((r) => r.json());
const geojson = topojson.feature(topo, topo.objects.CHL_ADM3);
```

## Join your own data

The usual reason to want boundaries: you have statistics keyed by an official
code and you want them on a map. For Chilean communes `shapeISO` is the
five-character CUT code — Camiña is `"01402"`.

```python
import geopandas as gpd
import pandas as pd

communes = gpd.read_file("CHL_ADM3.geojson")
stats = pd.read_csv("population.csv", dtype={"cut": str})   # columns: cut, population

merged = communes.merge(stats, left_on="shapeISO", right_on="cut")
```

!!! danger "The leading-zero trap"

    `shapeISO` is always a **string**, so the leading zero survives. The
    other side of the join is where it gets lost: `pd.read_csv` reads `01402`
    as the integer `1402` unless you pass `dtype={"cut": str}`, and then the
    join silently matches nothing. If your CSV already lost the zeros, put
    them back:

    ```python
    stats["cut"] = stats["cut"].astype(str).str.zfill(5)
    ```

    The same commune also carries its province in `parentISO` (`"014"`,
    Tamarugal) and its region in `adm1ISO` (`"CL-TA"`), so a join at any of
    the three levels needs no lookup table.

!!! warning "Check `shapeISO` before relying on it"

    On 22 municipal datasets from geoBoundaries, `shapeISO` holds the
    upstream's opaque id (something like `66186276B69138566591314`) rather
    than an official code, and it is not unique in Belize ADM2, Mexico ADM1
    and Ecuador ADM1. Look at the values on the catalog page first. A stable
    Feature `id` on every feature is planned for v1.0.0 — see
    [Roadmap](../about/roadmap.md).

## Compute area correctly

```python
import geopandas as gpd

regions = gpd.read_file("CHL_ADM1.geojson")

# WRONG — degrees are not a unit of area.
regions.area

# RIGHT — reproject to a projected CRS suited to the area of interest.
regions.to_crs(5361).area / 1e6   # km², SIRGAS-Chile / UTM
```

Chile's regions also carry `src_superficie_km2`, the official area from the
DPA package in square kilometres — the one numeric property in the catalog.
Prefer it where it exists: the geometry here is simplified to a 100 m
tolerance, so an area computed from it will not match the official figure
exactly.

## Merge levels into one file

```bash
npx mapshaper \
  -i CHL_ADM1.geojson CHL_ADM3.geojson combine-files \
  -o format=topojson chile.topojson
```

Produces a single TopoJSON with both layers, sharing the coastline arcs.

--8<-- "abbreviations.md"
