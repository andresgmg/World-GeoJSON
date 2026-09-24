# Pipeline de datos

Cómo los datos de origen se convierten en un archivo que este repositorio
acepta. Cinco scripts, en este orden:

```
fetch_sources.py → build_data.py → make_previews.mjs → build_manifest.py → validate_data.py
.cache/sources/    data/earth/XXX/   preview/            manifest datasets[]   checks de CI
```

El orden no es negociable: `build_manifest.py` registra la ruta y el tamaño de
un preview solo si el preview ya existe, así que los previews van antes que el
manifiesto.

## Requisitos

- Python 3.11 o superior (el CI usa 3.12) y `pip install ijson` —
  `build_manifest.py` lee los archivos en streaming en vez de parsearlos
  enteros. `requirements-docs.txt` lo incluye.
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
  un ADM1, añadiendo `adm1ISO` a cada parte. Las features cuyo padre no se
  puede determinar acaban en `{LEVEL}/unassigned.geojson`;
- escribe la identidad, `source` y `status` del manifiesto, y `license` y
  `simplification` de cada dataset.

A `data/` solo llega la salida de mapshaper; nada va con indentación. El
formato de 14 decimales y cuatro espacios existe únicamente en los archivos
heredados de la raíz.

!!! danger "Rellena los códigos con ceros, como cadenas"

    `shapeISO` debe ser una cadena. Los códigos oficiales llevan con
    frecuencia ceros a la izquierda que un número JSON no puede representar —
    Camiña, en Chile, es `01402`, no `1402`. Equivocarse aquí hace que todos
    los joins posteriores fallen en silencio, y `validate_data.py` rechaza el
    archivo.

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
número de features, bbox, tipos de geometría, lista de propiedades, preview y
su tamaño, y para los niveles partidos las `parts`. Todo lo que está fuera de
`datasets` se preserva tal cual, y las claves por dataset que no calcula él
mismo (`license`, `src_provider`, `simplification`) se arrastran de la
ejecución anterior. Ver [Formato del manifiesto](../reference/manifest.md).

## 5. Valida

```bash
python scripts/validate_data.py                 # todo
python scripts/validate_data.py data/earth/ARG  # un país
```

Las mismas comprobaciones que el CI ejecuta en cada pull request que toca
`data/`: claves del manifiesto, la lista blanca de licencias, que las `parts`
sumen el número de features del nivel, previews por debajo de 2 MB, archivos
por debajo de 50 MB, `FeatureCollection` con `bbox` y sin `crs`, las cuatro
propiedades obligatorias en cada feature, `shapeISO` como cadena. Las
coordenadas con más de 6 decimales son un aviso. El
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
ejecutar los pasos 3 a 5 como siempre.

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
