# Pipeline de datos

Cómo los datos de origen se convierten en un archivo que este repositorio
acepta. Seis scripts, en este orden:

```
fetch_sources.py → build_data.py → make_previews.mjs → build_manifest.py → build_index.py → validate_data.py
.cache/sources/    data/earth/XXX/   preview/            manifest datasets[]   data/index.json    checks de CI
                   + finalize
```

El orden no es negociable: `build_manifest.py` registra la ruta y el tamaño de
un preview solo si el preview ya existe, así que los previews van antes que el
manifiesto; `build_index.py` incrusta los manifiestos, así que va después de
ellos. `build_data.py` ejecuta él mismo el
[paso de finalización](#el-paso-de-finalizacion), así que un país recién
construido ya lleva sus ids, su jerarquía y su formato canónico antes de que
se recorten los previews.

## Requisitos

- Python 3.11 o superior (el CI usa 3.12) y `pip install -r
  requirements-dev.txt` — `ijson`, con el que `build_manifest.py` lee los
  archivos en streaming en vez de parsearlos enteros, y `jsonschema`, con el
  que `validate_data.py` lo comprueba todo contra los esquemas.
- Node 18 o superior (el CI usará 20) y `npm install`, que fija mapshaper
  0.6.109. Todo el trabajo de geometría se delega en él.

## 0. Declara el país

`scripts/countries.json` es el registro que leen todos los scripts. Un país
que no esté ahí no se puede descargar ni construir. La entrada de Argentina:

```json
"ARG": {
  "iso_a2": "AR",
  "m49_region": "South America",
  "name": { "en": "Argentina", "es": "Argentina" },
  "adm1_term": { "en": "Province", "es": "Provincia" },
  "municipal_level": "ADM2",
  "municipal_term": { "en": "Department", "es": "Departamento" },
  "source": "geoboundaries"
}
```

| Campo | Significado |
|---|---|
| `iso_a2`, `m49_region`, `name` | Identidad, copiada al manifiesto |
| `source` | Qué proveedor usa `build_data.py`: `geoboundaries` o `ide-chile` |
| `municipal_level` | Qué nivel ADM es el tier municipal (`ADM2`, `ADM3` o `ADM4`), o `null` si no se publica ninguno. No se puede inferir de los datos: una comuna chilena es ADM3, un municipio mexicano ADM2 |
| `adm1_term`, `adm2_term`, `municipal_term` | Nombres locales de los niveles, en ambos idiomas. Viven solo aquí, no en los manifiestos |
| `verify` | `true` marca una entrada cuya asignación de niveles o número de unidades no se ha contrastado con una fuente oficial; su manifiesto sale con `status: "review"` |
| `note` | Se copia a `notes` del manifiesto en el primer build. Una sola línea |

## 1. Descarga las fuentes

```bash
python scripts/fetch_sources.py --iso3 ARG          # uno o varios países
python scripts/fetch_sources.py --continent americas
python scripts/fetch_sources.py --continent americas --dry-run
```

Descarga a `.cache/sources/`, que está en `.gitignore`. El archivo admin-0 de
Natural Earth a 10m aporta el contorno de todos los países; la publicación
gbOpen de geoBoundaries aporta ADM1 y niveles inferiores, por país y nivel
desde `https://www.geoboundaries.org/api/current/gbOpen/{ISO3}/{LEVEL}/`; los
niveles subnacionales de Chile vienen del paquete DPA 2023 de IDE Chile /
SUBDERE.

**El filtro de licencias vive aquí, a propósito.** gbOpen es un contenedor de
licencias de origen heterogéneas, no un dataset uniformemente CC BY 4.0: un
tercio de sus entradas de América son ODbL o CC-BY-SA. Esas se rechazan antes
de llegar al working tree, y ni hablar del historial de git. `--dry-run`
muestra qué se aceptaría y qué se rechazaría sin descargar nada.

## 2. Construye los datos

```bash
python scripts/build_data.py ARG
python scripts/build_data.py --continent americas --skip-existing
```

Lee la caché y escribe `data/earth/ARG/`. Para cada nivel:

- reproyecta a WGS 84 y escribe GeoJSON RFC 7946 — `bbox` de nivel superior,
  sin miembro `crs`;
- renombra los campos de origen al [esquema estándar](../reference/schema.md)
  (`shapeName`, `shapeISO`, `shapeGroup`, `shapeType`) y conserva el resto
  con prefijo `src_` — el id opaco de geoBoundaries pasa a ser
  `src_shape_id`;
- simplifica a una **tolerancia de 100 m sobre el terreno** (Visvalingam),
  duplicándola solo cuando un archivo superaría 18 MiB, y registra lo aplicado
  en el bloque `simplification` del manifiesto;
- escribe coordenadas con 6 decimales, una feature por línea;
- parte el tier municipal por ADM1 en `{LEVEL}/{código}.geojson` cuando existe
  un ADM1. Las features cuyo padre no se puede determinar acaban en
  `{LEVEL}/unassigned.geojson`;
- escribe la identidad, `source` y `status` del manifiesto, y `license` y
  `simplification` de cada dataset;
- **finaliza** cada archivo que escribió — ids, jerarquía, correcciones de
  `shapeISO`, bbox, formato canónico. Ver la sección siguiente.

Nada bajo `data/` va con indentación: el paso de finalización reescribe la
salida de mapshaper en un único formato canónico. El formato de 14 decimales y
cuatro espacios existe únicamente en los archivos heredados de la raíz.

!!! danger "Rellena los códigos con ceros, como cadenas"

    `shapeISO` debe ser una cadena. Los códigos oficiales llevan con
    frecuencia ceros a la izquierda que un número JSON no puede representar —
    Camiña, en Chile, es `01402`, no `1402`. Equivocarse aquí hace que todos
    los joins posteriores fallen en silencio, y `validate_data.py` rechaza el
    archivo.

### El paso de finalización

`scripts/finalize_geojson.py` es lo último que hace `build_data.py`, y el paso
que convierte la salida de mapshaper en el
[contrato de datos](../reference/properties.md). Es Python puro — sin
mapshaper, sin red. Lee los archivos a resolución completa del país (los
combinados de nivel y las partes partidas) y los reescribe para que cada
feature lleve:

- `id` — `{ISO3}:{LEVEL}:{clave}`, según la
  [regla de la clave](../reference/properties.md#el-id-de-la-feature);
- `shapeISO` corregido desde `scripts/shapeiso_fixes.json`, y vaciado a `""`
  donde la fuente entregó su id opaco en vez de un código;
- `adm1ISO`, `parentISO` y `parentID` — la jerarquía, derivada de las partes
  partidas y del nivel superior;
- un `bbox` recalculado desde las coordenadas;

y escribe el archivo en el formato canónico — una feature por línea,
separadores compactos, como máximo 6 decimales — de modo que ejecutarlo dos
veces no cambia nada. Se niega a ejecutarse mientras dos features fueran a
recibir el mismo `id`, y las nombra.

Lo alimentan dos registros. Son los dos archivos que un contribuidor puede
tener que editar a mano:

| Registro | Qué contiene |
|---|---|
| `scripts/shapeiso_fixes.json` | Correcciones a valores de `shapeISO` de origen, indexadas por ISO3, nivel y el `src_shape_id` de la feature (`"*"` señala todas las features de un nivel; el valor `""` vacía el código). Solo errores documentados de la fuente: el valor corregido es el código ISO 3166-2 de la unidad que nombra `shapeName`. Cuatro entradas hoy — `SU-SD` → `US-SD`, `MX-MEX` → `MX-CMX`, `EC-H` → `EC-X`, y los códigos ADM2 de Belice vaciados |
| `scripts/id_overrides.json` | Claves de `id` manuales, señaladas de la misma forma, con la parte posterior a `{ISO3}:{LEVEL}:` como valor. Para cuando la regla automática colisionaría o induciría a error. Vacío hoy |

No uses ninguno de los dos para inventar un código: una unidad sin código
ISO 3166-2 se queda con `shapeISO: ""` y recibe un `id` basado en el nombre.

El paso también se ejecuta por sí solo, sobre datos ya commiteados:

```bash
python scripts/finalize_geojson.py data/earth/ARG           # un país
python scripts/finalize_geojson.py data/earth/*/            # todo
python scripts/finalize_geojson.py --check data/earth/*/    # CI: sale con 1 si algo está desactualizado
```

Cuando cambia un código ADM1 — una entrada nueva en `shapeiso_fixes.json` —
las partes municipales tienen que seguirlo, porque los archivos de parte se
llaman como la clave del ADM1. `--resplit` vuelve a derivar los padres y las
partes desde los archivos commiteados sin tocar `.cache/sources` (la fuente
puede haber cambiado, y un rebuild completo removería todos los checksums):

```bash
python scripts/build_data.py --resplit USA
python scripts/finalize_geojson.py data/earth/USA
```

y después previews, manifiesto, índice y validación como siempre. Así es como
`USA/ADM2/SU-SD.geojson` pasó a ser `US-SD.geojson`.

## 3. Previews

```bash
node scripts/make_previews.mjs data/earth/ARG
npm run previews                                   # todos los países
```

Escribe `data/earth/ARG/preview/ARG_{LEVEL}.preview.geojson`, uniendo antes
las partes de los niveles partidos. El detalle y el presupuesto de tamaño están
en [Simplificación y previews](previews.md).

## 4. Manifiesto

```bash
python scripts/build_manifest.py data/earth/ARG
```

Escanea el directorio y escribe el array `datasets` — ruta, bytes, SHA-256,
número de features, bbox, tipos de geometría, lista de propiedades (campos de
jerarquía incluidos), preview y su tamaño, y para los niveles partidos las
`parts`. Todo lo que está fuera de `datasets` se preserva tal cual, y las
claves por dataset que no calcula él mismo (`license`, `src_provider`,
`simplification`) se arrastran de la ejecución anterior. Ver
[Formato del manifiesto](../reference/manifest.md).

## 5. Índice

```bash
python scripts/build_index.py
python scripts/build_index.py --check      # CI: sale con 1 si el archivo commiteado está desactualizado
```

Reconstruye `data/index.json` a partir de todos los manifiestos. Cada cambio
en un manifiesto debe ir seguido de esto, porque el índice los incrusta tal
cual; el CI comprueba que el índice commiteado está al día. Ver
[Índice global y esquemas](../reference/index-json.md).

## 6. Valida

```bash
python scripts/validate_data.py                 # todo
python scripts/validate_data.py data/earth/ARG  # un país
python scripts/validate_data.py --checksums     # además recalcula el hash de cada archivo, como el CI
```

Las mismas comprobaciones que el CI ejecuta en cada pull request que toca
`data/`, `schemas/` o `scripts/`. Cada manifiesto, `data/index.json`,
`scripts/countries.json` y cada feature de cada archivo a resolución completa
se valida contra los [JSON Schemas](../reference/index-json.md#esquemas) —
que es donde viven ahora la lista blanca de licencias, las propiedades
obligatorias, `shapeISO` como cadena y el patrón del `id` — más lo que un
esquema no puede expresar: ids de feature únicos por archivo, cada `parentID`
resolviendo a una feature del país, el `bbox` del archivo igual a las
coordenadas, recuentos de features del manifiesto iguales a los archivos,
`parts` sumando el nivel, previews presentes y por debajo de 2 MB, archivos por
debajo de 50 MB, y con `--checksums` cada recuento de bytes y SHA-256
coincidiendo con el manifiesto. Las coordenadas con más de 6 decimales son un
aviso.

El CI ejecuta dos comprobaciones más junto a esta — `finalize_geojson.py
--check data/earth/*/` y `build_index.py --check` — y regenera los
manifiestos para asegurarse de que los commiteados coinciden. El
[Checklist de revisión](checklist.md) dice qué está automatizado y qué
necesita ojos.

Después confirma a ojo lo que ningún script puede:

- [ ] el número de features coincide con el número oficial de unidades
- [ ] los valores de `shapeName` llevan las tildes correctas y no hay mojibake

El mojibake es lo habitual: un shapefile con `.cpg` ausente o incorrecto
decodifica `Ñuble` como `Ã‘uble`. Si ves una `Ã` en cualquier sitio, la
codificación se leyó mal — vuelve al origen y fuerza UTF-8.

## Construir a mano

Si la fuente es un proveedor que `build_data.py` no conoce, los archivos se
pueden producir con ogr2ogr o mapshaper y dejar en `data/earth/XXX/`, y luego
finalizarlos — `python scripts/finalize_geojson.py data/earth/XXX` les da sus
ids, su jerarquía y su formato canónico — y ejecutar los pasos 3 a 6 como
siempre.

=== "ogr2ogr"

    ```bash
    ogr2ogr -f GeoJSON \
      -t_srs EPSG:4326 \
      -lco RFC7946=YES \
      -lco COORDINATE_PRECISION=6 \
      -lco WRITE_BBOX=YES \
      salida.geojson entrada.shp
    ```

    `-lco RFC7946=YES` importa: sin él, GDAL escribe el dialecto del borrador
    de 2008, que permite un miembro `crs` y usa reglas de orientación
    distintas.

=== "mapshaper"

    ```bash
    npx mapshaper entrada.shp \
      -proj wgs84 \
      -rename-fields shapeName=NOMBRE,src_codigo=CODIGO \
      -each 'shapeGroup="XXX", shapeType="ADM1", shapeISO=String(src_codigo).padStart(2,"0")' \
      -filter-fields shapeName,shapeISO,shapeGroup,shapeType,src_codigo \
      -o precision=0.000001 bbox format=geojson data/earth/XXX/XXX_ADM1.geojson
    ```

Verifica la proyección en vez de suponerla — un shapefile con un `.prj`
ausente o incorrecto pasa sin cambios y deja tu país en el Golfo de Guinea.
`npx mapshaper -i salida.geojson -info` debe mostrar coordenadas en el rango
−180…180 / −90…90 y en el hemisferio correcto. Comprueba cualquier país con
territorio cerca del antimeridiano o de los polos: RFC 7946 exige orientación
según la regla de la mano derecha y geometrías cortadas en los 180°.

Dos cosas que `build_data.py` habría hecho por ti ahora toca hacerlas a mano:

- **El `license` de cada dataset en el manifiesto.** `build_manifest.py`
  escribe `datasets[]` pero no sabe de dónde salieron los archivos, y
  `validate_data.py` rechaza cualquier dataset sin un `license` de la lista
  blanca. Añade `license` (y `src_provider`) a cada entrada tras la primera
  ejecución de `build_manifest.py`; las siguientes lo arrastran.
- **El bloque de identidad** — `body`, `iso_a3`, `iso_a2`, `m49_region`,
  `name`, `crs`, `source`, `status` — que muestra
  [Añadir un país](add-a-country.md).

El tamaño es la última comprobación: `validate_data.py` falla con cualquier
archivo de más de 50 MB, y GitHub rechaza pushes por encima de 100 MB. Antes de
recurrir a Git LFS — [no lo hagas](../about/versioning.md#por-que-no-git-lfs)
— confirma que el archivo está simplificado y recortado a 6 decimales, y
pártelo por ADM1 si sigue siendo demasiado grande.

--8<-- "abbreviations.md"
