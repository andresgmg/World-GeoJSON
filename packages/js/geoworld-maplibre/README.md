# geoworld-maplibre

[MapLibre GL JS](https://maplibre.org/) helpers for
[`geoworld`](https://www.npmjs.com/package/geoworld), the client for
[World GeoJSON](https://github.com/andresgmg/World-GeoJSON) administrative
boundaries. Zero runtime dependencies: `maplibre-gl` and `geoworld` are peers.

```bash
npm install geoworld geoworld-maplibre maplibre-gl
```

```ts
import { createClient } from "geoworld";
import { addBoundaries, clearFeatureState, setFeatureState } from "geoworld-maplibre";

const world = createClient({ version: "1.0.0" });
const regions = await addBoundaries(map, world, "CHL", "ADM1", { fit: true });
// regions.source === "geoworld-CHL-ADM1", regions.layers === ["…-fill", "…-line"]

map.on("mousemove", regions.layers[0], (e) => {
  const id = e.features?.[0]?.id;            // "CHL:ADM1:CL-RM" — the stable World GeoJSON id
  if (id) setFeatureState(map, regions.source, String(id), { hover: true });
});
map.on("mouseleave", regions.layers[0], () => clearFeatureState(map, regions.source));

regions.remove();                             // layers, then the source
```

- `addBoundaries(map, client, iso3, level, { part?, preview?, source?, fill?, line?, before?, fit? })`
  downloads the level through the client (verified, cached), waits for the
  style, adds a GeoJSON source with `promoteId: "id"` and a fill and a line
  layer, and returns a handle with `remove()`.
- `sourceSpec(...)` and `collection(...)` for adding your own layers;
  `withIdProperty(fc)` is what makes the stable `id` reach `feature-state`.
- `fitToBounds(map, bbox)` and `toLngLatBounds(bbox)` for the index bbox
  (`client.bbox(iso3, level)`), no download needed.
- `setFeatureState(map, source, id, state)` / `clearFeatureState(map, source, id?, key?)`.

Full guide: <https://andresgmg.github.io/World-GeoJSON/libraries/maplibre/>.
