# Formato del manifiesto

Cada directorio de dataset contiene un `manifest.json`. Es la **única** entrada
de este sitio de documentación: todas las páginas del catálogo se generan a
partir de él. Hoy hay 55, uno por territorio bajo `data/earth/`.

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
      "bytes": 407930,
      "sha256": "18e57932e64371abccbc383c486af4111243c4974b5098bb04ee86fb8cebac79",
      "features": 1,
      "bbox": [-109.453725, -55.918504, -66.420806, -17.506588],
      "geometry_types": { "MultiPolygon": 1 },
      "properties": ["shapeGroup", "shapeISO", "shapeName", "shapeType"],
      "preview": "data/earth/CHL/preview/CHL_ADM0.preview.geojson",
      "preview_bytes": 18782,
      "simplification": { "method": "visvalingam", "tolerance_m": 100 },
      "license": "public-domain",
      "src_provider": "Natural Earth"
    },
    {
      "level": "ADM1",
      "path": "data/earth/CHL/CHL_ADM1.geojson",
      "bytes": 4814221,
      "sha256": "5cf4e9d8d34822d498cc61ddea063bd4381671d9d05568b49bb3e2f40f9b44b8",
      "features": 16,
      "bbox": [-109.449861, -56.525107, -66.416176, -17.498399],
      "geometry_types": { "MultiPolygon": 10, "Polygon": 6 },
      "properties": ["shapeGroup", "shapeISO", "shapeName", "shapeType",
                     "src_cut_reg", "src_superficie_km2"],
      "preview": "data/earth/CHL/preview/CHL_ADM1.preview.geojson",
      "preview_bytes": 226499,
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
| `properties` | Todas las claves de propiedad presentes en alguna feature, **ordenadas** |
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
  "bytes": 6965828,
  "features": 345,
  "properties": ["adm1ISO", "parentISO", "shapeGroup", "shapeISO", "shapeName",
                 "shapeType", "src_cut_com", "src_cut_prov", "src_cut_reg",
                 "src_provincia", "src_region"],
  "preview": "data/earth/CHL/preview/CHL_ADM3.preview.geojson",
  "split_by": "ADM1",
  "license": "CC-BY-4.0",
  "parts": [
    {
      "code": "CL-AI",
      "path": "data/earth/CHL/ADM3/CL-AI.geojson",
      "bytes": 1281188,
      "sha256": "3e55fb5694854d124580a8625dbe4d6a9b6b34a0810675130bed701532aafe0c",
      "features": 10,
      "bbox": [-75.64927, -49.158776, -71.091675, -43.637991],
      "geometry_types": { "MultiPolygon": 4, "Polygon": 6 },
      "properties": ["adm1ISO", "parentISO", "shapeGroup", "shapeISO", "shapeName",
                     "shapeType", "src_cut_com", "src_cut_prov", "src_cut_reg",
                     "src_provincia", "src_region"]
    }
  ]
}
```

- `features` en la entrada es el **nivel completo**, para que el catálogo pueda
  dar siempre un total exista o no un archivo combinado.
- `path` es el archivo de país completo, opcional, presente solo cuando cabe
  bajo el presupuesto de 18 MiB. El ADM2 de Brasil tiene 28 partes y ningún
  `path`; su ausencia es normal y el catálogo lo indica.
- `code` es el código ADM1 tal como lo entrega la fuente — errores incluidos.
  El manifiesto de USA tiene una parte codificada `SU-SD` (la errata de
  geoBoundaries para Dakota del Sur), y su `notes` lo explica. Una parte
  codificada `unassigned` contiene las unidades a las que no se encontró
  padre; la entrada ADM2 de USA lleva además `"unassigned": 1`.

El CI comprueba que las partes sumen exactamente el número de features del
nivel — así es como se detecta una partición que perdió o duplicó un municipio.

!!! warning "`bbox` es un mínimo/máximo ingenuo"

    El `bbox` del manifiesto es el simple mínimo y máximo de cada coordenada.
    Para un territorio que cruza el antimeridiano eso es casi el globo entero:
    las entradas de USA leen `[-179,14…, 18,90…, 179,78…, 71,41…]`. Los
    propios archivos GeoJSON los escribe mapshaper y siguen en cambio la
    RFC 7946 §5.2 — `USA_ADM0.geojson` lleva `[172,47…, 18,90…, -66,97…,
    71,41…]`, con oeste mayor que este. Para esos países ajusta el mapa al
    `bbox` del archivo, no al del manifiesto. Ver
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
`preview` y `preview_bytes` para un preview que ya exista:

```bash
node scripts/make_previews.mjs data/earth/CHL
python scripts/build_manifest.py data/earth/CHL
```

El escáner streamea cada archivo con `ijson` en memoria constante, así que
incluso el archivo más grande del repositorio (el ADM1 de Canadá, 14,9 MB)
cuesta unos segundos y unas decenas de megabytes de RAM en vez de más de un
gigabyte de objetos Python parseados.

No edites a mano los campos medidos; el CI regenera el manifiesto y falla el
build si la versión commiteada no coincide.

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

`scripts/validate_data.py` corre en el CI en cada PR que toque `data/` y
comprueba:

- que cada `.geojson` pesa menos de 50 MB y cada preview menos de 2 MB;
- que cada archivo tiene un `bbox` de nivel superior y las cuatro propiedades
  obligatorias;
- que `source.license` — o cada entrada de `source.licenses` cuando es
  `"mixed"` — y cada `datasets[].license` están en la
  [lista aprobada](../contributing/sources.md);
- que las partes de un nivel partido suman exactamente su `features`;
- que el manifiesto commiteado coincide con una regeneración limpia.

## Previsto: un índice global y esquemas

Dos cosas que los manifiestos todavía no te dan, ambas programadas para v1.0.0:

- **`data/index.json`** — un único archivo que enumera cada territorio, nivel
  y archivo con `bytes`, `sha256`, `bbox` y licencia, para que un cliente pueda
  descubrir todo el corpus con una sola petición en vez de 55.
- **JSON Schemas** en `schemas/` para el manifiesto, el índice y las
  propiedades de las features, para que pipeline y consumidores validen contra
  la misma definición.

Ver la [Hoja de ruta](../about/roadmap.md).

--8<-- "abbreviations.md"
