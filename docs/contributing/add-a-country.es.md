# Añadir un país

Runbook completo. Calcula una hora para el primero. Los scripts hacen casi
todo el trabajo; el orden importa — previews antes que manifiesto.

## 0. Verifica la licencia

[Fuentes aprobadas y licencias](sources.md). Hazlo primero — es el paso que más
probablemente detenga la contribución, y todo lo posterior es trabajo perdido
si la fuente resulta inutilizable. `fetch_sources.py --dry-run` (paso 3) te
dice qué ofrece geoBoundaries para un país y con qué licencia, sin descargar
nada.

## 1. Preparación

```bash
git clone https://github.com/andresgmg/World-GeoJSON.git
cd World-GeoJSON
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r requirements-docs.txt                 # mkdocs + ijson
npm install                                          # mapshaper, fijado
git checkout -b add-nzl
```

Python 3.11 o superior, Node 18 o superior.

## 2. Decláralo en el registro

Añade una entrada a `scripts/countries.json`. Usando Nueva Zelanda y
geoBoundaries como ejemplo:

```json
"NZL": {
  "iso_a2": "NZ",
  "m49_region": "Australia and New Zealand",
  "name": { "en": "New Zealand", "es": "Nueva Zelanda" },
  "adm1_term": { "en": "Region", "es": "Región" },
  "municipal_level": "ADM2",
  "municipal_term": { "en": "Territorial authority", "es": "Autoridad territorial" },
  "source": "geoboundaries",
  "verify": true,
  "note": "The Chatham Islands sit east of 180°; geometry is cut at the antimeridian."
}
```

`municipal_level` es el único campo que tienes que investigar: qué nivel ADM
es el tier municipal es un hecho sobre el país, no algo que los datos revelen.
`verify: true` hace que el manifiesto salga con `status: "review"` hasta que
alguien contraste la asignación de niveles y el número de unidades con una
fuente oficial. [Pipeline de datos](pipeline.md#0-declara-el-pais) documenta
todos los campos.

## 3. Descarga las fuentes

```bash
python scripts/fetch_sources.py --iso3 NZL --dry-run
python scripts/fetch_sources.py --iso3 NZL
```

El dry run lista cada nivel con su licencia y número de unidades y marca lo
que se rechaza. Nada copyleft llega a tu disco. Los archivos aceptados acaban
en `.cache/sources/`, que está en `.gitignore`.

## 4. Construye los datos

```bash
python scripts/build_data.py NZL
```

Escribe `data/earth/NZL/NZL_ADM0.geojson`, `NZL_ADM1.geojson`, … —
reproyectados, renombrados al [esquema estándar](../reference/schema.md),
simplificados a una tolerancia de 100 m, partidos por ADM1 donde el tier
municipal lo necesite — y la identidad y procedencia del manifiesto. Antes de
los dos pasos siguientes el manifiesto se ve así, con `license` y
`simplification` ya en cada entrada de `datasets`:

```json
{
  "schema_version": 1,
  "body": "earth",
  "iso_a3": "NZL",
  "iso_a2": "NZ",
  "m49_region": "Australia and New Zealand",
  "name": { "en": "New Zealand", "es": "Nueva Zelanda" },
  "crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 },
  "status": "review",
  "source": {
    "name": "geoBoundaries (gbOpen)",
    "url": "https://www.geoboundaries.org/",
    "license": "CC-BY-4.0",
    "retrieved": "2026-09-24"
  },
  "notes": "The Chatham Islands sit east of 180°; geometry is cut at the antimeridian."
}
```

`status`, `notes` y `name`, `url` y `retrieved` del bloque `source` solo se
rellenan si faltan, así que puedes editarlos y volver a ejecutar sin miedo.
`iso_a2`, `m49_region` y `crs` se sobrescriben desde el registro — cámbialos
ahí.

!!! tip "Nueva Zelanda cruza el antimeridiano"

    Las Islas Chatham están al este de los 180°. Comprueba que la salida esté
    cortada en el antimeridiano en lugar de usar longitudes más allá de 180,
    e indícalo en `notes`. Ver [CRS](../reference/crs.md#el-antimeridiano).

## 5. Genera los previews

```bash
node scripts/make_previews.mjs data/earth/NZL
```

Antes del manifiesto, no después: `build_manifest.py` registra un preview solo
si ya existe. Ver [Simplificación y previews](previews.md) para el presupuesto
de tamaño.

## 6. Genera el manifiesto

```bash
python scripts/build_manifest.py data/earth/NZL
```

Rellena `datasets` con rutas, tamaños, checksums, número de features, bounding
boxes, listas de propiedades y tamaños de preview. Los campos escritos a mano
se dejan intactos.

## 7. Valida

```bash
python scripts/validate_data.py data/earth/NZL
```

Cero errores antes de abrir el PR. Los avisos — un dataset sin preview,
coordenadas con más de 6 decimales — no hacen fallar el CI, pero sí reciben
comentarios de revisión.

## 8. Comprueba que se ve bien

```bash
mkdocs serve
```

Tu país aparece bajo **Catálogo** automáticamente. Confirma que el número de
features es plausible, que el bounding box está en el hemisferio correcto y que
el mapa de preview se parece al país.

## 9. Abre el PR

Repasa antes el [Checklist de revisión](checklist.md).

Tu PR debe contener la entrada del registro, el archivo o archivos de datos,
el manifiesto y los previews. **No** debe contener nada de `.cache/` ni
páginas de documentación generadas — para git, ninguna de las dos cosas
existe.

## Añadir un nivel a un país existente

Vuelve a ejecutar los pasos 3 a 7 para ese país. `build_data.py` deja intactos
los campos escritos a mano del manifiesto; `build_manifest.py` reescribe
`datasets` y arrastra el `license` de cada entrada.

## Una fuente que los scripts no conocen

Si los datos del país vienen de un SDI nacional y no de geoBoundaries,
construye los archivos con mapshaper u ogr2ogr como describe
[Pipeline de datos](pipeline.md#construir-a-mano), déjalos en
`data/earth/XXX/` y ejecuta los pasos 5 a 7. Después añade `license` a mano a
cada entrada de `datasets` — `validate_data.py` rechaza un dataset sin él, y
solo `build_data.py` lo escribe — más el bloque de identidad del paso 4.
Enseñar el nuevo proveedor a `build_data.py` es la mejor contribución si
esperas repetirlo.

## Corregir geometría existente

Explica qué cambió y por qué en la descripción del PR, y cita la fuente de la
corrección. Los cambios de límites son el cambio con mayor escrutinio de este
repositorio. Si la corrección refleja una reclamación de soberanía y no un
error cartográfico, lee antes
[Fronteras disputadas](../about/disputed-boundaries.md).

--8<-- "abbreviations.md"
