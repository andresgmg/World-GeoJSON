# Quick start

Every snippet below loads Chile's 16 regions. Swap the URL for any dataset from
the [Catalog](../catalog/index.md).

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
        "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/regiones.geojson";

      fetch(url)
        .then((r) => r.json())
        .then((data) => {
          const layer = L.geoJSON(data, {
            style: { weight: 1, color: "#00695c", fillOpacity: 0.15 },
            onEachFeature: (f, l) => l.bindTooltip(f.properties.Region),
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
        data: "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/regiones.geojson",
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
        "/main/regiones.geojson"
    )

    regions = gpd.read_file(URL)

    print(len(regions))                    # 16
    print(regions.crs)                     # EPSG:4326
    print(regions["Region"].tolist()[:3])

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
        print(feature["properties"]["Region"])
    ```

    !!! warning "Do not `json.load` a 70 MB file casually"

        `comunas.geojson` will expand to well over a gigabyte of Python
        objects. Use `ijson` to stream it, or GeoPandas, which parses via
        GDAL rather than into Python dicts.

=== "QGIS"

    1. **Layer → Add Layer → Add Vector Layer**
    2. Set **Source Type** to *Protocol: HTTP(S), cloud, etc.*
    3. Paste the raw URL:
       `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/regiones.geojson`
    4. Click **Add**.

    QGIS reads the CRS as EPSG:4326 automatically. To measure areas or
    distances, reproject to a projected CRS appropriate for your area of
    interest first — for Chile, EPSG:5361.

    For the 70 MB communes file, download it locally rather than streaming it
    over HTTP; QGIS will re-request ranges repeatedly otherwise.

=== "R"

    ```r
    library(sf)

    url <- paste0(
      "https://raw.githubusercontent.com/andresgmg/World-GeoJSON",
      "/main/regiones.geojson"
    )

    regions <- st_read(url)

    nrow(regions)        # 16
    st_crs(regions)      # EPSG:4326
    plot(st_geometry(regions))
    ```

## What you get back

A standard `FeatureCollection`. Chile's regions carry these properties today:

```json
{
  "objectid": 1084,
  "cir_sena": 1,
  "codregion": 15,
  "area_km": 16866.81984442,
  "st_area_sh": 18868687743.9,
  "st_length_": 750529.550114,
  "Region": "Región de Arica y Parinacota"
}
```

!!! note "These property names are not final"

    They come straight from the upstream Esri shapefile and are inconsistent —
    three naming styles in one object, plus export artifacts like `st_area_sh`.
    A standardised schema is defined in
    [Property schema](../reference/schema.md) and will be applied as a
    documented breaking change. See
    [Versioning & stability](../about/versioning.md).

--8<-- "abbreviations.md"
