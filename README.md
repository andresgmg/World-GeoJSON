# World GeoJSON

Open, versioned GeoJSON administrative boundaries — the Americas today,
growing toward every country on Earth, and eventually the Moon and Mars.

**📖 Documentation: <https://andresgmg.github.io/World-GeoJSON/>**

*[Versión en español abajo.](#world-geojson-es)*

---

## Quick start

```js
const url =
  "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/earth/CHL/CHL_ADM1.geojson";

const regions = await fetch(url).then((r) => r.json());
console.log(regions.features.length); // 16
console.log(regions.features.map((f) => f.properties.shapeName));
// ["Coquimbo", "Ñuble", "Los Lagos", …]
```

Every dataset lives at the same kind of path and carries the same four
properties — `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` — so code
written against one country works against all of them.

Or let a client do the fetching, caching and checksum verification, pinned
to a data release — `geoworld` has the same API in Python and JavaScript:

```python
from geoworld import GeoWorld  # pip install geoworld

world = GeoWorld("1.0.0")
world.get("CHL", "ADM1")["features"][0]["id"]  # "CHL:ADM1:CL-CO"
world.children("CHL:ADM1:CL-TA")  # the provinces of Tarapacá
```

```js
import { createClient } from "geoworld";  // npm install geoworld
const world = createClient({ version: "1.0.0" });
(await world.get("CHL", "ADM1")).features[0].id;   // "CHL:ADM1:CL-CO"
```

## What is here

| | |
|---|---|
| **Coverage** | The Americas: 55 territories, 95 datasets, 16,195 features |
| **Layout** | `data/earth/{ISO3}/{ISO3}_{LEVEL}.geojson` with `LEVEL` from `ADM0` to `ADM4`, plus `manifest.json` (sizes, SHA-256, licence) and `preview/` (simplified, at most 2 MB) per country |
| **Sizes** | Largest file 14.9 MB (`CAN_ADM1`); nothing over 20 MB. Municipal tiers that would be bigger are split by ADM1 into `{LEVEL}/{code}.geojson` |
| **Sources** | Natural Earth (every ADM0), geoBoundaries gbOpen under permissive licences only (ADM1 and municipal tiers), IDE Chile / SUBDERE DPA 2023 (Chile) |
| **Index & ids** | `data/index.json` lists every territory and dataset — paths, sizes, SHA-256, bbox, licence, every manifest embedded — in one 340 KB file. Every feature has a stable `id` (`{ISO3}:{LEVEL}:{key}`, e.g. `CHL:ADM3:01402`) and, below the country outline, its parent's id in `parentID` |

The [Catalog](https://andresgmg.github.io/World-GeoJSON/catalog/) lists every
dataset with feature counts, bounding boxes, properties and download links.

### Legacy files (deprecated)

The four files in the repository root predate the catalog. They are an older
BCN dataset with their own property names (`Region`, `Comuna`, `cod_comuna`,
`area_km`), kept only so that existing links keep working.

| Legacy file | Use instead |
|---|---|
| `regiones.geojson` (3.5 MB) and its duplicate `regiones.json` | `data/earth/CHL/CHL_ADM1.geojson` |
| `comunas.geojson` (72 MB) and its duplicate `comunas.json` | `data/earth/CHL/CHL_ADM3.geojson` (7 MB) |

> [!WARNING]
> `comunas.geojson` is 72 MB. Do not load it in a browser — it crashes the tab
> on mobile. The replacement is 7 MB, and its preview under 500 KB.

All four stay unchanged through the 1.x series and are removed in v2.0.0. See
[Versioning](https://andresgmg.github.io/World-GeoJSON/about/versioning/).

## Where things are going

1. **Data contract v1** — done, tag pending: `data/index.json`, the JSON
   Schemas under `schemas/`, a stable Feature `id` (`{ISO3}:{LEVEL}:{key}`)
   and `parentID`/`parentISO`/`adm1ISO` on every sub-national feature are on
   `main`. `v1.0.0` is tagged from the merge of that change, and its GitHub
   Release carries per-country zips, `index.json` and `SHA256SUMS`.
2. **Pipeline as a package** — done: the `wgj` command, installed from
   `pipeline/`, with tests that run on `fixtures/data/` and previews cut from
   Python.
3. **Client libraries** — done: `geoworld` for Python (`pip install geoworld`)
   and for JavaScript/TypeScript (`npm install geoworld`), in `packages/`.
   Thin clients with the same API that read `index.json` at a pinned data
   version, download on demand, cache, verify checksums and navigate by
   feature `id`. See
   [Client libraries](https://andresgmg.github.io/World-GeoJSON/libraries/).
4. **Framework adapters** — done: `geoworld-maplibre`, `geoworld-leaflet`
   and `geoworld-react` (npm) put a level on a map or in a component tree in
   one call, with feature state and sub-layers keyed by the stable feature
   `id`. Pages in `examples/` run them without a build step.

Other continents follow the same pipeline. There is no hosted API, tile
service or geocoder, and no historical boundaries. The
[Roadmap](https://andresgmg.github.io/World-GeoJSON/about/roadmap/) has the
detail.

## Contributing

Country contributions are welcome. **Check the licence of your source first** —
[Approved sources](https://andresgmg.github.io/World-GeoJSON/contributing/sources/)
lists what is usable and what is not. GADM, the most convenient global source,
is not.

Then follow
[Add a country](https://andresgmg.github.io/World-GeoJSON/contributing/add-a-country/).

To run the checks locally: `pip install -r requirements-dev.txt && npm ci`,
then `ruff check . && mypy && pytest` for the code and
`wgj validate --checksums` for the data. See [CONTRIBUTING](CONTRIBUTING.md).

## Licence

Code is [MIT](LICENSE). **Data is licensed per source** — see
[Licensing & attribution](https://andresgmg.github.io/World-GeoJSON/about/license/).

---

<a name="world-geojson-es"></a>

# World GeoJSON <sub>(español)</sub>

Límites administrativos en GeoJSON, abiertos y versionados — hoy América,
creciendo hacia todos los países del mundo y, más adelante, la Luna y Marte.

**📖 Documentación: <https://andresgmg.github.io/World-GeoJSON/es/>**

## Inicio rápido

```js
const url =
  "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/earth/CHL/CHL_ADM1.geojson";

const regiones = await fetch(url).then((r) => r.json());
console.log(regiones.features.length); // 16
console.log(regiones.features.map((f) => f.properties.shapeName));
// ["Coquimbo", "Ñuble", "Los Lagos", …]
```

Todos los datasets viven en el mismo tipo de ruta y llevan las mismas cuatro
propiedades — `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` — así que el
código escrito para un país sirve para todos.

O deja que un cliente descargue, cachee y verifique los checksums, fijado a
una release de datos — `geoworld` tiene la misma API en Python y JavaScript:

```python
from geoworld import GeoWorld  # pip install geoworld

world = GeoWorld("1.0.0")
world.get("CHL", "ADM1")["features"][0]["id"]  # "CHL:ADM1:CL-CO"
world.children("CHL:ADM1:CL-TA")  # las provincias de Tarapacá
```

```js
import { createClient } from "geoworld";  // npm install geoworld
const world = createClient({ version: "1.0.0" });
(await world.get("CHL", "ADM1")).features[0].id;   // "CHL:ADM1:CL-CO"
```

## Qué hay aquí

| | |
|---|---|
| **Cobertura** | América: 55 territorios, 95 datasets, 16.195 features |
| **Estructura** | `data/earth/{ISO3}/{ISO3}_{LEVEL}.geojson` con `LEVEL` de `ADM0` a `ADM4`, más `manifest.json` (tamaños, SHA-256, licencia) y `preview/` (simplificados, como máximo 2 MB) por país |
| **Tamaños** | El archivo más grande pesa 14,9 MB (`CAN_ADM1`); ninguno supera 20 MB. Los niveles municipales que lo superarían se parten por ADM1 en `{LEVEL}/{código}.geojson` |
| **Fuentes** | Natural Earth (todos los ADM0), geoBoundaries gbOpen solo con licencias permisivas (ADM1 y niveles municipales), IDE Chile / SUBDERE DPA 2023 (Chile) |
| **Índice e ids** | `data/index.json` enumera cada territorio y dataset — rutas, tamaños, SHA-256, bbox, licencia, todos los manifiestos incrustados — en un único archivo de 340 KB. Cada feature tiene un `id` estable (`{ISO3}:{LEVEL}:{clave}`, p. ej. `CHL:ADM3:01402`) y, por debajo del contorno del país, el id de su padre en `parentID` |

El [Catálogo](https://andresgmg.github.io/World-GeoJSON/es/catalog/) lista cada
dataset con número de features, bounding box, propiedades y enlaces de
descarga.

### Archivos heredados (obsoletos)

Los cuatro archivos de la raíz del repositorio son anteriores al catálogo. Son
un dataset más antiguo (BCN) con sus propios nombres de propiedades (`Region`,
`Comuna`, `cod_comuna`, `area_km`) y se conservan solo para que los enlaces
existentes sigan funcionando.

| Archivo heredado | Usa en su lugar |
|---|---|
| `regiones.geojson` (3,5 MB) y su duplicado `regiones.json` | `data/earth/CHL/CHL_ADM1.geojson` |
| `comunas.geojson` (72 MB) y su duplicado `comunas.json` | `data/earth/CHL/CHL_ADM3.geojson` (7 MB) |

> [!WARNING]
> `comunas.geojson` pesa 72 MB. No lo cargues en el navegador — en móvil
> revienta la pestaña. El reemplazo pesa 7 MB, y su preview menos de 500 KB.

Los cuatro se mantienen sin cambios durante la serie 1.x y se eliminan en
v2.0.0. Ver
[Versionado](https://andresgmg.github.io/World-GeoJSON/es/about/versioning/).

## Hacia dónde va

1. **Contrato de datos v1** — hecho, etiqueta pendiente: `data/index.json`,
   los JSON Schemas en `schemas/`, un `id` de Feature estable
   (`{ISO3}:{LEVEL}:{clave}`) y `parentID`/`parentISO`/`adm1ISO` en cada
   feature subnacional están en `main`. `v1.0.0` se etiqueta desde el merge de
   ese cambio, y su GitHub Release lleva zips por país, `index.json` y
   `SHA256SUMS`.
2. **Pipeline como paquete** — hecho: el comando `wgj`, instalado desde
   `pipeline/`, con tests que corren sobre `fixtures/data/` y previews
   generados desde Python.
3. **Bibliotecas cliente** — hecho: `geoworld` para Python
   (`pip install geoworld`) y para JavaScript/TypeScript
   (`npm install geoworld`), en `packages/`. Clientes ligeros con la misma API
   que leen `index.json` de una versión de datos fijada, descargan bajo
   demanda, cachean, verifican checksums y navegan por el `id` de cada
   feature. Ver
   [Bibliotecas cliente](https://andresgmg.github.io/World-GeoJSON/es/libraries/).
4. **Adaptadores** — hecho: `geoworld-maplibre`, `geoworld-leaflet` y
   `geoworld-react` (npm) ponen un nivel en un mapa o en un árbol de
   componentes con una llamada, con feature state y subcapas indexadas por el
   `id` estable de cada feature. Las páginas de `examples/` los ejecutan sin
   paso de build.

Los demás continentes siguen el mismo pipeline. No hay API alojada, servidor
de teselas ni geocodificador, y no hay límites históricos. La
[Hoja de ruta](https://andresgmg.github.io/World-GeoJSON/es/about/roadmap/)
tiene el detalle.

## Contribuir

**Verifica primero la licencia de tu fuente.** GADM, la fuente global más
cómoda, no es utilizable aquí. Después sigue
[Añadir un país](https://andresgmg.github.io/World-GeoJSON/es/contributing/add-a-country/).

Para ejecutar las comprobaciones en local:
`pip install -r requirements-dev.txt && npm ci`, después
`ruff check . && mypy && pytest` para el código y `wgj validate --checksums`
para los datos. Ver [CONTRIBUTING](CONTRIBUTING.md).

## Licencia

El código es [MIT](LICENSE). **Los datos se licencian según su fuente.**
