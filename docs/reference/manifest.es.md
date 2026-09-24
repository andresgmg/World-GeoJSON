# Formato del manifiesto

Cada directorio de dataset contiene un `manifest.json`. Es la **única** entrada
de este sitio de documentación: todas las páginas del catálogo se generan a
partir de él. Hoy hay 55, uno por territorio bajo `data/earth/`, y los 55 van
incrustados tal cual en el [índice global](index-json.md), `data/index.json`.

## Por qué existe

El build de documentación no debe abrir nunca un archivo GeoJSON.

Parsear decenas de megabytes de geometría en cada build haría `mkdocs serve`
inutilizable para editar, ralentizaría notablemente el CI y obligaría al CI a
descargar datos que de otro modo no necesita. En su lugar, un script aparte
escanea los datos cuando cambian *los datos* y escribe unos pocos kilobytes de
metadatos a su lado. El build de docs lee solo eso.

Esto es lo que permite que el catálogo escale a cientos de países con coste de
build constante, y lo que permite que el CI haga checkout del repositorio *sin
ningún archivo `.geojson`*.

## Ejemplo

`data/earth/CHL/manifest.json`, abreviado a sus dos primeros datasets:

```json
{
  "schema_version": 1,
  "body": "earth",
  "iso_a3": "CHL",
  "iso_a2": "CL",
  "m49_region": "South America",
  "name": { "en": "Chile", "es": "Chile" },
  "crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 },
  "status": "ok",
  "source": {
    "name": "IDE Chile / SUBDERE — División Política Administrativa 2023",
    "url": "https://www.geoportal.cl/",
    "license": "mixed",
    "retrieved": "2026-08-11",
    "licenses": ["CC-BY-4.0", "public-domain"]
  },
  "datasets": [
    {
      "level": "ADM0",
      "path": "data/earth/CHL/CHL_ADM0.geojson",
      "bytes": 407948,
      "sha256": "9abf1248d9c64bb3e50a63a24723595093aa6a58b75cf3935b3465b090205889",
      "features": 1,
      "bbox": [-109.453725, -55.918504, -66.420806, -17.506588],
      "geometry_types": { "MultiPolygon": 1 },
      "properties": ["shapeGroup", "shapeISO", "shapeName", "shapeType"],
      "preview": "data/earth/CHL/preview/CHL_ADM0.preview.geojson",
      "preview_bytes": 18800,
      "simplification": { "method": "visvalingam", "tolerance_m": 100 },
      "license": "public-domain",
      "src_provider": "Natural Earth"
    },
    {
      "level": "ADM1",
      "path": "data/earth/CHL/CHL_ADM1.geojson",
      "bytes": 4815275,
      "sha256": "6679a263585d6ef01bf9778d629f6daaa9a765011109b7ad95c27863a0a7b5c5",
      "features": 16,
      "bbox": [-109.449861, -56.525107, -66.416176, -17.498399],
      "geometry_types": { "MultiPolygon": 10, "Polygon": 6 },
      "properties": ["parentID", "parentISO", "shapeGroup", "shapeISO", "shapeName",
                     "shapeType", "src_cut_reg", "src_superficie_km2"],
      "preview": "data/earth/CHL/preview/CHL_ADM1.preview.geojson",
      "preview_bytes": 226849,
      "simplification": { "method": "visvalingam", "tolerance_m": 100 },
      "license": "CC-BY-4.0"
    }
  ]
}
```

La licencia es `"mixed"` porque el contorno es de Natural Earth (dominio
público) mientras que los tres niveles de subdivisión son de IDE Chile
(CC BY 4.0); `licenses` enumera los valores distintos. El manifiesto de Chile
no tiene `notes`.

## Campos

### Nivel superior

| Campo | Tipo | Significado |
|---|---|---|
| `schema_version` | entero | Versión del formato de este manifiesto. `1` hoy; se sube solo ante un cambio rompedor de formato |
| `body` | cadena | `earth` (la Luna y Marte usarán el suyo) |
| `iso_a3`, `iso_a2` | cadena | Códigos ISO 3166-1 |
| `m49_region` | cadena | Subregión UN M49, usada para agrupar el catálogo |
| `name` | objeto | Nombres para mostrar `{ "en": …, "es": … }` |
| `crs` | objeto | Siempre `{ "authority": "OGC", "code": "CRS84", "epsg": 4326 }` para la Tierra — los archivos no pueden declararlo por sí mismos. Ver [CRS](crs.md) |
| `status` | cadena | `ok`, o `review` cuando la asignación del tier municipal en `scripts/countries.json` sigue marcada como `verify` |
| `source` | objeto | `name`, `url`, `license`, `retrieved` (fecha ISO). Cuando los datasets llevan licencias distintas, `license` es `"mixed"` y `licenses` enumera los valores distintos, ordenados |
| `notes` | cadena | Opcional, una línea. Huecos conocidos, rarezas de origen, disputas |
| `datasets` | array | Una entrada por nivel, ordenadas por nivel |

