# JavaScript client

`geoworld` on [npm](https://www.npmjs.com/package/geoworld). TypeScript,
ESM and CommonJS, zero dependencies. Runs wherever `fetch` and Web Crypto
exist: Node ≥ 20, browsers, Deno, Bun, edge runtimes. The source lives in
[`packages/js/geoworld`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/js/geoworld).

```bash
npm install geoworld
```

## Constructing a client

```ts
import { createClient } from "geoworld";

const world = createClient({ version: "1.0.0" });
```

| Option | Default | Meaning |
|---|---|---|
| `version` | `"1.0.0"` (`DEFAULT_DATA_VERSION`) | A data release tag without the `v`, or `"main"` |
| `baseUrl` | `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v{version}` | Any static host with the repository layout |
| `fetch` | `globalThis.fetch` | Your own `fetch` (a proxy, a test double, a rate limiter) |
| `cache` | `"memory"` | `"memory"`, `"none"`, or a `CacheLike` store that persists the bytes |
| `verify` | `true` | Hash every download and cached read against the index |
| `timeoutMs` | none | Abort a request after this long |
| `headers` | — | Extra request headers |

`new GeoWorld(options)` is the same thing as `createClient(options)`.

Passing `version: "main"` follows the branch: it warns and never persists,
because a cached `main` would be stale within days.

### Caching

`"memory"` keeps parsed files for the life of the client — right for a page
or a script. `"none"` refetches on every call (the index is still read once).
A `CacheLike` — `{ get, set, delete, clear }` over `Uint8Array`s keyed by
`"<version>/<path>"` — persists the raw bytes; they are re-hashed on every
read. In Node, `geoworld/node` provides one on disk:

```ts
import { createClient } from "geoworld";
import { diskCache } from "geoworld/node";

const world = createClient({ cache: diskCache() });       // $GEOWORLD_CACHE, else the platform cache dir
const world = createClient({ cache: diskCache("/tmp/wg") });
```

The layout is `<dir>/<version>/<path>`, the same as the Python client's, so
the two can share a directory. In a browser, implement `CacheLike` over
IndexedDB or the Cache API if you need persistence.

## Reading the index

None of these download GeoJSON; they answer from `data/index.json`, fetched
once per client. Everything is `async`.

```ts
await world.index();                    // the whole index: schema_version, totals, countries
await world.countries();                // [{ iso_a3: "ABW", name: {…}, levels: [...], features: 1, … }, …]
await world.country("CHL");             // the full entry: source, licence, terms, datasets
await world.levels("CHL");              // ["ADM0", "ADM1", "ADM2", "ADM3"]
await world.dataset("CHL", "ADM3");     // the level's entry: path, bytes, sha256, bbox, license, …
await world.bbox("CHL", "ADM3");        // [-109.449861, -56.525107, -66.416176, -17.498399]
await world.parts("USA", "ADM2");       // ["US-AK", "US-AL", …, "unassigned"]
await world.url("CHL", "ADM1");         // ".../v1.0.0/data/earth/CHL/CHL_ADM1.geojson"
await world.url("USA", "ADM2", { part: "US-CA" });
await world.url("CHL", "ADM3", { preview: true });
```

`(await world.country("CHL")).terms` holds what the tiers are called locally,
when the registry knows.

## Reading files

```ts
const fc = await world.get("CHL", "ADM1");          // FeatureCollection, verified, cached
fc.features[0].id;                                  // "CHL:ADM1:CL-CO"
fc.features[0].properties;                          // shapeName, shapeISO, shapeGroup, shapeType, parentID, …

await world.getPart("USA", "ADM2", "US-CA");        // one part of a split level
for await (const [code, fc] of world.iterParts("BRA", "ADM2")) {
  // every part, in index order
}
for await (const feature of world.features("BRA", "ADM2")) {
  // every feature, from the file or across parts
}

await world.preview("CHL", "ADM3");                 // simplified, ≤ 2 MB; only shapeName, shapeISO, shapeType
```

A level published as parts only (Brazil's ADM2, 33 MB combined) rejects
`get()` with `NoCombinedFile`; use `iterParts()` or `features()`.

Returned objects are cached in memory and shared between calls: copy before
mutating.

## Navigating

Every feature has a stable `id` (`{ISO3}:{LEVEL}:{key}`) and every
sub-national feature a `parentID`; see
[Property dictionary](../reference/properties.md).

```ts
await world.find("CHL:ADM3:01402");            // one feature; loads only the part it lives in when it can
await world.parent("CHL:ADM3:01402");          // the province, or null at ADM0
await world.children("CHL:ADM1:CL-TA");        // the provinces of Tarapacá
await world.search("santiago", "CHL", "ADM3"); // accent- and case-insensitive on shapeName; exact on shapeISO
await world.search("valpar", "CHL");           // all levels of the territory
```

`children()` uses the next *published* level: for a territory without ADM1
(Puerto Rico), the children of ADM0 are its ADM2 units.

## On a map

The stable `id` is what map libraries key on. MapLibre:

```ts
const world = createClient({ version: "1.0.0" });
map.addSource("regions", {
  type: "geojson",
  data: await world.url("CHL", "ADM1"),   // let MapLibre fetch it…
  promoteId: "id",                        // …and key feature-state by our id
});
// or hand it the parsed, verified object:
map.addSource("regions", { type: "geojson", data: await world.get("CHL", "ADM1"), promoteId: "id" });
map.setFeatureState({ source: "regions", id: "CHL:ADM1:CL-RM" }, { hover: true });
```

Leaflet:

```ts
const bounds = await world.bbox("CHL", "ADM1");
L.geoJSON(await world.preview("CHL", "ADM1")).addTo(map);
map.fitBounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]]);
```

## Errors

All extend `GeoWorldError`:

| Error | When |
|---|---|
| `UnknownCountry`, `UnknownLevel`, `UnknownPart`, `UnknownFeature` | Not in this data version |
| `InvalidFeatureId` | Not a `{ISO3}:{LEVEL}:{key}` string |
| `NotSplit` | Parts asked of a single-file level |
| `NoCombinedFile` | `get()` on a parts-only level |
| `NoPreview` | The level has no preview |
| `DownloadError` | Network or HTTP failure; `.status` carries the code |
| `ChecksumMismatch` | The bytes do not hash to the index's `sha256` |
| `UnsupportedSchema` | The index is newer than `SUPPORTED_SCHEMA_VERSION` |

## Offline and mirrors

Any host with the repository layout works as a source, including a directory
served locally or an unzipped `world-geojson-v1.0.0-all.zip` from the
[release assets](../get-started/download.md).

```ts
createClient({ version: "1.0.0", baseUrl: "https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0" });
createClient({ version: "1.0.0", baseUrl: "http://localhost:8080/world-geojson" });
```

The `version` names the cache namespace; keep it equal to what the mirror
holds.

## Types

The package ships its declarations: `Index`, `Country`, `Dataset`, `Part`,
`CountrySummary`, `Feature`, `FeatureCollection`, `FeatureProperties`, written
from the [JSON Schemas](../reference/index-json.md#schemas). Import them with
`import type { Feature } from "geoworld"`.

--8<-- "abbreviations.md"
