# Inicio rápido

Todos los ejemplos cargan las 16 regiones de Chile desde
`data/earth/CHL/CHL_ADM1.geojson`. Cambia la URL por cualquier dataset del
[Catálogo](../catalog/index.md) — los nombres de las propiedades son los mismos
en todos.

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
        "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/earth/CHL/CHL_ADM1.geojson";

      fetch(url)
        .then((r) => r.json())
        .then((data) => {
          const capa = L.geoJSON(data, {
            style: { weight: 1, color: "#00695c", fillOpacity: 0.15 },
            onEachFeature: (f, l) => l.bindTooltip(f.properties.shapeName),
          }).addTo(map);
          map.fitBounds(capa.getBounds());
        });
    </script>
    ```

    O con el [adaptador Leaflet](../libraries/leaflet.md), fijado a una
    release de datos, verificado y encuadrado desde el índice:

    ```js
    import { createClient } from "geoworld";
    import { withLeaflet } from "geoworld-leaflet";

    const world = createClient({ version: "1.0.0" });
    await withLeaflet(L).addBoundaries(map, world, "CHL", "ADM1", {
      fit: true,
      onEachFeature: (f, l) => l.bindTooltip(f.properties.shapeName),
    });
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
        data: "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/earth/CHL/CHL_ADM1.geojson",
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

    O con el [adaptador MapLibre](../libraries/maplibre.md), que además hace
    utilizable el `id` estable de cada feature en `feature-state`:

    ```js
    import { createClient } from "geoworld";
    import { addBoundaries } from "geoworld-maplibre";

    const world = createClient({ version: "1.0.0" });
    const regiones = await addBoundaries(map, world, "CHL", "ADM1", { fit: true });
    ```

=== "Python"

    ```python
    import geopandas as gpd

    URL = (
        "https://raw.githubusercontent.com/andresgmg/World-GeoJSON"
        "/main/data/earth/CHL/CHL_ADM1.geojson"
    )

    regiones = gpd.read_file(URL)

    print(len(regiones))                        # 16
    print(regiones.crs)                         # EPSG:4326
    print(regiones["shapeName"].tolist()[:3])   # ['Coquimbo', 'Ñuble', 'Los Lagos']
    print(regiones.set_index("shapeISO").loc["CL-RM", "shapeName"])
    # Metropolitana de Santiago

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
        p = feature["properties"]
        print(p["shapeISO"], p["shapeName"])
    ```

    !!! warning "Cuidado con `json.load` en archivos grandes"

        `json.load` construye un objeto Python por cada par de coordenadas.
        Los archivos de 5 a 15 MB de `data/` van bien; el `comunas.geojson`
        heredado de 72 MB en la raíz del repositorio no — se expande a
        bastante más de un gigabyte de objetos Python. Usa `ijson` para
        streamearlo, o GeoPandas, que parsea con GDAL en vez de construir
        diccionarios de Python.

=== "QGIS"

    1. **Capa → Añadir capa → Añadir capa vectorial**
    2. En **Tipo de origen** elige *Protocolo: HTTP(S), nube, etc.*
    3. Pega la URL raw:
       `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/earth/CHL/CHL_ADM1.geojson`
    4. Pulsa **Añadir**.

    QGIS detecta el CRS como EPSG:4326 automáticamente. Para medir áreas o
    distancias, reproyecta primero a un CRS proyectado adecuado a tu zona de
    interés — para Chile, EPSG:5361.

    Para los archivos más grandes — el ADM1 de Canadá pesa 14,9 MB —
    descárgalos localmente en vez de consumirlos por HTTP; si no, QGIS
    repetirá peticiones por rangos.

=== "R"

    ```r
    library(sf)

    url <- paste0(
      "https://raw.githubusercontent.com/andresgmg/World-GeoJSON",
      "/main/data/earth/CHL/CHL_ADM1.geojson"
    )

    regiones <- st_read(url)

    nrow(regiones)           # 16
    st_crs(regiones)         # EPSG:4326
    regiones$shapeName[1:3]  # "Coquimbo" "Ñuble" "Los Lagos"
    plot(st_geometry(regiones))
    ```

## Qué recibes

Un `FeatureCollection` estándar con `bbox` de nivel superior, una feature por
línea. La Región Metropolitana se ve así:

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

Las cuatro primeras propiedades están en todas las features del catálogo: el
nombre, el código ISO 3166-2 cuando existe (si no, el código oficial
nacional, o `""` cuando la fuente no tiene ninguno), el país y el nivel.
`parentISO` y `parentID` nombran la unidad padre — aquí el contorno del país —
y las features por debajo de un ADM1 llevan además `adm1ISO`. Todo lo que
empieza por `src_` viene del origen y cambia según el país — las regiones de
Chile llevan su código DPA y la superficie oficial, los datasets de
geoBoundaries llevan `src_shape_id`. Los nombres no llevan el prefijo "Región
de". La lista completa está en [Esquema de propiedades](../reference/schema.md).

Cada feature tiene además un `id` de nivel superior — `CHL:ADM1:CL-RM` en
esta — único en todo el repositorio, y cada feature subnacional nombra el id
de su padre en `parentID`. Haz el join por `id` y no por `shapeISO`, que está
vacío allí donde la fuente no tiene código. En MapLibre, cópialo a una
propiedad antes de añadir la fuente (`f.properties.id = f.id`) y declara
`promoteId: "id"`, y `setFeatureState` se indexa por él — las fuentes GeoJSON
solo conservan por sí solas los ids de nivel superior que son enteros. Ver
[Diccionario de propiedades → El `id` de la feature](../reference/properties.md#el-id-de-la-feature).

!!! tip "Descubre todo el catálogo en una sola petición"

    `data/index.json` enumera cada territorio y dataset con su ruta, tamaño,
    checksum, bounding box y licencia — ver
    [Índice global y esquemas](../reference/index-json.md).

--8<-- "abbreviations.md"
