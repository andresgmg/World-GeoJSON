# Inicio rápido

Todos los ejemplos cargan las 16 regiones de Chile. Cambia la URL por
cualquier dataset del [Catálogo](../catalog/index.md).

!!! tip "La pestaña elegida se recuerda"

    Elegir un lenguaje aquí selecciona la pestaña equivalente en todas las
    demás páginas del sitio.

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
          const capa = L.geoJSON(data, {
            style: { weight: 1, color: "#00695c", fillOpacity: 0.15 },
            onEachFeature: (f, l) => l.bindTooltip(f.properties.Region),
          }).addTo(map);
          map.fitBounds(capa.getBounds());
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
      map.addSource("regiones", {
        type: "geojson",
        data: "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/regiones.geojson",
      });

      map.addLayer({
        id: "regiones-fill",
        type: "fill",
        source: "regiones",
        paint: { "fill-color": "#00695c", "fill-opacity": 0.15 },
      });

      map.addLayer({
        id: "regiones-line",
        type: "line",
        source: "regiones",
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

    regiones = gpd.read_file(URL)

    print(len(regiones))                    # 16
    print(regiones.crs)                     # EPSG:4326
    print(regiones["Region"].tolist()[:3])

    # El área necesita un CRS proyectado. Calcularla en grados no significa nada.
    # EPSG:5361 (SIRGAS-Chile) es el adecuado para Chile.
    print(regiones.to_crs(5361).area / 1e6)  # km²
    ```

    Sin GeoPandas, la biblioteca estándar basta para inspeccionar el archivo:

    ```python
    import json
    import urllib.request

    with urllib.request.urlopen(URL) as fh:
        data = json.load(fh)

    for feature in data["features"]:
        print(feature["properties"]["Region"])
    ```

    !!! warning "No hagas `json.load` de un archivo de 70 MB a la ligera"

        `comunas.geojson` se expande a bastante más de un gigabyte de objetos
        Python. Usa `ijson` para streamearlo, o GeoPandas, que parsea con GDAL
        en vez de construir diccionarios de Python.

=== "QGIS"

    1. **Capa → Añadir capa → Añadir capa vectorial**
    2. En **Tipo de origen** elige *Protocolo: HTTP(S), nube, etc.*
    3. Pega la URL raw:
       `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/regiones.geojson`
    4. Pulsa **Añadir**.

    QGIS detecta el CRS como EPSG:4326 automáticamente. Para medir áreas o
    distancias, reproyecta primero a un CRS proyectado adecuado a tu zona de
    interés — para Chile, EPSG:5361.

    Para el archivo de comunas de 70 MB, descárgalo localmente en vez de
    consumirlo por HTTP; si no, QGIS repetirá peticiones por rangos.

=== "R"

    ```r
    library(sf)

    url <- paste0(
      "https://raw.githubusercontent.com/andresgmg/World-GeoJSON",
      "/main/regiones.geojson"
    )

    regiones <- st_read(url)

    nrow(regiones)        # 16
    st_crs(regiones)      # EPSG:4326
    plot(st_geometry(regiones))
    ```

## Qué recibes

Un `FeatureCollection` estándar. Las regiones de Chile llevan hoy estas
propiedades:

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

!!! note "Estos nombres de propiedades no son definitivos"

    Vienen directamente del shapefile Esri de origen y son inconsistentes:
    tres estilos de nomenclatura en un mismo objeto, más artefactos de
    exportación como `st_area_sh`. El esquema estandarizado está definido en
    [Esquema de propiedades](../reference/schema.md) y se aplicará como un
    cambio rompedor documentado. Ver
    [Versionado y estabilidad](../about/versioning.md).

--8<-- "abbreviations.md"
