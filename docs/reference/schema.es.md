# Esquema de propiedades

Cada feature lleva un pequeño conjunto de propiedades estándar, más lo que
haya aportado la fuente original.

## Propiedades obligatorias

| Propiedad | Tipo | Significado |
|---|---|---|
| `shapeName` | cadena | Nombre de la unidad, en el idioma local, con las tildes correctas |
| `shapeISO` | cadena | Código oficial de la unidad — ISO 3166-2 si existe, si no el código nacional; `""` cuando la fuente no tiene ninguno |
| `shapeGroup` | cadena | ISO 3166-1 alpha-3 del país que la contiene, o código de cuerpo |
| `shapeType` | cadena | `ADM0`, `ADM1`, `ADM2`, `ADM3`, `ADM4` o `QUAD` |

Estos nombres coinciden deliberadamente con
[geoBoundaries](https://www.geoboundaries.org/). Adoptar un vocabulario ya
existente significa que quien ya procesa datos de geoBoundaries puede leer
estos archivos sin cambios, y elimina toda una categoría de discusión estéril
en la revisión.

Las cuatro están presentes en cada feature de cada archivo bajo `data/`; el CI
valida cada feature contra el JSON Schema que lo exige
([`feature-properties.schema.json`](#json-schemas)). `shapeISO` es `""` en la
mayoría de las unidades municipales — geoBoundaries no tiene código para
ellas — y nunca es un id opaco de origen; donde no está vacío es único dentro
de su nivel.

## Propiedades opcionales

| Propiedad | Tipo | Significado | Presente en |
|---|---|---|---|
| `adm1ISO` | cadena | Clave del ADM1 al que pertenece la feature | Cada feature por debajo de ADM1 cuando el país publica ADM1, archivos combinados incluidos; `"unassigned"` donde no se pudo determinar el padre |
| `parentISO` | cadena | Clave del padre en el nivel publicado anterior | Cada feature que tiene un nivel padre en el catálogo — ADM1 (el ISO3) e inferiores |
| `parentID` | cadena | El `id` de la feature padre | Las mismas, salvo las features `"unassigned"` |
| `src_shape_id` | cadena | Identificador opaco de origen de geoBoundaries | Cada feature de geoBoundaries (ADM1 e inferiores) |
| `src_*` | cadena o número | Otros atributos de origen, con prefijo | Chile: códigos CUT, nombres de región y provincia, superficie oficial |

No se permite ninguna otra propiedad: el esquema fija
`additionalProperties: false`, así que un archivo con una clave extraña falla
el CI. Las reglas de presencia completas, con recuentos, están en el
[Diccionario de propiedades](properties.md#propiedades-de-jerarquia).

!!! tip "Join por `id`, anidamiento por `parentID`"

    Cada feature tiene un `id` de nivel Feature (más abajo) y cada feature
    subnacional nombra el id de su padre en `parentID`, en todos los países.
    `shapeISO` es la clave para unir *estadísticas oficiales* donde existe un
    código; `id` es la clave para todo lo demás.

## Las propiedades de origen se preservan, no se borran

Los atributos originales se conservan con el prefijo `src_`. Esta es Camiña,
de `data/earth/CHL/ADM3/CL-TA.geojson` — `id` de feature `CHL:ADM3:01402` —
con sus propiedades tal cual están almacenadas, en el orden en que se
almacenan:

```json
{
  "shapeName": "Camiña",
  "shapeISO": "01402",
  "shapeGroup": "CHL",
  "shapeType": "ADM3",
  "adm1ISO": "CL-TA",
  "parentISO": "014",
  "parentID": "CHL:ADM2:014",
  "src_cut_com": "01402",
  "src_cut_prov": "014",
  "src_cut_reg": "01",
  "src_provincia": "Tamarugal",
  "src_region": "Tarapacá"
}
```

El razonamiento: la información que descartas se pierde, y siempre hay alguien
que necesita justo el campo que decidiste que era irrelevante. Los códigos CUT y
los nombres de región y provincia permiten agregar comunas a provincias o
regiones con una comparación de cadenas en vez de una unión espacial. El
prefijo los conserva sin dejar que colisionen con el vocabulario estándar — y el
`shapeID` de geoBoundaries pasa a `src_shape_id` por la misma razón.

## Qué se descarta

Los artefactos de exportación del software GIS de origen son la excepción. No
aportan información que no se pueda recalcular, y además inducen a error:

| Propiedad | Por qué se va |
|---|---|
| `objectid` | Número de fila interno de Esri. No es estable entre exportaciones ni significativo. |
| `st_area_sh` | Área precalculada en **metros cuadrados**, desde una proyección no declarada |
| `st_length_` | Perímetro precalculado, mismo problema |
| `shape_leng` | Duplicado de `st_length_`, truncado al límite de 10 caracteres de dBase |
| `area_km` | Área precalculada en **kilómetros cuadrados** (archivos heredados de la raíz) |

!!! warning "Las áreas precalculadas no se pueden comparar entre fuentes"

    Cada productor usa unidades y proyecciones distintas para un campo que
    suena igual, y rara vez documenta ninguna de las dos. La DPA de Chile trae
    `SUPERFICIE` en km²; las exportaciones Esri traen `st_area_sh` en m².
    Compáralos ingenuamente y el resultado se desvía por un factor de un
    millón.

    Cuando un campo así se preserva, se le da un nombre que lleva la unidad
    (`src_superficie_km2`, en las regiones de Chile). Para cualquier cosa de la
    que dependas, calcula el área tú mismo desde la geometría, en una
    proyección adecuada a tu zona de interés — ver
    [Recetas](../get-started/recipes.md#calcular-el-area-correctamente).

## Ejemplo trabajado: Chile

Chile se construye desde la *División Política Administrativa* 2023 de IDE
Chile, cuyos atributos encajan limpiamente en el conjunto estándar:

| Campo de origen | Pasa a ser |
|---|---|
| `REGION` | `shapeName` en ADM1; `src_region` en ADM2 y ADM3 |
| `PROVINCIA` | `shapeName` en ADM2; `src_provincia` en ADM3 |
| `COMUNA` | `shapeName` en ADM3 |
| `CUT_REG` | `shapeISO` en ADM1 vía el lookup ISO 3166-2 (`01` → `CL-TA`); `src_cut_reg` en ADM1, ADM2 y ADM3 |
| `CUT_PROV` | `shapeISO` en ADM2, `parentISO` en ADM3; `src_cut_prov` en ambos |
| `CUT_COM` | `shapeISO` en ADM3; `src_cut_com` |
| `SUPERFICIE` | `src_superficie_km2` en ADM1 |

Los nombres de región llegan **sin** el prefijo "Región de": `Ñuble`,
`Tarapacá`, `Libertador General Bernardo O'Higgins`. Una región queda así:

```json
{
  "shapeName": "Coquimbo",
  "shapeISO": "CL-CO",
  "shapeGroup": "CHL",
  "shapeType": "ADM1",
  "parentISO": "CHL",
  "parentID": "CHL:ADM0:CHL",
  "src_cut_reg": "04",
  "src_superficie_km2": 40587.8
}
```

— `id` de feature `CHL:ADM1:CL-CO`, con el contorno del país como padre — y
una comuna como el ejemplo de Camiña de arriba.

### `shapeISO` es siempre una cadena

El código oficial INE/SUBDERE de Camiña es `01402` — cinco caracteres, cero
inicial incluido. Todas las comunas de las regiones 1 a 9 lo llevan.

Un **número** JSON no puede representar un cero a la izquierda en absoluto, así
que una fuente que los guarde como enteros convierte `01402` en `1402` sin
avisar, y cualquier join contra estadísticas oficiales deja de encontrar nada.
El shapefile de la DPA ya guarda los códigos CUT como cadenas, que es una de las
razones por las que se eligió frente a las alternativas.

Por eso `shapeISO` es siempre una cadena, nunca un número, aunque parezca
numérico.

!!! note "Aquí los códigos son nacionales, no ISO 3166-2"

    Chile tiene códigos ISO 3166-2 para sus regiones (`CL-TA`) pero no para
    provincias ni comunas, así que esos niveles llevan el código CUT nacional:
    el código de provincia de tres dígitos en ADM2 (`014`), el de comuna de
    cinco dígitos en ADM3 (`01402`). Es el respaldo documentado: ISO 3166-2
    donde exista, código nacional en caso contrario.

## El `id` a nivel de feature

Cada feature de cada archivo bajo `data/` — previews incluidos — fija el
miembro `id` de nivel superior de GeoJSON: `{ISO3}:{LEVEL}:{clave}`, único en
todo el repositorio.

```json
{"type":"Feature","id":"CHL:ADM3:01402","properties":{…},"geometry":{…}}
```

La clave es el `shapeISO` cuando es un código real y único
(`CHL:ADM3:01402`, `USA:ADM1:US-SD`) y una clave basada en el nombre en caso
contrario (`USA:ADM2:US-SD.davison`, `COL:ADM2:san-rafael`). La regla completa
de cinco pasos, el reparto medido entre ambas, el comportamiento del sufijo
numérico ante colisiones de nombre y su salvedad de estabilidad, y el registro
`scripts/id_overrides.json` están documentados una sola vez, en
[Diccionario de propiedades → El `id` de la feature](properties.md#el-id-de-la-feature).

La regla de fondo: o todas las features de un archivo tienen un `id` estable y
significativo, o ninguna lo tiene. El `comunas.geojson` heredado de la raíz es
el ejemplo de lo que no hay que hacer — lleva `id` en solo **5 de 343**
features de comunas, con valores (`0`, `1`, `3`, `142`, `155`) que no se
corresponden con nada, así que quien se apoyara en `feature.id` obtenía
`undefined` el 98,5% de las veces. Por eso el contrato hace el `id`
obligatorio: [`feature.schema.json`](#json-schemas) lo lista en `required`, y
el CI valida cada feature contra él.

## Formato del archivo

Cada archivo a resolución completa lo escribe `scripts/finalize_geojson.py` en
una única forma canónica, para que los mismos datos produzcan siempre los
mismos bytes:

```
{"type":"FeatureCollection","bbox":[oeste,sur,este,norte],"features":[
{"type":"Feature","id":"CHL:ADM1:CL-CO","properties":{…},"geometry":{…}},
{"type":"Feature","id":"CHL:ADM1:CL-NB","properties":{…},"geometry":{…}},
…
]}
```

- la cabecera de la colección y su `bbox` en la primera línea, y después
  **una feature por línea** — `grep`, `head` y los parsers en streaming
  funcionan;
- separadores compactos, sin indentación;
- coordenadas con como máximo **6 decimales** (4 en los previews), sin
  exponentes ni ceros finales;
- `bbox` recalculado desde las coordenadas, así que siempre coincide con la
  geometría;
- propiedades en el [orden fijo](properties.md#orden-de-las-propiedades).

Ejecutar dos veces el paso de finalización no cambia nada, y el CI lo ejecuta
con `--check` para asegurarse de que cada archivo commiteado tiene esta forma.
Los previews usan el mismo formato y llevan el mismo `id`, con solo
`shapeName`, `shapeISO` y `shapeType`.

## JSON Schemas

El contrato de esta página es legible por máquina. Dos esquemas, JSON Schema
2020-12, en `schemas/` y servidos desde este sitio:

| Esquema | Valida | Publicado en |
|---|---|---|
| `feature.schema.json` | Una Feature: `type`, un `id` obligatorio que cumple `^[A-Z]{3}:(ADM[0-4]\|QUAD):\S+$`, `properties` (por referencia al esquema siguiente), una geometría `Polygon` o `MultiPolygon` | <https://andresgmg.github.io/World-GeoJSON/schemas/feature.schema.json> |
| `feature-properties.schema.json` | El objeto `properties`: las cuatro claves obligatorias, las tres claves de jerarquía, `src_*` por patrón, nada más | <https://andresgmg.github.io/World-GeoJSON/schemas/feature-properties.schema.json> |

`scripts/validate_data.py` los aplica a cada feature de cada archivo a
resolución completa en el CI. Los esquemas del manifiesto, del índice y del
registro están en [Índice global y esquemas](index-json.md#esquemas).

## Nombres y codificación

- Los archivos son UTF-8. `shapeName` **debe** llevar las tildes correctas:
  `Ñuble`, `Camiña`, `La Araucanía`.
- Usa un apóstrofo ASCII (`'`), no uno tipográfico. `Libertador General
  Bernardo O'Higgins` lo hace así; respetarlo importa para la comparación de
  cadenas.
- No abrevies. El `regiones.geojson` heredado de la raíz trae `Región de Aysén
  del Gral.Ibañez del Campo` — mal de tres formas: "Gral." abreviado, sin
  espacio tras el punto y sin la tilde en "Ibáñez". Los datos actuales llevan
  `Aysén del General Carlos Ibáñez del Campo`, tal como lo publica la DPA.

--8<-- "abbreviations.md"
