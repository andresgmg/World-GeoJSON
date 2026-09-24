# Diccionario de propiedades

Todas las claves de propiedad que aparecen en el corpus, qué significan y dónde
están presentes. Las tablas se han contrastado con los datos; la lista ordenada
de cada dataset está en su [`manifest.json`](manifest.md), en
`datasets[].properties`, y el propio contrato lo aplica un JSON Schema,
[`feature-properties.schema.json`](index-json.md#esquemas), sobre cada feature
de cada archivo a resolución completa en el CI.

## Propiedades estándar

Definidas por este proyecto y presentes en **cada** feature de cada archivo.
Ver [Esquema de propiedades](schema.md).

| Clave | Tipo | Significado |
|---|---|---|
| `shapeName` | cadena | Nombre en el idioma local, con tildes |
| `shapeISO` | cadena | Código oficial — ISO 3166-2 si existe, si no el código nacional; `""` cuando la fuente no tiene ninguno. Nunca un id opaco. Único dentro de un nivel allí donde no está vacío |
| `shapeGroup` | cadena | ISO 3166-1 alpha-3 del país, o código de cuerpo |
| `shapeType` | cadena | `ADM0`–`ADM4` (o `QUAD`, cuando existan datos planetarios) |

### `shapeISO` en detalle

**Vacío significa "sin código".** geoBoundaries no entrega código para la
mayoría de las unidades municipales, y el pipeline ya no lo disimula con el
identificador opaco de la fuente: `shapeISO` es `""` en 15.364 features —
14.797 de ADM2, 501 de ADM3 y las 66 de ADM4. El id de origen sigue ahí, como
`src_shape_id`, y la identidad de la feature es su [`id`](#el-id-de-la-feature).

**Los errores documentados de la fuente se corrigen**, desde
`scripts/shapeiso_fixes.json`. Cada entrada de ese archivo es un código
ISO 3166-2 que la fuente asignó mal a la unidad que nombra `shapeName`:

| Dónde | Unidad | En origen | Corregido |
|---|---|---|---|
| USA ADM1 | Dakota del Sur | `SU-SD` | `US-SD` |
| MEX ADM1 | Ciudad de México ("Distrito Federal" en origen) | `MX-MEX`, duplicando al Estado de México | `MX-CMX` |
| ECU ADM1 | Cotopaxi | `EC-H`, duplicando a Chimborazo | `EC-X` |
| BLZ ADM2 | las 31 unidades | el código de su distrito, repetido | `""` |

El registro no sirve para inventar códigos. Una unidad sin código ISO 3166-2
se queda con `""` y recibe un `id` basado en el nombre.

**Único dentro de cada nivel allí donde no está vacío.** Las tres correcciones
de arriba resolvieron los únicos duplicados, y la regla del `id` de más abajo
solo usa un código que sea único dentro de su nivel — un código duplicado se
descartaría a favor de una clave basada en el nombre, no se reutilizaría en
silencio.

**Siempre una cadena**, aunque parezca numérico (`"01402"`).

## Propiedades de jerarquía

Presentes por debajo de ADM0 según reglas fijas — las mismas en todos los
países, no solo en Chile:

| Clave | Tipo | Significado | Presente en |
|---|---|---|---|
| `adm1ISO` | cadena | Clave de la unidad ADM1 a la que pertenece la feature — el código que da nombre a su parte partida | Cada feature por debajo de ADM1 en un país que publica ADM1 (13.181 features), tanto en los archivos combinados de nivel como en las partes. `"unassigned"` en las 12 features cuyo padre no se pudo determinar (ARG 8, BRA 3, USA 1). No en el propio ADM1 |
| `parentISO` | cadena | Clave del padre en el **nivel publicado anterior** | Cada feature que tiene un nivel padre en el catálogo: el ISO3 en ADM1 (`"CHL"`), la región en las provincias de Chile (`"CL-MA"`), la provincia en las comunas de Chile (`"014"`), el estado en los condados de EE.UU. (`"US-SD"`) |
| `parentID` | cadena | El `id` de la feature padre, listo para un join | 16.063 features. Ausente en ADM0, en las features `"unassigned"` y donde no se publica ningún nivel padre — el ADM4 de Guadalupe y Martinica y el ADM3 de la Guayana Francesa, territorios sin ADM0 en el catálogo |

La comuna chilena de Camiña lleva las tres a la vez: `adm1ISO` es su región
(`CL-TA`), `parentISO` su provincia (`014`) y `parentID` el id de la provincia
(`CHL:ADM2:014`).

!!! note "`parentISO` y `adm1ISO` no son lo mismo"

    En una comuna chilena, `parentISO` es su *provincia* — el padre inmediato
    en la jerarquía oficial — mientras que `adm1ISO` es su *región*, que es por
    lo que está indexado el archivo partido. Donde el nivel publicado anterior
    *es* el ADM1 — condados de EE.UU., municipios de México — los dos
    coinciden. Donde un país no tiene ADM1, el `parentISO` de una unidad
    municipal es el ISO3 y no hay `adm1ISO` (`COL:ADM2:san-rafael`, más
    abajo).

## El `id` de la feature

Cada feature lleva un `id` GeoJSON de nivel superior — un miembro de la
Feature, no una propiedad — con la forma `{ISO3}:{LEVEL}:{clave}`, único en
todo el repositorio. La clave se elige con una sola regla, implementada una
sola vez en `scripts/finalize_geojson.py`:

1. **ADM0** → el ISO3: `ABW:ADM0:ABW`.
2. **`shapeISO`, cuando es un código real y único dentro del nivel**:
   `CHL:ADM3:01402`, `USA:ADM1:US-SD`, `CHL:ADM2:014`.
3. **Si no, por debajo del primer nivel cuando el país tiene ADM1**:
   `{adm1ISO}.{slug(shapeName)}` — `USA:ADM2:US-SD.davison`,
   `BLZ:ADM2:BZ-SC.stann-creek-west`, `MEX:ADM2:MX-CMX.azcapotzalco`.
4. **Si no**, `slug(shapeName)`: `COL:ADM2:san-rafael`, `PRI:ADM2:fajardo`,
   `GLP:ADM4:la-desirade`.
5. **Las colisiones de nombre** reciben un sufijo numérico determinista, en
   el orden del id de origen: `COL:ADM2:albania`, `COL:ADM2:albania-2`,
   `COL:ADM2:albania-3`.

Medido sobre los datos actuales: 831 ids están indexados por un código real
(todos los ADM0, los 378 ADM1, las 56 provincias y las 345 comunas de Chile),
12.780 por `adm1.slug`, 2.584 solo por el slug, y 169 llevan sufijo numérico
(COL 84, HND 28, SLV 18, ARG 16, GTM 6, USA 6, MEX 4, BLZ 2, BRA 2, VIR 2,
SUR 1).

!!! warning "Los ids con sufijo son estables por versión de datos — fija una"

    El sufijo se asigna en el orden del id de origen, así que
    `COL:ADM2:albania-2` sigue siendo `albania-2` mientras no cambie la añada
    de la fuente. Un refresco de la fuente puede renumerarlos. Los ids
    indexados por código no tienen este problema. Fija una versión de datos
    etiquetada en producción y trata un refresco de la fuente como el cambio
    rompedor que es — ver
    [Versionado y estabilidad](../about/versioning.md).

Una clave se puede fijar a mano en `scripts/id_overrides.json` — indexado por
ISO3, nivel y el `src_shape_id` de la feature (o su `shapeISO` en las fuentes
nacionales), con la parte de la clave que va tras `{ISO3}:{LEVEL}:` como
valor. Hoy está vacío: las correcciones de `shapeISO` resolvieron todas las
colisiones conocidas. `finalize_geojson.py` se niega a ejecutarse mientras
quede una colisión y nombra las features, así que una entrada nueva ahí es la
forma de resolverla.

Los previews llevan el mismo `id` que los archivos completos, así que un mapa
dibujado desde un preview se puede unir a cualquier cosa indexada por los
datos completos.

## Orden de las propiedades

Las propiedades se escriben en un orden fijo: `shapeName`, `shapeISO`,
`shapeGroup`, `shapeType`, después `adm1ISO`, `parentISO` y `parentID` donde
existan, y después los campos `src_*`. Los archivos son canónicos — una
feature por línea, separadores compactos, coordenadas con 6 decimales — y el
CI comprueba que volver a ejecutar el paso de finalización no cambia nada. Ver
[Esquema de propiedades → Formato del archivo](schema.md#formato-del-archivo).

## Ejemplos reales

Una feature por regla, tal cual está almacenada (geometría omitida):

```json
{"type":"Feature","id":"CHL:ADM1:CL-CO","properties":{"shapeName":"Coquimbo","shapeISO":"CL-CO","shapeGroup":"CHL","shapeType":"ADM1","parentISO":"CHL","parentID":"CHL:ADM0:CHL","src_cut_reg":"04","src_superficie_km2":40587.8}}
{"type":"Feature","id":"CHL:ADM2:122","properties":{"shapeName":"Antártica Chilena","shapeISO":"122","shapeGroup":"CHL","shapeType":"ADM2","adm1ISO":"CL-MA","parentISO":"CL-MA","parentID":"CHL:ADM1:CL-MA","src_cut_prov":"122","src_cut_reg":"12","src_region":"Magallanes y de la Antártica Chilena"}}
{"type":"Feature","id":"CHL:ADM3:01402","properties":{"shapeName":"Camiña","shapeISO":"01402","shapeGroup":"CHL","shapeType":"ADM3","adm1ISO":"CL-TA","parentISO":"014","parentID":"CHL:ADM2:014","src_cut_com":"01402","src_cut_prov":"014","src_cut_reg":"01","src_provincia":"Tamarugal","src_region":"Tarapacá"}}
{"type":"Feature","id":"USA:ADM2:US-SD.davison","properties":{"shapeName":"Davison","shapeISO":"","shapeGroup":"USA","shapeType":"ADM2","adm1ISO":"US-SD","parentISO":"US-SD","parentID":"USA:ADM1:US-SD","src_shape_id":"52423323B35289781006587"}}
{"type":"Feature","id":"COL:ADM2:san-rafael","properties":{"shapeName":"San Rafael","shapeISO":"","shapeGroup":"COL","shapeType":"ADM2","parentISO":"COL","parentID":"COL:ADM0:COL","src_shape_id":"7082276B22021388124839"}}
{"type":"Feature","id":"GLP:ADM4:la-desirade","properties":{"shapeName":"La Désirade","shapeISO":"","shapeGroup":"GLP","shapeType":"ADM4","src_shape_id":"45945325B8612440900081"}}
```

Coquimbo es un ADM1: padre, pero sin `adm1ISO`. Antártica Chilena y Camiña
están indexadas por su código CUT, y el padre de Camiña es una provincia, no
su región. Davison no tiene código, así que se indexa por estado y nombre. El
país de San Rafael no tiene ADM1, así que su padre es el ADM0. La Désirade no
tiene ningún nivel padre en el catálogo.

## Propiedades de origen — geoBoundaries

Cada feature tomada de geoBoundaries — ADM1 y niveles inferiores, 15.726
features hoy — lleva un campo extra:

| Clave | Tipo | Significado |
|---|---|---|
| `src_shape_id` | cadena | Identificador opaco propio de geoBoundaries para la unidad, p. ej. `66186276B69138566591314`. Estable dentro de una release de geoBoundaries; no es un código territorial. Es también la clave con la que `shapeiso_fixes.json` e `id_overrides.json` señalan una feature |

Los otros cuatro campos de geoBoundaries (`shapeName`, `shapeISO`,
`shapeGroup`, `shapeType`) ya coinciden con el vocabulario estándar, que es
justamente por lo que este proyecto lo adoptó. Su `shapeID` se renombra a
`src_shape_id` al entrar; ningún archivo lleva una propiedad llamada `shapeID`.

## Propiedades de origen — Chile

Preservadas de la DPA 2023 de IDE Chile con el prefijo `src_`.

| Clave | Tipo | Presente en | Significado |
|---|---|---|---|
| `src_cut_reg` | cadena | ADM1, ADM2, ADM3 | Código CUT de región, dos caracteres |
| `src_cut_prov` | cadena | ADM2, ADM3 | Código CUT de provincia, tres caracteres |
| `src_cut_com` | cadena | ADM3 | Código CUT de comuna, cinco caracteres, con ceros a la izquierda |
| `src_region` | cadena | ADM2, ADM3 | Nombre de la región, sin el prefijo "Región de" |
| `src_provincia` | cadena | ADM3 | Nombre de la provincia |
| `src_superficie_km2` | número | ADM1 | Superficie oficial en **kilómetros cuadrados**. La única propiedad no textual del corpus |

CUT (*Código Único Territorial*) es el esquema nacional de codificación
territorial que usan el INE y SUBDERE. Los códigos anidan: la comuna `01402`
(Camiña) está en la provincia `014` (Tamarugal), que está en la región `01`
(Tarapacá).

## Propiedades que se descartan

Artefactos de exportación del software GIS de origen. No aportan información que
no se pueda recalcular, e inducen a error.

| Clave | Por qué se va |
|---|---|
| `objectid` | Número de fila interno de Esri. No es estable entre exportaciones |
| `st_area_sh` | Área precalculada en metros cuadrados, desde una proyección no declarada |
| `st_length_` | Perímetro precalculado, mismo problema |
| `shape_leng` | Duplicado de `st_length_`, truncado al límite de 10 caracteres de dBase |

## Historia

!!! info "Qué cambió en v1.0.0"

    En el `main` 0.x sin publicar, 22 datasets municipales llevaban el id
    opaco de geoBoundaries en `shapeISO`, el código estaba duplicado en BLZ
    ADM2, MEX ADM1 y ECU ADM1, `adm1ISO` existía solo en las partes partidas
    (más el ADM3 combinado de Chile), `parentISO` solo en Chile, y ninguna
    feature tenía `id`. El paso de finalización introducido en v1.0.0 lo
    corrigió todo de una pasada; el
    [Registro de cambios](../about/changelog.md) tiene la lista.

## Trampas conocidas

!!! danger "Los códigos territoriales deben ser cadenas"

    Un número JSON no puede guardar un cero a la izquierda, así que cualquier
    fuente que almacene el `01402` de Chile como entero produce `1402` sin
    avisar, y los joins contra estadísticas oficiales no encuentran nada.
    `shapeISO` y todos los campos `src_cut_*` son cadenas.

!!! warning "`shapeISO` está vacío donde no hay código — haz el join por `id`"

    La mayoría de las unidades municipales no tienen código ISO 3166-2 y en
    ellas `shapeISO` es `""`. Es una clave de join correcta contra
    estadísticas oficiales *donde está relleno*; para la identidad usa `id`,
    que toda feature tiene y que es único en el repositorio.

!!! note "No parsees el `id`"

    La clave es legible a propósito, pero `shapeISO`, `adm1ISO`, `parentISO`
    y `parentID` existen como campos separados precisamente para que nunca
    tengas que desmontar un `id`. Trátalo como una cadena opaca al hacer
    joins.

## Regenerar esta página

Las listas de propiedades se registran por dataset en cada
[`manifest.json`](manifest.md). Esta página se mantiene a mano; generarla desde
los manifiestos está en la [Hoja de ruta](../about/roadmap.md).

--8<-- "abbreviations.md"
