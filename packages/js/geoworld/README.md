# geoworld

A thin JavaScript/TypeScript client for
[World GeoJSON](https://github.com/andresgmg/World-GeoJSON): open, versioned
administrative boundaries (countries, first-level divisions, municipalities)
as GeoJSON.

The library ships no data. It reads `data/index.json` from a pinned data
release, downloads the files you ask for, caches them and verifies their
`sha256` against the index. Zero dependencies; runs wherever `fetch` and Web
Crypto exist (Node ≥ 20, browsers, Deno, Bun, edge runtimes). ESM and
CommonJS, types included.

```bash
npm install geoworld
```

```ts
import { createClient } from "geoworld";

const world = createClient({ version: "1.0.0" });   // a data release; the library has its own version

await world.countries();                            // every territory: levels, licence, feature counts
(await world.country("CHL")).terms;                 // { adm1: { en: "Region", es: "Región" }, … }
await world.levels("CHL");                          // ["ADM0", "ADM1", "ADM2", "ADM3"]
await world.bbox("CHL", "ADM1");                    // [west, south, east, north] — no download

const regions = await world.get("CHL", "ADM1");     // a GeoJSON FeatureCollection
regions.features[0].id;                             // "CHL:ADM1:CL-CO"

await world.getPart("USA", "ADM2", "US-CA");        // one part of a split level
for await (const [code, counties] of world.iterParts("BRA", "ADM2")) {
  // levels too big for one file come as parts
}

await world.preview("CHL", "ADM3");                 // simplified (≤ 2 MB) for maps
await world.find("CHL:ADM3:01402");                 // one feature by id
await world.parent("CHL:ADM3:01402");               // its province
await world.children("CHL:ADM1:CL-TA");             // the provinces of Tarapacá
await world.search("santiago", "CHL", "ADM3");      // accent- and case-insensitive

await world.url("CHL", "ADM1");                     // the file's URL, if you would rather fetch it yourself
```

Every feature has a stable `id` (`{ISO3}:{LEVEL}:{key}`), and every
sub-national feature a `parentID`, so joins and hierarchies work without
string matching on names. With MapLibre, `promoteId: "id"` keys feature
state by it.

## Where the files come from

By default `https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v{version}/`.
Pass `baseUrl` to read from any static host with the same layout, and `fetch`
to supply your own implementation:

```ts
createClient({ version: "1.0.0", baseUrl: "https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0" });
```

## Caching

`cache: "memory"` (default) keeps parsed files for the life of the client;
`"none"` refetches on every call. A `CacheLike` (`get`/`set`/`delete`/`clear`
over `Uint8Array`s) persists the raw bytes, re-hashed on every read. In Node:

```ts
import { diskCache } from "geoworld/node";
const world = createClient({ cache: diskCache() });   // ~/.cache/geoworld/<version>/… (XDG, %LOCALAPPDATA%, ~/Library/Caches)
```

The layout matches the Python client's, so both can share a directory.

## Versions

The library's version and the data's version are independent. Each release of
the library declares the data schema it understands
(`SUPPORTED_SCHEMA_VERSION`) and a default data release
(`DEFAULT_DATA_VERSION`); a newer index throws `UnsupportedSchema`.

## Documentation

- [Library guide](https://andresgmg.github.io/World-GeoJSON/libraries/javascript/)
- [Data reference](https://andresgmg.github.io/World-GeoJSON/reference/) — properties, levels, the index
- [Licensing](https://andresgmg.github.io/World-GeoJSON/about/license/) — the code is MIT; each dataset carries its own permissive licence, listed in the index

On a map or in React, [`geoworld-maplibre`](https://www.npmjs.com/package/geoworld-maplibre),
[`geoworld-leaflet`](https://www.npmjs.com/package/geoworld-leaflet) and
[`geoworld-react`](https://www.npmjs.com/package/geoworld-react) wrap this
client in one call each. The same API exists for Python as
[`geoworld` on PyPI](https://pypi.org/project/geoworld/).
