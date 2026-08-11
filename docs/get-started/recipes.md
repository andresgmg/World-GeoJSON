# Recipes

Task-shaped snippets. All of them assume you have a dataset URL from the
[Catalog](../catalog/index.md).

## Filter to one region

=== "Python"

    ```python
    import geopandas as gpd

    communes = gpd.read_file("comunas.geojson")

    # codregion 13 is the Santiago Metropolitan Region.
    santiago = communes[communes["codregion"] == 13]
    santiago.to_file("santiago.geojson", driver="GeoJSON")
    ```

=== "mapshaper"

    ```bash
    npx mapshaper comunas.geojson \
      -filter 'codregion === 13' \
      -o santiago.geojson
    ```

=== "jq"

    ```bash
    jq '{type, features: [.features[] | select(.properties.codregion == 13)]}' \
      comunas.geojson > santiago.geojson
    ```

## Simplify for the web

The single most useful thing you can do with this data. Three reductions
compound:

```bash
npx mapshaper comunas.geojson \
  -simplify percentage=2% keep-shapes \
  -filter-fields Comuna,cod_comuna,Region \
  -o precision=0.0001 comunas.min.geojson
```

| Flag | Effect |
|---|---|
| `-simplify percentage=2%` | Visvalingam simplification, keeping 2% of vertices |
| `keep-shapes` | Prevents small islands from vanishing entirely |
| `-filter-fields` | Drops `objectid`, `st_area_sh`, `st_length_` and friends |
| `precision=0.0001` | Rounds coordinates to ~11 m |

Expect roughly 70 MB → 300–800 KB. Always check the result visually: aggressive
simplification creates slivers and can disconnect coastlines.

!!! tip "Why precision alone helps so much"

    The source files store coordinates with about **14 decimal places**
    (`-68.95020116247055`) — nanometre precision for administrative
    boundaries. Six decimals is roughly 11 cm. Everything past that is
    incompressible noise occupying real bytes.

## Convert to TopoJSON

TopoJSON stores shared borders once instead of twice, which matters a lot for
administrative units that tile a country.

```bash
npx mapshaper comunas.geojson -o format=topojson comunas.topojson
```

Reading it back in the browser needs `topojson-client`:

```js
import * as topojson from "topojson-client";

const topo = await fetch("comunas.topojson").then((r) => r.json());
const geojson = topojson.feature(topo, topo.objects.comunas);
```

## Join your own data

The usual reason to want boundaries: you have statistics keyed by an official
code and you want them on a map.

```python
import geopandas as gpd
import pandas as pd

communes = gpd.read_file("comunas.geojson")
stats = pd.read_csv("population.csv")   # columns: cut, population

merged = communes.merge(stats, left_on="cod_comuna", right_on="cut")
```

!!! danger "The leading-zero trap"

    `cod_comuna` is stored as a **number**, so Camiña is `1402`. The official
    INE/SUBDERE code is the five-character string `01402` — regions 1 through 9
    all lose their leading zero this way.

    If your CSV has zero-padded strings, the join silently matches nothing.
    Normalise one side first:

    ```python
    communes["cut"] = communes["cod_comuna"].astype(str).str.zfill(5)
    stats["cut"] = stats["cut"].astype(str).str.zfill(5)
    ```

    This is exactly the class of problem the standardised
    [property schema](../reference/schema.md) exists to eliminate.

## Compute area correctly

```python
import geopandas as gpd

regions = gpd.read_file("regiones.geojson")

# WRONG — degrees are not a unit of area.
regions.area

# RIGHT — reproject to a projected CRS suited to the area of interest.
regions.to_crs(5361).area / 1e6   # km², SIRGAS-Chile / UTM
```

The `area_km` property already present in `regiones.geojson` is precomputed
upstream and can be used directly. Note that `st_area_sh` in the same file is
in **square metres**, not square kilometres — the units are inconsistent
between the two properties and between the two files.

## Merge levels into one file

```bash
npx mapshaper \
  -i regiones.geojson comunas.geojson combine-files \
  -o format=topojson chile.topojson
```

Produces a single TopoJSON with both layers, sharing the coastline arcs.

--8<-- "abbreviations.md"
