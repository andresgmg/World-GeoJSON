# Adaptador React

`geoworld-react` en [npm](https://www.npmjs.com/package/geoworld-react): un
provider y hooks sobre el [cliente JavaScript](javascript.md). Cero
dependencias en runtime; `react` (≥ 18) y `geoworld` son peers. El código
vive en
[`packages/js/geoworld-react`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/js/geoworld-react).

```bash
npm install geoworld geoworld-react
```

## Provider y hooks

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

| Hook | Recurso |
|---|---|
| `useIndex()` | todo el `index.json` |
| `useCountries()` | un resumen por territorio |
| `useCountry(iso3)` | la entrada completa del índice (niveles, licencia, términos, datasets) |
| `useBoundaries(iso3, level, { part?, preview?, enabled? })` | una FeatureCollection |
| `useFeature(id)` | una feature por id estable |
| `useChildren(id)` | las features del siguiente nivel publicado bajo ese id |
| `useResource(key, loader)` | cualquier otra cosa, a través del mismo store |

Cada hook devuelve un **recurso**:

```ts
{ status: "idle" | "loading" | "success" | "error"; data?: T; error?: unknown; reload(): Promise<void> }
```

`data` está tipado como presente solo cuando `status === "success"`, así que
basta un `if` que estreche el tipo. Pasar `null` o `undefined` como `iso3`,
`level` o `id`, o `enabled: false`, deja el recurso en `idle` sin desmontar
el componente. `reload()` vuelve a cargar aunque ya esté cargado; con la
caché en memoria por defecto del cliente, eso solo vuelve a descargar tras
un error.

## Qué hace el store

El cliente cachea promesas, que React no puede leer durante el render. Por
eso el provider tiene un pequeño **store** con clave por petición
(`["boundaries", "CHL", "ADM1", null, false]`): dos componentes que piden el
mismo nivel disparan una sola descarga, un componente que se monta cuando el
dato ya está renderiza `success` en su primer paso, y `reload`/`invalidate`
tienen un sitio donde vivir. `useGeoWorld()` devuelve `{ client, store }`;
`createStore()` construye uno para cebarlo en el servidor o compartirlo entre
providers:

```ts
import { createStore, keys } from "geoworld-react";

const store = createStore();
await store.load(keys.boundaries("CHL", "ADM1"), () => world.get("CHL", "ADM1"));
// <GeoWorldProvider client={world} store={store}> renderiza ese nivel como success de inmediato
```

Las claves ponen en mayúsculas el territorio y el nivel, así que
`useBoundaries("chl", "adm1")` y `useBoundaries("CHL", "ADM1")` comparten
una entrada.

## En un mapa

Los hooks dan los datos; los adaptadores de mapa los ponen en pantalla. Con
[`geoworld-maplibre`](maplibre.md), pasa el cliente del provider a
`addBoundaries` dentro de un efecto; con [`geoworld-leaflet`](leaflet.md),
lo mismo con `withLeaflet(L).addBoundaries`. El `id` estable de cada feature
es lo que permite que una lista en React y una capa en el mapa hablen de la
misma unidad.

## Ejemplo

[`examples/react.html`](https://github.com/andresgmg/World-GeoJSON/blob/main/examples/react.html)
ejecuta los hooks con React desde un CDN y sin paso de build: selector de
territorio y nivel, la lista de features y `useChildren` al hacer clic.
`just examples` la sirve.

--8<-- "abbreviations.md"
