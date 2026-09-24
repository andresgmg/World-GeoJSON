# Recetas

Fragmentos orientados a tareas. Todos asumen que ya has descargado un dataset
del [Catálogo](../catalog/index.md); los ejemplos usan `CHL_ADM1.geojson`
(16 regiones) y `CHL_ADM3.geojson` (345 comunas) de Chile.

## Filtrar a una región

Las comunas de Chile llevan `adm1ISO`, el código ISO 3166-2 de su región —
`CL-RM` es la Región Metropolitana.

=== "Python"

    ```python
    import geopandas as gpd

    comunas = gpd.read_file("CHL_ADM3.geojson")

    santiago = comunas[comunas["adm1ISO"] == "CL-RM"]
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

!!! tip "Los niveles partidos ya vienen filtrados"

    Los niveles municipales que tienen un ADM1 por el que partirse traen un
    archivo por región junto al archivo combinado — para Chile,
    `data/earth/CHL/ADM3/CL-RM.geojson` es exactamente la salida de arriba.
    Esas partes, y el archivo combinado, llevan `adm1ISO` en cada feature de
    todos los países que tienen ADM1.

## Simplificar para la web

Lo más útil que puedes hacer con estos datos. Tres reducciones que se componen:

```bash
npx mapshaper CHL_ADM3.geojson \
  -simplify percentage=5% keep-shapes \
  -filter-fields shapeName,shapeISO,shapeType \
  -o precision=0.0001 comunas.min.geojson
```

| Flag | Efecto |
|---|---|
| `-simplify percentage=5%` | Simplificación Visvalingam conservando el 5% de los vértices |
| `keep-shapes` | Evita que desaparezcan islas pequeñas |
| `-filter-fields` | Descarta los atributos de origen `src_*` que el mapa no necesita |
| `precision=0.0001` | Redondea coordenadas a ~11 m |

Espera aproximadamente 7 MB → unos cientos de KB. Revisa siempre el resultado
visualmente: una simplificación agresiva crea slivers y puede desconectar
costas.

Así es exactamente como se construyen los previews commiteados — reduciendo
el porcentaje a la mitad hasta que el archivo baja de 800 KB — así que antes
de hacerlo tú, mira si
`data/earth/{ISO3}/preview/{ISO3}_{LEVEL}.preview.geojson` ya es lo que
necesitas. Ver [Simplificación y previews](../contributing/previews.md).

!!! tip "Por qué la precisión sola ayuda tanto"

    Los archivos de `data/` ya vienen recortados a seis decimales, unos
    11 cm. Cuatro decimales (~11 m) sobran para un mapa, y quitar los dígitos
    extra es compresión gratis. Los archivos heredados de la raíz, en cambio,
    guardan unos **14 decimales** (`-68.95020116247055`) — precisión de
    nanómetro para límites administrativos, todo ruido incompresible ocupando
    bytes reales.

## Convertir a TopoJSON

TopoJSON guarda las fronteras compartidas una sola vez en lugar de dos, lo que
importa mucho para unidades administrativas que teselan un país.

```bash
npx mapshaper CHL_ADM3.geojson -o format=topojson CHL_ADM3.topojson
```

Leerlo de vuelta en el navegador necesita `topojson-client`. El objeto se
llama como el archivo de entrada:

```js
import * as topojson from "topojson-client";

const topo = await fetch("CHL_ADM3.topojson").then((r) => r.json());
const geojson = topojson.feature(topo, topo.objects.CHL_ADM3);
```

## Unir tus propios datos

La razón habitual para querer límites: tienes estadísticas indexadas por un
código oficial y quieres ponerlas en un mapa. Para las comunas de Chile,
`shapeISO` es el código CUT de cinco caracteres — Camiña es `"01402"`.

```python
import geopandas as gpd
import pandas as pd

comunas = gpd.read_file("CHL_ADM3.geojson")
stats = pd.read_csv("poblacion.csv", dtype={"cut": str})   # columnas: cut, poblacion

