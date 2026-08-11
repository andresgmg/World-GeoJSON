# Recetas

Fragmentos orientados a tareas. Todos asumen que ya tienes una URL de dataset
del [Catálogo](../catalog/index.md).

## Filtrar a una región

=== "Python"

    ```python
    import geopandas as gpd

    comunas = gpd.read_file("comunas.geojson")

    # codregion 13 es la Región Metropolitana de Santiago.
    santiago = comunas[comunas["codregion"] == 13]
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

## Simplificar para la web

Lo más útil que puedes hacer con estos datos. Tres reducciones que se componen:

```bash
npx mapshaper comunas.geojson \
  -simplify percentage=2% keep-shapes \
  -filter-fields Comuna,cod_comuna,Region \
  -o precision=0.0001 comunas.min.geojson
```

| Flag | Efecto |
|---|---|
| `-simplify percentage=2%` | Simplificación Visvalingam conservando el 2% de los vértices |
| `keep-shapes` | Evita que desaparezcan islas pequeñas |
| `-filter-fields` | Descarta `objectid`, `st_area_sh`, `st_length_` y compañía |
| `precision=0.0001` | Redondea coordenadas a ~11 m |

Espera aproximadamente 70 MB → 300-800 KB. Revisa siempre el resultado
visualmente: una simplificación agresiva crea slivers y puede desconectar
costas.

!!! tip "Por qué la precisión sola ayuda tanto"

    Los archivos de origen guardan coordenadas con unos **14 decimales**
    (`-68.95020116247055`) — precisión de nanómetro para límites
    administrativos. Seis decimales son unos 11 cm. Todo lo que va más allá es
    ruido incompresible ocupando bytes reales.

## Convertir a TopoJSON

TopoJSON guarda las fronteras compartidas una sola vez en lugar de dos, lo que
importa mucho para unidades administrativas que teselan un país.

```bash
npx mapshaper comunas.geojson -o format=topojson comunas.topojson
```

Leerlo de vuelta en el navegador necesita `topojson-client`:

```js
import * as topojson from "topojson-client";

const topo = await fetch("comunas.topojson").then((r) => r.json());
const geojson = topojson.feature(topo, topo.objects.comunas);
```

## Unir tus propios datos

La razón habitual para querer límites: tienes estadísticas indexadas por un
código oficial y quieres ponerlas en un mapa.

```python
import geopandas as gpd
import pandas as pd

comunas = gpd.read_file("comunas.geojson")
stats = pd.read_csv("poblacion.csv")   # columnas: cut, poblacion

merged = comunas.merge(stats, left_on="cod_comuna", right_on="cut")
```

!!! danger "La trampa del cero inicial"

    `cod_comuna` está guardado como **número**, así que Camiña es `1402`. El
    código oficial INE/SUBDERE es la cadena de cinco caracteres `01402` — todas
    las regiones de la 1 a la 9 pierden así su cero inicial.

    Si tu CSV tiene cadenas con ceros a la izquierda, el join no encuentra nada
    y no avisa. Normaliza un lado primero:

    ```python
    comunas["cut"] = comunas["cod_comuna"].astype(str).str.zfill(5)
    stats["cut"] = stats["cut"].astype(str).str.zfill(5)
    ```

    Este es exactamente el tipo de problema que el
    [esquema de propiedades](../reference/schema.md) estandarizado existe para
    eliminar.

## Calcular el área correctamente

```python
import geopandas as gpd

regiones = gpd.read_file("regiones.geojson")

# MAL — los grados no son una unidad de área.
regiones.area

# BIEN — reproyecta a un CRS proyectado adecuado a la zona de interés.
regiones.to_crs(5361).area / 1e6   # km², SIRGAS-Chile / UTM
```

La propiedad `area_km` que ya viene en `regiones.geojson` está precalculada
aguas arriba y se puede usar directamente. Ojo: `st_area_sh` en ese mismo
archivo está en **metros cuadrados**, no en kilómetros cuadrados — las unidades
son inconsistentes entre ambas propiedades y entre los dos archivos.

## Unir niveles en un solo archivo

```bash
npx mapshaper \
  -i regiones.geojson comunas.geojson combine-files \
  -o format=topojson chile.topojson
```

Produce un único TopoJSON con ambas capas, compartiendo los arcos de la costa.

--8<-- "abbreviations.md"
