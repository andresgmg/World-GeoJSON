# MapLibre adapter

`geoworld-maplibre` on [npm](https://www.npmjs.com/package/geoworld-maplibre):
helpers that put a level from the [JavaScript client](javascript.md) on a
[MapLibre GL JS](https://maplibre.org/) map. Zero runtime dependencies;
`maplibre-gl` (≥ 2) and `geoworld` are peers. The source lives in
[`packages/js/geoworld-maplibre`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/js/geoworld-maplibre).

```bash
npm install geoworld geoworld-maplibre maplibre-gl
```

## One call per level

```ts
import { createClient } from "geoworld";
import { addBoundaries } from "geoworld-maplibre";

const world = createClient({ version: "1.0.0" });
const regions = await addBoundaries(map, world, "CHL", "ADM1", { fit: true });

regions.source;   // "geoworld-CHL-ADM1"
regions.layers;   // ["geoworld-CHL-ADM1-fill", "geoworld-CHL-ADM1-line"]
regions.bbox;     // from the index, no download needed
regions.remove(); // layers, then the source
```

`addBoundaries` fails early on an unknown territory or level, fits the map
from the index bbox when asked (before the data arrives), downloads the level
through the client (verified, cached), waits until the style can take a
source, and adds a GeoJSON source plus a fill and a line layer. It throws if
the source id is already on the map: call `remove()` on the previous handle
rather than relying on a silent replacement.

| Option | Default | Meaning |
|---|---|---|
| `part` | — | One part of a split level (`"US-CA"`, `"unassigned"`) |
| `preview` | `false` | The simplified preview instead of the full file |
| `source` | `geoworld-{ISO3}-{LEVEL}[-{part}][-preview]` | Source id |
| `fill` | `{ "fill-color": "#00695c", "fill-opacity": 0.15 }` | Fill paint, or `false` for no fill layer |
| `line` | `{ "line-color": "#00695c", "line-width": 1 }` | Line paint, or `false` for no line layer |
| `before` | — | Insert the layers below this layer id |
| `fit` | `false` | `true` or `FitBoundsOptions` to fit the map to the index bbox |

A level published as parts only (Brazil's municipalities) is concatenated
unless `part` is given; large levels are better shown with `preview: true`.

## Feature state by stable id

Every World GeoJSON feature has a stable `id` such as `CHL:ADM1:CL-RM`.
MapLibre cannot use it directly: `promoteId` reads a *property*, and a
non-numeric feature id is dropped on the way into the source. The adapter
therefore builds the source data as shallow copies with `properties.id`
repeating the feature id and sets `promoteId: "id"`, so both `feature-state`
and `e.features[0].id` see the World GeoJSON id.

```ts
import { clearFeatureState, setFeatureState } from "geoworld-maplibre";

const regions = await addBoundaries(map, world, "CHL", "ADM1", {
  fill: {
    "fill-color": "#00695c",
    "fill-opacity": ["case", ["boolean", ["feature-state", "hover"], false], 0.45, 0.15],
  },
});

let hovered: string | null = null;
map.on("mousemove", regions.layers[0], (e) => {
  const id = String(e.features?.[0]?.id ?? "");
  if (!id || id === hovered) return;
  if (hovered) clearFeatureState(map, regions.source, hovered, "hover");
  hovered = id;
  setFeatureState(map, regions.source, id, { hover: true });
});
map.on("mouseleave", regions.layers[0], () => {
  if (hovered) clearFeatureState(map, regions.source, hovered, "hover");
  hovered = null;
});
```

## Building your own layers

```ts
import { collection, fitToBounds, sourceSpec, withIdProperty } from "geoworld-maplibre";

map.addSource("provinces", await sourceSpec(world, "CHL", "ADM2"));   // { type: "geojson", data, promoteId: "id" }
map.addLayer({ id: "provinces-outline", type: "line", source: "provinces" });
fitToBounds(map, await world.bbox("CHL", "ADM2"), { padding: 20 });
```

`collection(client, iso3, level, { part?, preview? })` returns the
FeatureCollection the client would, concatenating parts when there is no
combined file; `withIdProperty(fc)` is the promotion step on its own;
`toLngLatBounds(bbox)` converts an index bbox to what `fitBounds` takes;
`whenStyleReady(map)` resolves when `addSource` is safe.

!!! note "Antimeridian"
    Index bboxes are naive `[west, south, east, north]` values. A dataset that
    crosses the antimeridian (Russia, Fiji, the United States with Alaska)
    reads `[-180, …, 180, …]` and `fit` shows the whole world.

## Example

[`examples/maplibre.html`](https://github.com/andresgmg/World-GeoJSON/blob/main/examples/maplibre.html)
is a complete page: a territory and level picker, the layer with `fit`, and
hover highlighting through feature state. `just examples` serves it.

--8<-- "abbreviations.md"
