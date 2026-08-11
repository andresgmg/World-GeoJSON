# Añadir un país

Runbook completo. Calcula una hora para el primero.

## 0. Verifica la licencia

[Fuentes aprobadas y licencias](sources.md). Hazlo primero — es el paso que más
probablemente detenga la contribución, y todo lo posterior es trabajo perdido
si la fuente resulta inutilizable.

## 1. Preparación

```powershell
git clone https://github.com/andresgmg/World-GeoJSON.git
cd World-GeoJSON
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-docs.txt
git checkout -b add-nzl
```

También necesitas [mapshaper](https://github.com/mbloch/mapshaper), que se
ejecuta con `npx` sin instalar nada. Node 18 o superior.

## 2. Consigue los datos

Usando Nueva Zelanda y geoBoundaries como ejemplo:

```bash
curl -LO https://www.geoboundaries.org/data/geoBoundaries-3_0_0/NZL/ADM1/geoBoundaries-3_0_0-NZL-ADM1.geojson
```

## 3. Normaliza

El detalle completo está en [Pipeline de datos](pipeline.md). La versión corta:

```bash
npx mapshaper geoBoundaries-3_0_0-NZL-ADM1.geojson \
  -rename-fields shapeName=shapeName \
  -each 'shapeGroup="NZL", shapeType="ADM1"' \
  -o precision=0.000001 format=geojson \
     data/earth/NZL/NZL_ADM1.geojson
```

Después contrasta con [Esquema de propiedades](../reference/schema.md):

- `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` en cada feature
- atributos de origen preservados bajo `src_`
- artefactos Esri (`objectid`, `st_area_sh`, …) eliminados
- `shapeISO` es una **cadena**, con ceros a la izquierda si el código oficial
  los lleva

Y con [CRS](../reference/crs.md):

- EPSG:4326 / CRS84, longitud primero
- sin miembro `crs` en el archivo
- coordenadas con 6 decimales o menos
- `bbox` de nivel superior presente

## 4. Escribe el manifiesto

Crea `data/earth/NZL/manifest.json` con los campos escritos a mano. Deja
`datasets` fuera — lo escribe el escáner.

```json
{
  "schema_version": 1,
  "body": "earth",
  "iso_a3": "NZL",
  "iso_a2": "NZ",
  "m49_region": "Australia and New Zealand",
  "name": { "en": "New Zealand", "es": "Nueva Zelanda" },
  "crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 },
  "source": {
    "name": "geoBoundaries",
    "url": "https://www.geoboundaries.org/",
    "license": "CC-BY-4.0",
    "retrieved": "2026-08-10"
  },
  "status": "review"
}
```

!!! tip "Nueva Zelanda cruza el antimeridiano"

    Las Islas Chatham están al este de los 180°. Comprueba que tu geometría
    esté cortada en el antimeridiano en lugar de usar longitudes más allá de
    180, e indícalo en `notes`. Ver
    [CRS](../reference/crs.md#el-antimeridiano).

## 5. Genera manifiesto y preview

```powershell
.\.venv\Scripts\python.exe scripts\build_manifest.py data\earth\NZL
node scripts\make_previews.mjs data/earth/NZL
```

El primero rellena `datasets` con conteos de features, bbox, checksums y listas
de propiedades. El segundo escribe los archivos de preview simplificados — ver
[Simplificación y previews](previews.md) para el presupuesto de tamaño.

## 6. Comprueba que se ve bien

```powershell
.\.venv\Scripts\python.exe -m mkdocs serve
```

Tu país aparece bajo **Catálogo** automáticamente. Confirma que el número de
features es plausible, que el bounding box está en el hemisferio correcto y que
el mapa de preview se parece al país.

## 7. Abre el PR

Repasa antes el [Checklist de revisión](checklist.md).

Tu PR debe contener el archivo o archivos de datos, el manifiesto y los
previews. **No** debe contener páginas de documentación generadas — esas no
existen en disco.

## Añadir un nivel a un país existente

Mismo proceso, sin crear el manifiesto: deja el archivo nuevo en el directorio
existente y vuelve a ejecutar `build_manifest.py`. Reescribe el array
`datasets` y deja intactos los campos curados.

## Corregir geometría existente

Explica qué cambió y por qué en la descripción del PR, y cita la fuente de la
corrección. Los cambios de límites son el cambio con mayor escrutinio de este
repositorio. Si la corrección refleja una reclamación de soberanía y no un
error cartográfico, lee antes
[Fronteras disputadas](../about/disputed-boundaries.md).

--8<-- "abbreviations.md"
