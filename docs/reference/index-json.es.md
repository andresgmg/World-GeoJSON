# Índice global y esquemas

`data/index.json` es el catálogo entero en un solo archivo: cada territorio y
cada dataset, con el [manifiesto](manifest.md) de cada país incrustado tal
cual. Una petición en vez de cincuenta y cinco, y el punto de entrada que
leen las [bibliotecas cliente](../libraries/index.md).

## Qué es

`wgj index` recorre los manifiestos y escribe un único documento
JSON que los contiene, más unos pocos campos derivados que un cliente necesita
antes de haber descargado nada: los niveles publicados, las licencias que
realmente rigen los archivos, qué nivel es el tier municipal y cómo se llaman
los niveles localmente. Como los manifiestos van incrustados y no resumidos, el
índice nunca puede discrepar de un manifiesto — y el CI lo regenera en cada
cambio (`wgj index --check`) para asegurarse de que la copia commiteada
está al día.

## Forma

```json
{
  "schema_version": 1,
  "bodies": ["earth"],
  "totals": { "countries": 55, "datasets": 95, "features": 16195, "bytes": 125679933 },
  "countries": [ … ]
}
```

| Clave | Significado |
|---|---|
| `schema_version` | Versión del formato del índice. `1` hoy |
| `bodies` | Los cuerpos con datos: `["earth"]` hasta que lleguen la Luna y Marte |
| `totals` | `countries`, `datasets`, `features` y `bytes` de datos a resolución completa en todo el corpus |
| `countries` | Una entrada por territorio, ordenadas por `body` y después `iso_a3` |

### Por país (`countries[]`)

La entrada de Chile, con los datasets abreviados:

```json
{
  "body": "earth",
  "iso_a3": "CHL",
  "iso_a2": "CL",
  "m49_region": "South America",
  "name": { "en": "Chile", "es": "Chile" },
  "status": "ok",
  "manifest": "data/earth/CHL/manifest.json",
  "license": "mixed",
  "licenses": ["CC-BY-4.0", "public-domain"],
  "levels": ["ADM0", "ADM1", "ADM2", "ADM3"],
  "municipal_level": "ADM3",
  "terms": {
    "adm1": { "en": "Region", "es": "Región" },
    "adm2": { "en": "Province", "es": "Provincia" },
    "municipal": { "en": "Commune", "es": "Comuna" }
  },
  "crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 },
  "source": {
    "name": "IDE Chile / SUBDERE — División Política Administrativa 2023",
    "url": "https://www.geoportal.cl/",
    "license": "mixed",
    "retrieved": "2026-08-11",
    "licenses": ["CC-BY-4.0", "public-domain"]
  },
  "datasets": [ … ]
}
```

