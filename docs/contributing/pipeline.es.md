# Pipeline de datos

Cómo los datos de origen se convierten en un archivo que este repositorio
acepta. Un solo comando, `wgj`, con un subcomando por paso, en este orden:

```
wgj fetch → wgj build → wgj previews → wgj manifest → wgj index → wgj validate
.cache/sources/  data/earth/XXX/  preview/       manifest datasets[]  data/index.json  checks de CI
                 + finalize
```

El orden no es negociable: `wgj manifest` registra la ruta y el tamaño de un
preview solo si el preview ya existe, así que los previews van antes que el
manifiesto; `wgj index` incrusta los manifiestos, así que va después de
ellos. `wgj build` ejecuta él mismo el
[paso de finalización](#el-paso-de-finalizacion), así que un país recién
construido ya lleva sus ids, su jerarquía y su formato canónico antes de que
se recorten los previews — y los previews llevan esos mismos ids.

Con las fuentes ya descargadas, `wgj all ARG` ejecuta los pasos 2 a 6 —
build, previews, manifiesto, índice, validación — para los países que
indiques, y se detiene en el primer fallo. Cada subcomando tiene `--help`, y
`python -m wgj …` es lo mismo que `wgj …`.

## Requisitos

- Python 3.11 o superior (el CI prueba de 3.11 a 3.13 y valida los datos con
  3.12) y `pip install -r requirements-dev.txt`. Eso instala el propio
  pipeline como paquete editable — el archivo contiene
  `-e ./pipeline[pipeline]` — lo que deja el comando `wgj` en tu path, junto
  con sus dependencias (`ijson`, con el que `wgj manifest` lee los archivos en
  streaming en vez de parsearlos enteros, y `jsonschema`, con el que
  `wgj validate` lo comprueba todo contra los esquemas) y la cadena de lint y
  tests. `pip install -e ./pipeline[pipeline]` a secas te da el comando sin la
  cadena de herramientas.
- Node 18 o superior (el CI usa 20) y `npm ci`, que instala la versión de
  mapshaper fijada en `package.json`. Todo el trabajo de geometría se delega
  en él: `wgj build` y `wgj previews` lo ejecutan por debajo.

`just setup` hace las dos cosas si tienes
[`just`](https://github.com/casey/just); el `justfile` también trae `lint`,
`fmt`, `test`, `validate`, `finalize`, `previews`, `manifest`, `index`,
`check-data` (todo lo que el CI comprueba sobre los datos commiteados),
`docs`, `serve` y `ci`.

## 0. Declara el país

`pipeline/src/wgj/tables/countries.json` es el registro que leen todos los
pasos. Un país que no esté ahí no se puede descargar ni construir. El archivo
va dentro del paquete, y como la instalación es editable, cualquier edición
se aplica al momento. La entrada de Argentina:

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
| `source` | Qué proveedor usa `wgj build`: `geoboundaries` o `ide-chile` |
| `municipal_level` | Qué nivel ADM es el tier municipal (`ADM2`, `ADM3` o `ADM4`), o `null` si no se publica ninguno. No se puede inferir de los datos: una comuna chilena es ADM3, un municipio mexicano ADM2 |
| `adm1_term`, `adm2_term`, `municipal_term` | Nombres locales de los niveles, en ambos idiomas. Viven solo aquí, no en los manifiestos |
| `verify` | `true` marca una entrada cuya asignación de niveles o número de unidades no se ha contrastado con una fuente oficial; su manifiesto sale con `status: "review"` |
| `note` | Se copia a `notes` del manifiesto en el primer build. Una sola línea |

## 1. Descarga las fuentes

```bash
wgj fetch --iso3 ARG          # uno o varios países
wgj fetch --continent americas
wgj fetch --continent americas --dry-run
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
wgj build ARG
wgj build --continent americas --skip-existing
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
    los joins posteriores fallen en silencio, y `wgj validate` rechaza el
    archivo.

### El paso de finalización

`wgj finalize` es lo último que hace `wgj build`, y el paso que convierte la
salida de mapshaper en el [contrato de datos](../reference/properties.md). Es
Python puro — sin mapshaper, sin red. Lee los archivos a resolución completa
del país (los combinados de nivel y las partes partidas) y los reescribe para
que cada feature lleve:

- `id` — `{ISO3}:{LEVEL}:{clave}`, según la
  [regla de la clave](../reference/properties.md#el-id-de-la-feature);
- `shapeISO` corregido desde
  `pipeline/src/wgj/tables/shapeiso_fixes.json`, y vaciado a `""` donde la
  fuente entregó su id opaco en vez de un código;
- `adm1ISO`, `parentISO` y `parentID` — la jerarquía, derivada de las partes
  partidas y del nivel superior;
- un `bbox` recalculado desde las coordenadas;

y escribe el archivo en el formato canónico — una feature por línea,
separadores compactos, como máximo 6 decimales — de modo que ejecutarlo dos
veces no cambia nada. Se niega a ejecutarse mientras dos features fueran a
recibir el mismo `id`, y las nombra.

Lo alimentan dos registros. Viven en el directorio `tables/` del paquete,
junto a `countries.json`, y son los dos archivos que un contribuidor puede
tener que editar a mano:

| Registro | Qué contiene |
|---|---|
| `pipeline/src/wgj/tables/shapeiso_fixes.json` | Correcciones a valores de `shapeISO` de origen, indexadas por ISO3, nivel y el `src_shape_id` de la feature (`"*"` señala todas las features de un nivel; el valor `""` vacía el código). Solo errores documentados de la fuente: el valor corregido es el código ISO 3166-2 de la unidad que nombra `shapeName`. Cuatro entradas hoy — `SU-SD` → `US-SD`, `MX-MEX` → `MX-CMX`, `EC-H` → `EC-X`, y los códigos ADM2 de Belice vaciados |
| `pipeline/src/wgj/tables/id_overrides.json` | Claves de `id` manuales, señaladas de la misma forma, con la parte posterior a `{ISO3}:{LEVEL}:` como valor. Para cuando la regla automática colisionaría o induciría a error. Vacío hoy |

No uses ninguno de los dos para inventar un código: una unidad sin código
ISO 3166-2 se queda con `shapeISO: ""` y recibe un `id` basado en el nombre.

El paso también se ejecuta por sí solo, sobre datos ya commiteados:

```bash
wgj finalize data/earth/ARG           # un país
wgj finalize data/earth/*/            # todo
wgj finalize --check data/earth/*/    # CI: sale con 1 si algo está desactualizado
```

Cuando cambia un código ADM1 — una entrada nueva en `shapeiso_fixes.json` —
las partes municipales tienen que seguirlo, porque los archivos de parte se
llaman como la clave del ADM1. `--resplit` vuelve a derivar los padres y las
partes desde los archivos commiteados sin tocar `.cache/sources` (la fuente
puede haber cambiado, y un rebuild completo removería todos los checksums):

```bash
wgj build --resplit USA
wgj finalize data/earth/USA
```

y después previews, manifiesto, índice y validación como siempre. Así es como
`USA/ADM2/SU-SD.geojson` pasó a ser `US-SD.geojson`.

## 3. Previews

```bash
wgj previews data/earth/ARG
wgj previews                                   # todos los países
npm run previews                               # lo mismo, para quien venga de Node
```

Escribe `data/earth/ARG/preview/ARG_{LEVEL}.preview.geojson`, uniendo antes
las partes de los niveles partidos. El comando es Python, pero la
simplificación la hace mapshaper, ejecutado vía Node — de ahí `npm ci`. Cada
feature del preview conserva el `id` de su feature a resolución completa, y
por eso este paso va después de finalize. El detalle y el presupuesto de
tamaño están en [Simplificación y previews](previews.md).

## 4. Manifiesto

```bash
wgj manifest data/earth/ARG
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
wgj index
wgj index --check      # CI: sale con 1 si el archivo commiteado está desactualizado
```

Reconstruye `data/index.json` a partir de todos los manifiestos. Cada cambio
en un manifiesto debe ir seguido de esto, porque el índice los incrusta tal
cual; el CI comprueba que el índice commiteado está al día. Ver
[Índice global y esquemas](../reference/index-json.md).

## 6. Valida

```bash
wgj validate                 # todo
wgj validate data/earth/ARG  # un país
wgj validate --checksums     # además recalcula el hash de cada archivo, como el CI
```

Las mismas comprobaciones que el CI ejecuta en cada pull request que toca
`data/`, `schemas/` o `pipeline/`. Cada manifiesto, `data/index.json`, el
registro de países y cada feature de cada archivo a resolución completa se
valida contra los [JSON Schemas](../reference/index-json.md#esquemas) — que
es donde viven ahora la lista blanca de licencias, las propiedades
obligatorias, `shapeISO` como cadena y el patrón del `id` — más lo que un
esquema no puede expresar: ids de feature únicos por archivo, cada `parentID`
resolviendo a una feature del país, el `bbox` del archivo igual a las
coordenadas, recuentos de features del manifiesto iguales a los archivos,
`parts` sumando el nivel, previews presentes y por debajo de 2 MB, archivos por
debajo de 50 MB, y con `--checksums` cada recuento de bytes y SHA-256
coincidiendo con el manifiesto. Las coordenadas con más de 6 decimales son un
aviso.

El CI ejecuta tres comprobaciones más junto a esta —
`wgj finalize --check data/earth/*/`, `wgj index --check`, y
`wgj manifest data/earth/*/` seguido de `git diff --quiet` para asegurarse de
que los manifiestos commiteados coinciden con una regeneración limpia.
`just check-data` ejecuta las cuatro. El
[Checklist de revisión](checklist.md) dice qué está automatizado y qué
necesita ojos.

Después confirma a ojo lo que ninguna comprobación puede:

- [ ] el número de features coincide con el número oficial de unidades
- [ ] los valores de `shapeName` llevan las tildes correctas y no hay mojibake

El mojibake es lo habitual: un shapefile con `.cpg` ausente o incorrecto
decodifica `Ñuble` como `Ã‘uble`. Si ves una `Ã` en cualquier sitio, la
codificación se leyó mal — vuelve al origen y fuerza UTF-8.

## Construir a mano

Si la fuente es un proveedor que `wgj build` no conoce, los archivos se pueden
producir con ogr2ogr o mapshaper y dejar en `data/earth/XXX/`, y luego
finalizarlos — `wgj finalize data/earth/XXX` les da sus ids, su jerarquía y
su formato canónico — y ejecutar los pasos 3 a 6 como siempre.

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

Dos cosas que `wgj build` habría hecho por ti ahora toca hacerlas a mano:

- **El `license` de cada dataset en el manifiesto.** `wgj manifest` escribe
  `datasets[]` pero no sabe de dónde salieron los archivos, y `wgj validate`
  rechaza cualquier dataset sin un `license` de la lista blanca. Añade
  `license` (y `src_provider`) a cada entrada tras la primera ejecución de
  `wgj manifest`; las siguientes lo arrastran.
- **El bloque de identidad** — `body`, `iso_a3`, `iso_a2`, `m49_region`,
  `name`, `crs`, `source`, `status` — que muestra
  [Añadir un país](add-a-country.md).

El tamaño es la última comprobación: `wgj validate` falla con cualquier
archivo de más de 50 MB, y GitHub rechaza pushes por encima de 100 MB. Antes de
recurrir a Git LFS — [no lo hagas](../about/versioning.md#por-que-no-git-lfs)
— confirma que el archivo está simplificado y recortado a 6 decimales, y
pártelo por ADM1 si sigue siendo demasiado grande.

## Dónde vive el código

El pipeline es el paquete Python `wgj` bajo `pipeline/` —
`pipeline/pyproject.toml` y `pipeline/src/wgj/` — con un módulo por
responsabilidad:

| Módulo | Función |
|---|---|
| `wgj.cli` | El comando `wgj`: un subcomando por paso, más `all` |
| `wgj.paths` | Dónde vive cada cosa; `WGJ_DATA` apunta el paquete a otro árbol de datos |
| `wgj.registry` | Carga las tablas de `pipeline/src/wgj/tables/` — `countries.json`, `shapeiso_fixes.json`, `id_overrides.json`, `iso3166_2.json` |
| `wgj.licensing` | El texto de licencia de origen mapeado a ids SPDX, y la lista blanca |
| `wgj.levels`, `wgj.text` | Los niveles ADM y los nombres de archivo construidos sobre ellos; pequeños helpers de texto |
| `wgj.geojson_io` | Lectura en streaming, SHA-256, el escritor canónico |
| `wgj.mapshaper`, `wgj.simplify` | El subproceso de mapshaper; la regla de tolerancia y su presupuesto de tamaño |
| `wgj.sources.natural_earth`, `wgj.sources.geoboundaries`, `wgj.sources.ide_chile` | Un módulo por proveedor |
| `wgj.fetch`, `wgj.build`, `wgj.finalize`, `wgj.previews`, `wgj.manifest`, `wgj.index`, `wgj.validate` | Los seis pasos de arriba, en orden |
| `wgj.schema` | Los JSON Schemas de `schemas/`, cargados una vez con sus `$ref` resueltos en local |
| `wgj.catalog` | El hook de MkDocs que genera las páginas del catálogo; `pipeline/mkdocs_hook.py` lo reexporta, así que construir la documentación no requiere instalar nada |

Los tests están en `pipeline/tests/` y se ejecutan con `pytest` desde la raíz
del repositorio. No necesitan un checkout de los datos: `fixtures/data/`
contiene tres territorios pequeños — Aruba, Barbados y una República
Dominicana reducida — más su `index.json`, y la suite apunta el paquete a él
con `WGJ_DATA`. Define `WGJ_DATA=<dir>` tú mismo para ejecutar cualquier
comando `wgj` contra otro árbol de datos.

Los puntos de entrada `scripts/*.py` anteriores al paquete se mantuvieron
como shims durante una release y se retiraron en la Fase 4; `wgj` es el único
punto de entrada.

--8<-- "abbreviations.md"