### Por dataset (`datasets[]`)

| Campo | Significado |
|---|---|
| `level` | `ADM0`–`ADM4` |
| `path` | El archivo del nivel completo, relativo a la raíz del repositorio. Ausente cuando el combinado era demasiado grande para publicarse (el ADM2 de Brasil hoy) |
| `bytes`, `sha256` | Tamaño y hash de `path`; en un nivel partido sin combinado, `bytes` es la suma de las partes |
| `features` | Número de features del **nivel completo**, para que el catálogo pueda dar siempre un total |
| `bbox` | `[oeste, sur, este, norte]`, mínimo/máximo ingenuo de todas las coordenadas — ver la nota sobre el antimeridiano más abajo |
| `geometry_types` | Recuento por tipo de geometría GeoJSON, p. ej. `{ "MultiPolygon": 10, "Polygon": 6 }` |
| `properties` | Todas las claves de propiedad presentes en alguna feature, **ordenadas** — las cuatro claves estándar, las de jerarquía (`adm1ISO`, `parentISO`, `parentID`) donde el nivel las lleva, y los campos `src_*` |
| `preview`, `preview_bytes` | El archivo simplificado de `preview/` y su tamaño |
| `simplification` | Lo aplicado: `{ "method": "visvalingam", "tolerance_m": 100 }` |
| `license` | Identificador tipo SPDX de **este dataset** — las licencias difieren entre niveles de un mismo país |
| `src_provider` | Quién produjo la geometría aguas arriba: `Natural Earth`, `Instituto Nacional de Estadística y Geografía (INEGI)`, … Ausente en los niveles de subdivisión de Chile, donde `source` ya lo dice |
| `src_year` | Opcional. El año que representan los límites, según la fuente (`"2018"`) |
| `split_by` | `"ADM1"` cuando el nivel va partido en partes. Opcional |
| `unassigned` | Recuento opcional de unidades que no pudieron asociarse a un padre ADM1 y se conservaron en `unassigned.geojson` |
| `parts` | Array opcional, presente en los niveles partidos — ver abajo |

### Por parte (`datasets[].parts[]`)

Cada parte tiene `code` (el código ADM1 que da nombre al archivo, o
`unassigned`), `path`, `bytes`, `sha256`, `features`, `bbox`, `geometry_types`
y `properties` — las mismas medidas que un dataset, para un solo archivo.

## Niveles partidos

Un nivel partido lleva un array `parts` junto al archivo combinado opcional. El
ADM3 de Chile, abreviado:

```json
{
  "level": "ADM3",
  "path": "data/earth/CHL/CHL_ADM3.geojson",
  "bytes": 6982386,
  "features": 345,
  "properties": ["adm1ISO", "parentID", "parentISO", "shapeGroup", "shapeISO",
                 "shapeName", "shapeType", "src_cut_com", "src_cut_prov",
                 "src_cut_reg", "src_provincia", "src_region"],
  "preview": "data/earth/CHL/preview/CHL_ADM3.preview.geojson",
  "split_by": "ADM1",
  "license": "CC-BY-4.0",
  "parts": [
    {
      "code": "CL-AI",
      "path": "data/earth/CHL/ADM3/CL-AI.geojson",
      "bytes": 1281666,
      "sha256": "604104c46aa2863ed43158ff48be1450768e794f86276d840dd856c1e746c1f8",
      "features": 10,
      "bbox": [-75.64927, -49.158776, -71.091675, -43.637991],
      "geometry_types": { "MultiPolygon": 4, "Polygon": 6 },
      "properties": ["adm1ISO", "parentID", "parentISO", "shapeGroup", "shapeISO",
                     "shapeName", "shapeType", "src_cut_com", "src_cut_prov",
                     "src_cut_reg", "src_provincia", "src_region"]
    }
  ]
}
```