| Campo | Significado |
|---|---|
| `body`, `iso_a3`, `iso_a2`, `m49_region`, `name`, `status` | Identidad, copiada del manifiesto |
| `manifest` | Ruta del manifiesto, relativa a la raíz del repositorio |
| `license`, `licenses` | Consolidado de `datasets[].license`: el valor único, o `"mixed"`, y los valores distintos ordenados |
| `levels` | Los niveles publicados, en orden |
| `municipal_level` | Qué nivel es el tier municipal, o `null` si no se publica ninguno |
| `terms` | Nombres locales de los niveles en ambos idiomas — `adm1`, `adm2` donde exista, `municipal` — desde `pipeline/src/wgj/tables/countries.json`. Presente cuando el registro los define |
| `crs`, `source`, `notes` | Como en el manifiesto; `notes` solo donde el manifiesto lo tiene |
| `datasets` | El array `datasets` del manifiesto, **tal cual** — rutas, `bytes`, `sha256`, `features`, `bbox`, `properties`, previews y `parts` de los niveles partidos, exactamente como describe [Formato del manifiesto](manifest.md#por-dataset-datasets) |

## Tamaño y determinismo

340 KB en disco, 39 KB comprimido con gzip — una fracción del archivo de datos
más pequeño. No tiene marca de tiempo ni campo de versión, a propósito: el
archivo es determinista byte a byte para un estado dado de los manifiestos, así
que el CI puede regenerarlo y hacer `git diff`. La versión de los datos es la
referencia de git desde la que lo descargaste.

## Cómo obtenerlo

=== "Última versión (`main`)"

    ```
    https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/index.json
    ```

=== "Fijado (cuando exista la etiqueta v1.0.0)"

    ```
    https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v1.0.0/data/index.json
    ```

    `v1.0.0` se etiqueta desde el merge del contrato de datos; hasta entonces
    solo resuelve `main`. Cada release etiquetada adjunta además `index.json`
    como asset de la Release, junto a los zips por país y un `SHA256SUMS`:
    <https://github.com/andresgmg/World-GeoJSON/releases/tag/v1.0.0>. Ver
    [Descarga y CDN](../get-started/download.md#assets-de-la-release).

El `path` de cada dataset es relativo al repositorio, así que `base + path` es
la URL de descarga para la base desde la que obtuviste el índice. Listar todos
los territorios que publican divisiones de primer nivel:

=== "JavaScript"

    ```js
    const base = "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/";
    const index = await fetch(`${base}data/index.json`).then((r) => r.json());

    for (const c of index.countries) {
      const adm1 = c.datasets.find((d) => d.level === "ADM1");
      if (adm1) {
        console.log(c.iso_a3, c.name.es, adm1.features, `${base}${adm1.path}`);
      }
    }
    ```

=== "Python"

    ```python
    import json
    import urllib.request

    BASE = "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/"

    with urllib.request.urlopen(BASE + "data/index.json") as fh:
        index = json.load(fh)

    for c in index["countries"]:
        adm1 = next((d for d in c["datasets"] if d["level"] == "ADM1"), None)
        if adm1:
            print(c["iso_a3"], c["name"]["es"], adm1["features"], BASE + adm1["path"])
    ```

Antes de fiarte de un archivo descargado, compara su SHA-256 con el `sha256`
que el índice registra para él — ver
[Descarga y CDN → Checksums](../get-started/download.md#checksums).

## Esquemas

Todo lo que escribe el pipeline está descrito por un JSON Schema (borrador
2020-12). Los cinco archivos viven en `schemas/` y se sirven desde este sitio
en su URL `$id`, para que un validador pueda resolver las referencias cruzadas
en línea:

| Archivo | `$id` | Qué valida |
|---|---|---|
| `manifest.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/manifest.schema.json> | Cada `data/{body}/{ISO3}/manifest.json` — identidad, procedencia y una entrada por nivel. Su enum `license` **es** la lista blanca de licencias |
| `index.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/index.schema.json> | `data/index.json`, esta página |
| `feature.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/feature.schema.json> | Una Feature de un archivo a resolución completa: `type`, el `id` obligatorio, `properties`, una geometría poligonal |
| `feature-properties.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/feature-properties.schema.json> | El objeto `properties` de una feature — el [contrato](properties.md); no se admite ninguna clave fuera de él |
| `countries.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/countries.schema.json> | `pipeline/src/wgj/tables/countries.json`, el registro que lee el pipeline |

`wgj validate` aplica los cinco en el CI: cada manifiesto, el
índice, el registro y cada feature de cada archivo a resolución completa. Los
previews no están cubiertos — llevan un subconjunto de las propiedades.

Para comprobar un archivo tú mismo con el paquete
[`jsonschema`](https://pypi.org/project/jsonschema/) — el esquema de
propiedades no tiene referencias cruzadas, así que no necesita nada más:

```bash
pip install jsonschema
python -c "
import json, jsonschema
schema = json.load(open('schemas/feature-properties.schema.json'))
for f in json.load(open('data/earth/CHL/CHL_ADM1.geojson'))['features']:
    jsonschema.validate(f['properties'], schema)
print('ok')
"
```

Para los esquemas que se referencian entre sí (`feature.schema.json` →
`feature-properties.schema.json`; `index.schema.json` y
`countries.schema.json` → definiciones de `manifest.schema.json`) ejecuta
`wgj validate`, que los resuelve desde el directorio local
`schemas/` y añade las comprobaciones que un esquema no puede expresar —
unicidad de ids, resolución de `parentID`, bbox contra coordenadas, checksums.

--8<-- "abbreviations.md"
