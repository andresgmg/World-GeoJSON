# Cliente JavaScript

`geoworld` en [npm](https://www.npmjs.com/package/geoworld). TypeScript, ESM y
CommonJS, cero dependencias. Corre donde existan `fetch` y Web Crypto: Node
≥ 20, navegadores, Deno, Bun, runtimes de borde. El código vive en
[`packages/js/geoworld`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/js/geoworld).

```bash
npm install geoworld
```

## Construir un cliente

```ts
import { createClient } from "geoworld";

const world = createClient({ version: "1.0.0" });
```

| Opción | Por defecto | Significado |
|---|---|---|
| `version` | `"1.0.0"` (`DEFAULT_DATA_VERSION`) | Una etiqueta de release de datos sin la `v`, o `"main"` |
| `baseUrl` | `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v{version}` | Cualquier host estático con la disposición del repositorio |
| `fetch` | `globalThis.fetch` | Tu propio `fetch` (un proxy, un doble de pruebas, un limitador) |
| `cache` | `"memory"` | `"memory"`, `"none"`, o un almacén `CacheLike` que persiste los bytes |
| `verify` | `true` | Hashea cada descarga y cada lectura de caché contra el índice |
| `timeoutMs` | ninguno | Aborta una petición pasado ese tiempo |
| `headers` | — | Cabeceras extra |

`new GeoWorld(options)` es lo mismo que `createClient(options)`.

Pasar `version: "main"` sigue la rama: avisa y nunca persiste, porque un
`main` cacheado quedaría obsoleto en días.

### Caché

`"memory"` conserva los archivos parseados mientras viva el cliente — lo
adecuado para una página o un script. `"none"` vuelve a descargar en cada
llamada (el índice se lee una sola vez igualmente). Un `CacheLike` —
`{ get, set, delete, clear }` sobre `Uint8Array`s con clave
`"<versión>/<ruta>"` — persiste los bytes crudos; se vuelven a hashear en
cada lectura. En Node, `geoworld/node` ofrece uno en disco:

```ts
import { createClient } from "geoworld";
import { diskCache } from "geoworld/node";

const world = createClient({ cache: diskCache() });       // $GEOWORLD_CACHE, o el directorio de caché de la plataforma
const world = createClient({ cache: diskCache("/tmp/wg") });
```

La disposición es `<dir>/<versión>/<ruta>`, la misma que la del cliente
Python, así que ambos pueden compartir un directorio. En un navegador,
implementa `CacheLike` sobre IndexedDB o la Cache API si necesitas persistencia.

## Leer el índice

Ninguno de estos descarga GeoJSON; responden desde `data/index.json`, leído
una vez por cliente. Todo es `async`.

```ts
await world.index();                    // todo el índice: schema_version, totals, countries
await world.countries();                // [{ iso_a3: "ABW", name: {…}, levels: [...], features: 1, … }, …]
await world.country("CHL");             // la entrada completa: fuente, licencia, términos, datasets
await world.levels("CHL");              // ["ADM0", "ADM1", "ADM2", "ADM3"]
await world.dataset("CHL", "ADM3");     // la entrada del nivel: path, bytes, sha256, bbox, license, …
await world.bbox("CHL", "ADM3");        // [-109.449861, -56.525107, -66.416176, -17.498399]
await world.parts("USA", "ADM2");       // ["US-AK", "US-AL", …, "unassigned"]
await world.url("CHL", "ADM1");         // ".../v1.0.0/data/earth/CHL/CHL_ADM1.geojson"
await world.url("USA", "ADM2", { part: "US-CA" });
await world.url("CHL", "ADM3", { preview: true });
```

`(await world.country("CHL")).terms` guarda cómo se llaman los niveles
localmente, cuando el registro lo sabe.

## Leer archivos

```ts
const fc = await world.get("CHL", "ADM1");          // FeatureCollection, verificada, cacheada
fc.features[0].id;                                  // "CHL:ADM1:CL-CO"
fc.features[0].properties;                          // shapeName, shapeISO, shapeGroup, shapeType, parentID, …

await world.getPart("USA", "ADM2", "US-CA");        // una parte de un nivel dividido
for await (const [code, fc] of world.iterParts("BRA", "ADM2")) {
  // cada parte, en el orden del índice
}
for await (const feature of world.features("BRA", "ADM2")) {
  // cada feature, del archivo o a través de las partes
}

await world.preview("CHL", "ADM3");                 // simplificado, ≤ 2 MB; solo shapeName, shapeISO, shapeType
```

Un nivel publicado solo en partes (el ADM2 de Brasil, 33 MB combinado)
rechaza `get()` con `NoCombinedFile`; usa `iterParts()` o `features()`.

Los objetos devueltos se cachean en memoria y se comparten entre llamadas:
copia antes de modificar.

## Navegar

Cada feature tiene un `id` estable (`{ISO3}:{NIVEL}:{clave}`) y cada feature
subnacional un `parentID`; ver
[Diccionario de propiedades](../reference/properties.md).

```ts
await world.find("CHL:ADM3:01402");            // una feature; carga solo la parte donde vive cuando puede
await world.parent("CHL:ADM3:01402");          // la provincia, o null en ADM0
await world.children("CHL:ADM1:CL-TA");        // las provincias de Tarapacá
await world.search("santiago", "CHL", "ADM3"); // sin distinguir acentos ni mayúsculas en shapeName; exacto en shapeISO
await world.search("valpar", "CHL");           // todos los niveles del territorio
```

`children()` usa el siguiente nivel *publicado*: para un territorio sin ADM1
(Puerto Rico), los hijos del ADM0 son sus unidades ADM2.

## En un mapa

El `id` estable es la clave para las bibliotecas de mapas. MapLibre:

```ts
const world = createClient({ version: "1.0.0" });
map.addSource("regions", {
  type: "geojson",
  data: await world.url("CHL", "ADM1"),   // deja que MapLibre lo descargue…
  promoteId: "id",                        // …y usa nuestro id como clave de feature-state
});
// o pásale el objeto parseado y verificado:
map.addSource("regions", { type: "geojson", data: await world.get("CHL", "ADM1"), promoteId: "id" });
map.setFeatureState({ source: "regions", id: "CHL:ADM1:CL-RM" }, { hover: true });
```

Leaflet:

```ts
const bounds = await world.bbox("CHL", "ADM1");
L.geoJSON(await world.preview("CHL", "ADM1")).addTo(map);
map.fitBounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]]);
```

## Errores

Todos extienden `GeoWorldError`:

| Error | Cuándo |
|---|---|
| `UnknownCountry`, `UnknownLevel`, `UnknownPart`, `UnknownFeature` | No está en esta versión de datos |
| `InvalidFeatureId` | No es una cadena `{ISO3}:{NIVEL}:{clave}` |
| `NotSplit` | Se pidieron partes de un nivel de un solo archivo |
| `NoCombinedFile` | `get()` sobre un nivel solo en partes |
| `NoPreview` | El nivel no tiene preview |
| `DownloadError` | Fallo de red o HTTP; `.status` lleva el código |
| `ChecksumMismatch` | Los bytes no hashean al `sha256` del índice |
| `UnsupportedSchema` | El índice es más nuevo que `SUPPORTED_SCHEMA_VERSION` |

## Sin conexión y espejos

Cualquier host con la disposición del repositorio sirve como fuente, incluido
un directorio servido en local o un `world-geojson-v1.0.0-all.zip`
descomprimido de los [assets de la release](../get-started/download.md).

```ts
createClient({ version: "1.0.0", baseUrl: "https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0" });
createClient({ version: "1.0.0", baseUrl: "http://localhost:8080/world-geojson" });
```

La `version` nombra el espacio de caché; mantenla igual a lo que contiene el
espejo.

## Tipos

El paquete incluye sus declaraciones: `Index`, `Country`, `Dataset`, `Part`,
`CountrySummary`, `Feature`, `FeatureCollection`, `FeatureProperties`,
escritas a partir de los [JSON Schemas](../reference/index-json.md#esquemas).
Impórtalas con `import type { Feature } from "geoworld"`.

--8<-- "abbreviations.md"
