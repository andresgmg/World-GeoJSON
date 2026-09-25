# geoworld-react

React hooks for [`geoworld`](https://www.npmjs.com/package/geoworld), the
client for [World GeoJSON](https://github.com/andresgmg/World-GeoJSON)
administrative boundaries. Zero runtime dependencies: `react` (≥ 18) and
`geoworld` are peers.

```bash
npm install geoworld geoworld-react
```

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
  const regions = useBoundaries(iso3, "ADM1");            // { status, data, error, reload }
  if (regions.status !== "success") return <p>{regions.status}</p>;
  return <ul>{regions.data.features.map((f) => <li key={f.id}>{f.properties.shapeName}</li>)}</ul>;
}
```

| Hook | Resource |
|---|---|
| `useIndex()` | the whole `index.json` |
| `useCountries()` | one summary per territory |
| `useCountry(iso3)` | the full index entry |
| `useBoundaries(iso3, level, { part?, preview?, enabled? })` | a FeatureCollection |
| `useFeature(id)` | one feature by stable id |
| `useChildren(id)` | the features of the next level under it |
| `useResource(key, loader)` | anything else, through the same store |

Each returns `{ status: "idle" | "loading" | "success" | "error", data, error, reload }`.
Data comes from the client (verified, cached) through a small store that the
provider owns, so two components asking for the same level trigger one
download and a component mounting on cached data renders `success` at once.
`useGeoWorld()` gives the client and the store; `createStore()` lets you prime
one on the server or share it across providers.

Pair it with [`geoworld-maplibre`](https://www.npmjs.com/package/geoworld-maplibre)
or [`geoworld-leaflet`](https://www.npmjs.com/package/geoworld-leaflet) to
put the data on a map.

Full guide: <https://andresgmg.github.io/World-GeoJSON/libraries/react/>.
