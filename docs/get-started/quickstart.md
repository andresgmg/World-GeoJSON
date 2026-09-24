# Quick start

Every snippet below loads Chile's 16 regions from
`data/earth/CHL/CHL_ADM1.geojson`. Swap the URL for any dataset from the
[Catalog](../catalog/index.md) — the property names are the same everywhere.

!!! tip "Tab choice is remembered"

    Picking a language here selects the matching tab on every other page of
    this site.

=== "Leaflet"

    ```html
    <div id="map" style="height: 480px"></div>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <script>
      const map = L.map("map").setView([-35, -71], 4);
      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
      }).addTo(map);

      const url =
        "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/earth/CHL/CHL_ADM1.geojson";

      fetch(url)
        .then((r) => r.json())
        .then((data) => {
          const layer = L.geoJSON(data, {
            style: { weight: 1, color: "#00695c", fillOpacity: 0.15 },
            onEachFeature: (f, l) => l.bindTooltip(f.properties.shapeName),
          }).addTo(map);
          map.fitBounds(layer.getBounds());
        });
    </script>
    ```

=== "MapLibre"

    ```js
    import maplibregl from "maplibre-gl";

    const map = new maplibregl.Map({
      container: "map",
      style: "https://demotiles.maplibre.org/style.json",
      center: [-71, -35],
      zoom: 3,
    });

    map.on("load", () => {
      map.addSource("regions", {
        type: "geojson",
        data: "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/earth/CHL/CHL_ADM1.geojson",
      });

      map.addLayer({
        id: "regions-fill",
        type: "fill",
        source: "regions",
        paint: { "fill-color": "#00695c", "fill-opacity": 0.15 },
      });

      map.addLayer({
        id: "regions-line",
        type: "line",
        source: "regions",
        paint: { "line-color": "#00695c", "line-width": 1 },
      });
    });
    ```

=== "Python"

    ```python
    import geopandas as gpd

    URL = (
        "https://raw.githubusercontent.com/andresgmg/World-GeoJSON"
        "/main/data/earth/CHL/CHL_ADM1.geojson"
    )

    regions = gpd.read_file(URL)

    print(len(regions))                        # 16
    print(regions.crs)                         # EPSG:4326
    print(regions["shapeName"].tolist()[:3])   # ['Coquimbo', 'Ñuble', 'Los Lagos']
    print(regions.set_index("shapeISO").loc["CL-RM", "shapeName"])
    # Metropolitana de Santiago

    # Area needs a projected CRS. Computing it in degrees is meaningless.
    # EPSG:5361 (SIRGAS-Chile) is appropriate for Chile specifically.
    print(regions.to_crs(5361).area / 1e6)  # km²
    ```

    Without GeoPandas, the standard library is enough to inspect the file:

    ```python
    import json
    import urllib.request

    with urllib.request.urlopen(URL) as fh:
        data = json.load(fh)

    for feature in data["features"]:
        p = feature["properties"]
        print(p["shapeISO"], p["shapeName"])
    ```

    !!! warning "Mind `json.load` on big files"

        `json.load` builds a Python object for every coordinate pair. The
        5–15 MB files under `data/` are fine; the legacy 72 MB
        `comunas.geojson` in the repository root is not — it expands to well
        over a gigabyte of Python objects. Use `ijson` to stream it, or
        GeoPandas, which parses via GDAL rather than into Python dicts.

=== "QGIS"

    1. **Layer → Add Layer → Add Vector Layer**
    2. Set **Source Type** to *Protocol: HTTP(S), cloud, etc.*
    3. Paste the raw URL:
       `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/earth/CHL/CHL_ADM1.geojson`
    4. Click **Add**.

    QGIS reads the CRS as EPSG:4326 automatically. To measure areas or
    distances, reproject to a projected CRS appropriate for your area of
    interest first — for Chile, EPSG:5361.

    For the larger files — Canada's ADM1 is 14.9 MB — download locally rather
    than streaming over HTTP; QGIS will re-request ranges repeatedly otherwise.

=== "R"

    ```r
    library(sf)

    url <- paste0(
      "https://raw.githubusercontent.com/andresgmg/World-GeoJSON",
      "/main/data/earth/CHL/CHL_ADM1.geojson"
    )

    regions <- st_read(url)

    nrow(regions)          # 16
    st_crs(regions)        # EPSG:4326
    regions$shapeName[1:3] # "Coquimbo" "Ñuble" "Los Lagos"
    plot(st_geometry(regions))
    ```

## What you get back

A standard `FeatureCollection` with a top-level `bbox`, one feature per line.
Región Metropolitana looks like this:

```json
{
  "shapeName": "Metropolitana de Santiago",
  "shapeISO": "CL-RM",
  "shapeGroup": "CHL",
  "shapeType": "ADM1",
  "parentISO": "CHL",
  "parentID": "CHL:ADM0:CHL",
  "src_cut_reg": "13",
  "src_superficie_km2": 15398.38
}
```

The first four properties are on every feature in the catalog: the name, the
ISO 3166-2 code where one exists (otherwise the official national code, or
`""` where the upstream has none), the country, and the level. `parentISO` and
`parentID` name the parent unit — here the country outline — and features
below an ADM1 also carry `adm1ISO`. Anything prefixed `src_` is carried over
from the upstream source and differs by country — Chile's regions carry their
DPA code and official area, geoBoundaries datasets carry `src_shape_id`. Names
have no "Región de" prefix. The full list is in
[Property schema](../reference/schema.md).

Every feature also has a top-level `id` — `CHL:ADM1:CL-RM` for this one —
that is unique across the whole repository, and every sub-national feature
names its parent's id in `parentID`. Join on `id` rather than on `shapeISO`,
which is empty wherever the upstream has no code. In MapLibre, copy it into a
property before adding the source (`f.properties.id = f.id`) and declare
`promoteId: "id"`, and `setFeatureState` keys on it — GeoJSON sources keep
only integer top-level ids on their own. See
[Property dictionary → The feature `id`](../reference/properties.md#the-feature-id).

!!! tip "Discover the whole catalog in one request"

    `data/index.json` lists every territory and dataset with its path,
    size, checksum, bounding box and licence — see
    [Global index & schemas](../reference/index-json.md).

--8<-- "abbreviations.md"
