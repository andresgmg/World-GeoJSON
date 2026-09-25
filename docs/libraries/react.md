# React adapter

`geoworld-react` on [npm](https://www.npmjs.com/package/geoworld-react): a
provider and hooks over the [JavaScript client](javascript.md). Zero runtime
dependencies; `react` (≥ 18) and `geoworld` are peers. The source lives in
[`packages/js/geoworld-react`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/js/geoworld-react).

```bash
npm install geoworld geoworld-react
```

## Provider and hooks

```tsx
import { createClient } from "geoworld";
import { GeoWorldProvider, useBoundaries, useCountries } from "geoworld-react";

const world = createClient({ version: "1.0.0" });

export function App() {
  return (
    <GeoWorldProvider client={world}>
      <Regions iso3="CHL" />
    </GeoWorldProvider>
  );
}

function Regions({ iso3 }: { iso3: string }) {
  const regions = useBoundaries(iso3, "ADM1");
  if (regions.status !== "success") return <p>{regions.status}</p>;
  return (
    <ul>
      {regions.data.features.map((f) => <li key={f.id}>{f.properties.shapeName}</li>)}
    </ul>
  );
}
```

| Hook | Resource |
|---|---|
| `useIndex()` | the whole `index.json` |
| `useCountries()` | one summary per territory |
| `useCountry(iso3)` | the full index entry (levels, licence, terms, datasets) |
| `useBoundaries(iso3, level, { part?, preview?, enabled? })` | a FeatureCollection |
| `useFeature(id)` | one feature by stable id |
| `useChildren(id)` | the features of the next published level under it |
| `useResource(key, loader)` | anything else, through the same store |

Every hook returns a **resource**:

```ts
{ status: "idle" | "loading" | "success" | "error"; data?: T; error?: unknown; reload(): Promise<void> }
```

`data` is typed as present only when `status === "success"`, so a narrowing
`if` is enough. Passing `null` or `undefined` as `iso3`, `level` or `id`, or
`enabled: false`, keeps the resource `idle` without unmounting the component.
`reload()` loads again even when already loaded; with the client's default
memory cache that is a refetch only after an error.

## What the store does

The client caches promises, which React cannot read during render. The
provider therefore owns a small **store** keyed by request
(`["boundaries", "CHL", "ADM1", null, false]`): two components asking for the
same level trigger one download, a component that mounts after the data is
in renders `success` on its first pass, and `reload`/`invalidate` have one
place to live. `useGeoWorld()` returns `{ client, store }`;
`createStore()` builds one to prime on the server or share between providers:

```ts
import { createStore, keys } from "geoworld-react";

const store = createStore();
await store.load(keys.boundaries("CHL", "ADM1"), () => world.get("CHL", "ADM1"));
// <GeoWorldProvider client={world} store={store}> now renders that level as success at once
```

Keys upper-case the territory and level, so `useBoundaries("chl", "adm1")`
and `useBoundaries("CHL", "ADM1")` share an entry.

## On a map

The hooks give you data; the map adapters put it on screen. With
[`geoworld-maplibre`](maplibre.md), pass the provider's client to
`addBoundaries` inside an effect; with [`geoworld-leaflet`](leaflet.md), the
same with `withLeaflet(L).addBoundaries`. The stable `id` on every feature
is what lets a list in React and a layer on the map refer to the same unit.

## Example

[`examples/react.html`](https://github.com/andresgmg/World-GeoJSON/blob/main/examples/react.html)
runs the hooks with React from a CDN and no build step: a territory and level
picker, the feature list, and `useChildren` on click. `just examples` serves
it.

--8<-- "abbreviations.md"