- `features` en la entrada es el **nivel completo**, para que el catálogo pueda
  dar siempre un total exista o no un archivo combinado.
- `path` es el archivo de país completo, opcional, presente solo cuando cabe
  bajo el presupuesto de 18 MiB. El ADM2 de Brasil tiene 28 partes y ningún
  `path`; su ausencia es normal y el catálogo lo indica.
- `code` es la clave de la unidad ADM1: su `shapeISO` tras las correcciones de
  `scripts/shapeiso_fixes.json`, que es también el valor de `adm1ISO` en cada
  feature de la parte y la clave del propio `id` del ADM1. Las erratas de
  origen se corrigen ahí en vez de pasarse tal cual — los 66 condados de
  Dakota del Sur están en la parte codificada `US-SD` aunque geoBoundaries
  codifique el estado como `SU-SD`. Una parte codificada `unassigned`
  contiene las unidades a las que no se encontró padre; la entrada ADM2 de
  USA lleva además `"unassigned": 1`.

El CI comprueba que las partes sumen exactamente el número de features del
nivel — así es como se detecta una partición que perdió o duplicó un municipio.

!!! warning "`bbox` es un mínimo/máximo ingenuo — en el manifiesto y en el archivo"

    El `bbox` del manifiesto es el simple mínimo y máximo de cada coordenada,
    y también lo es el `bbox` de nivel superior del propio archivo: el paso de
    finalización lo recalcula desde las coordenadas, el CI comprueba que los
    dos coinciden, y ninguno usa la forma con oeste mayor que este que permite
    la RFC 7946 §5.2. Para un territorio que cruza el antimeridiano eso es
    casi el globo entero — las entradas de USA y `USA_ADM0.geojson` leen por
    igual `[-179,14…, 18,90…, 179,78…, 71,41…]`. No uses el `bbox` para
    decidir si un país así toca tu zona de interés cerca de los 180°. Ver
    [CRS → El antimeridiano](crs.md#el-antimeridiano).

## Simplificación

Cada dataset registra qué se le hizo:

```json
"simplification": { "method": "visvalingam", "tolerance_m": 100 }
```

`tolerance_m` es una **distancia sobre el terreno**, no un porcentaje. Es
deliberado: un porcentaje conserva una fracción fija de los vértices de cada
archivo, así que la resolución resultante depende de lo densamente que se
hubiera digitalizado la fuente y dos países vecinos acaban con fidelidades
distintas. Una distancia da a todo el repositorio una única resolución real
consistente.

La tolerancia estándar son **100 m**. Las 16 regiones de Chile — una de las
costas más complejas del mundo — miden 49,7 MB a 10 m, 10,0 MB a 50 m, 4,6 MB a
100 m y 1,6 MB a 250 m. Un dataset que aun así superara el presupuesto de
18 MiB con la tolerancia estándar ve su tolerancia duplicada hasta que cabe, y
el valor registrado aquí es siempre el aplicado realmente.

## Quién escribe qué

Tres cosas tocan un manifiesto, y la separación importa porque es lo que hace
segura la regeneración.

| Campo | Lo escribe | Notas |
|---|---|---|
| `schema_version` | cualquiera de los dos scripts, si falta | Se sube a mano solo ante un cambio rompedor de formato |
| `body`, `iso_a3`, `iso_a2`, `m49_region`, `name`, `crs` | **`build_data.py`** | Identidad, tomada de `scripts/countries.json`. Se **sobrescribe** en cada build — edita `countries.json`, no el manifiesto |
| `source.name`, `source.url`, `source.retrieved` | `build_data.py`, si faltan | Las ediciones a mano sobreviven; `retrieved` solo se fija cuando falta |
| `source.license`, `source.licenses` | ambos scripts | Consolidados a partir de `datasets[].license` |
| `status` | `build_data.py`, si falta | Las ediciones a mano sobreviven. `review` cuando `countries.json` marca la entrada como `verify` |
| `notes` | `build_data.py`, si falta | Sembrado desde el `note` de `countries.json`; las ediciones a mano sobreviven |
| `datasets[].simplification`, `license`, `src_provider`, `src_year`, `unassigned` | **`build_data.py`** | Procedencia del build; `build_manifest.py` los arrastra sin cambios |
| todo lo demás en `datasets[]` | **`build_manifest.py`** | Medido desde los archivos: `path`, `bytes`, `sha256`, `features`, `bbox`, `geometry_types`, `properties`, `preview`, `preview_bytes`, `split_by`, `parts` |

`scripts/build_manifest.py` reemplaza el array `datasets` por completo y deja
intacta cualquier otra clave. Los metadatos curados — `status`, `notes`,
`source.retrieved` — sobreviven así a la regeneración, que es lo que hace
seguro reejecutar el escáner de forma rutinaria. Los términos locales
(`adm1_term`, `municipal_term`) **no** están en el manifiesto; viven solo en
`scripts/countries.json`.

## Regenerar

Primero los previews y luego el manifiesto — `build_manifest.py` solo registra
`preview` y `preview_bytes` para un preview que ya exista — y después el
índice, que incrusta el manifiesto:

```bash
node scripts/make_previews.mjs data/earth/CHL
python scripts/build_manifest.py data/earth/CHL
python scripts/build_index.py
```

El escáner streamea cada archivo con `ijson` en memoria constante, así que
incluso el archivo más grande del repositorio (el ADM1 de Canadá, 14,9 MB)
cuesta unos segundos y unas decenas de megabytes de RAM en vez de más de un
gigabyte de objetos Python parseados.

No edites a mano los campos medidos; el CI regenera el manifiesto y el índice
y falla el build si una versión commiteada no coincide.

## Checksums y finales de línea

`sha256` se calcula sobre los bytes crudos del archivo tal como se almacena,
con finales de línea **LF**.

Esto importa más de lo que parece. Git normaliza los finales de línea al hacer
checkout, así que el mismo archivo en Windows con CRLF es un byte por línea más
grande — y, como cada feature va en su propia línea, su hash es completamente
distinto.

El `.gitattributes` del repositorio fija `*.geojson` a `eol=lf` para que los
hashes calculados en Windows, en el CI de Linux y por
`raw.githubusercontent.com` coincidan todos. Si te da un desajuste, revisa tu
configuración de finales de línea de Git antes de sospechar de los datos.

Las páginas del catálogo muestran los primeros 16 caracteres hexadecimales de
cada hash; el manifiesto tiene el valor completo.

## Validación

Cada manifiesto se valida contra
[`schemas/manifest.schema.json`](index-json.md#esquemas) — el mismo JSON Schema
contra el que puede validar un consumidor — y su enum `license` es la
[lista blanca de licencias](../contributing/sources.md), así que hay una única
definición de lo que un manifiesto puede contener. `scripts/validate_data.py`
corre en el CI en cada cambio de `data/`, `schemas/` o `scripts/` y comprueba:

- que cada manifiesto, `data/index.json` y `scripts/countries.json` validan
  contra su esquema, y cada feature de cada archivo a resolución completa
  contra los esquemas de feature;
- que los ids de feature son únicos por archivo y que cada `parentID` apunta a
  un id que existe en el país;
- que el `bbox` de cada archivo es igual a la extensión de sus coordenadas;
- que cada `.geojson` pesa menos de 50 MB, y que cada preview existe y pesa
  menos de 2 MB;
- que los recuentos de features del manifiesto coinciden con los archivos, y
  que las partes de un nivel partido suman exactamente su `features`;
- con `--checksums`, como lo ejecuta el CI, que los `bytes` y el `sha256` de
  cada archivo coinciden con el manifiesto.

Junto a él corren dos comprobaciones más: `finalize_geojson.py --check`
(cada archivo está en forma canónica, con sus ids y su jerarquía) y
`build_index.py --check`, y los manifiestos commiteados deben coincidir con
una regeneración limpia.

## El índice global y los assets de la release

Los manifiestos van incrustados, tal cual, en **`data/index.json`** — un único
archivo de 340 KB para todo el corpus, para que un cliente descubra cada
territorio, nivel y archivo con `bytes`, `sha256`, `bbox` y licencia en una
sola petición en vez de 55. Está documentado en
[Índice global y esquemas](index-json.md), junto a los cinco JSON Schemas.

Las releases etiquetadas distribuyen los mismos archivos de una segunda forma:
un zip por territorio — la carpeta del país con sus archivos, manifiesto y
previews — adjunto a la GitHub Release, más `index.json` y un `SHA256SUMS`.
Ver [Descarga y CDN → Assets de la release](../get-started/download.md#assets-de-la-release).

--8<-- "abbreviations.md"