merged = comunas.merge(stats, left_on="shapeISO", right_on="cut")
```

Si tus datos están indexados por el `id` propio del repositorio — toda
feature tiene uno, `CHL:ADM3:01402` para Camiña, único en todo el catálogo —
haz el join por el `id` de nivel superior de la Feature:

```python
import csv
import json

with open("CHL_ADM3.geojson") as fh:
    comunas = json.load(fh)

with open("poblacion.csv", newline="") as fh:              # columnas: id, poblacion
    poblacion = {fila["id"]: int(fila["poblacion"]) for fila in csv.DictReader(fh)}

for f in comunas["features"]:
    f["properties"]["poblacion"] = poblacion.get(f["id"])
```

`shapeISO` es la clave correcta cuando el otro lado son *estadísticas
oficiales*, porque es el código oficial; `id` es la clave correcta para
cualquier cosa que hayas construido contra este catálogo, porque nunca está
vacío — `shapeISO` es `""` en la mayoría de las unidades municipales fuera de
Chile.

!!! danger "La trampa del cero inicial"

    `shapeISO` es siempre una **cadena**, así que el cero inicial sobrevive.
    Donde se pierde es en el otro lado del join: `pd.read_csv` lee `01402`
    como el entero `1402` salvo que le pases `dtype={"cut": str}`, y entonces
    el join no encuentra nada y no avisa. Si tu CSV ya perdió los ceros,
    devuélvelos:

    ```python
    stats["cut"] = stats["cut"].astype(str).str.zfill(5)
    ```

    La misma comuna lleva además su provincia en `parentISO` (`"014"`,
    Tamarugal) y su región en `adm1ISO` (`"CL-TA"`), así que un join a
    cualquiera de los tres niveles no necesita tabla de equivalencias.

!!! tip "Donde `shapeISO` está vacío"

    geoBoundaries no tiene código para la mayoría de las unidades
    municipales, así que ahí `shapeISO` es `""` — nunca un valor inventado.
    Esas features siguen identificadas por `id`, indexado por su estado y su
    nombre (`USA:ADM2:US-SD.davison`), y siguen llevando `parentID`. Ver
    [Diccionario de propiedades](../reference/properties.md#shapeiso-en-detalle).

## Construir la jerarquía

Cada feature subnacional nombra el `id` de su padre en `parentID`, así que un
árbol no necesita ni unión espacial ni tabla de equivalencias:

```python
import json

with open("CHL_ADM3.geojson") as fh:
    comunas = json.load(fh)["features"]

hijos = {}
for f in comunas:
    hijos.setdefault(f["properties"]["parentID"], []).append(f["id"])

print(hijos["CHL:ADM2:014"])   # las cinco comunas de Tamarugal
```

Haz lo mismo sobre `CHL_ADM2.geojson` para colgar las provincias de sus
regiones (`parentID` = `CHL:ADM1:CL-TA`), y las regiones del país
(`CHL:ADM0:CHL`). Donde un país no tiene ADM1, el `parentID` de una unidad
municipal es directamente el ADM0; el puñado de unidades cuyo padre no se
pudo determinar no lleva `parentID`.

## Calcular el área correctamente

```python
import geopandas as gpd

regiones = gpd.read_file("CHL_ADM1.geojson")

# MAL — los grados no son una unidad de área.
regiones.area

# BIEN — reproyecta a un CRS proyectado adecuado a la zona de interés.
regiones.to_crs(5361).area / 1e6   # km², SIRGAS-Chile / UTM
```

Las regiones de Chile llevan además `src_superficie_km2`, la superficie
oficial del paquete DPA en kilómetros cuadrados — la única propiedad numérica
del catálogo. Prefiérela donde exista: la geometría de aquí está simplificada
a una tolerancia de 100 m, así que un área calculada a partir de ella no
coincidirá exactamente con la cifra oficial.

## Unir niveles en un solo archivo

```bash
npx mapshaper \
  -i CHL_ADM1.geojson CHL_ADM3.geojson combine-files \
  -o format=topojson chile.topojson
```

Produce un único TopoJSON con ambas capas, compartiendo los arcos de la costa.

--8<-- "abbreviations.md"
