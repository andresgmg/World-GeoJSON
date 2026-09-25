# geoworld-leaflet

[Leaflet](https://leafletjs.com/) helpers for
[`geoworld`](https://www.npmjs.com/package/geoworld), the client for
[World GeoJSON](https://github.com/andresgmg/World-GeoJSON) administrative
boundaries. Zero runtime dependencies: Leaflet is handed in, never imported,
so it works with `window.L` from a `<script>` tag as well as with a bundler.

```bash
npm install geoworld geoworld-leaflet leaflet
```

```ts
import { createClient } from "geoworld";
import { layerById, withLeaflet } from "geoworld-leaflet";

const world = createClient({ version: "1.0.0" });
const gw = withLeaflet(L);                                  // window.L, or import * as L from "leaflet"

const regions = await gw.addBoundaries(map, world, "CHL", "ADM1", {
  fit: true,                                                // fitBounds from the index bbox
  onEachFeature: (feature, layer) => layer.bindTooltip(feature.properties.shapeName),
});

layerById(regions, "CHL:ADM1:CL-RM")?.openTooltip();       // sub-layers by stable id
regions.remove();                                           // a plain L.GeoJSON layer
```

- `withLeaflet(L)` returns `bounds(bbox)`, `boundaries(client, iso3, level, options?)`
  (an `L.GeoJSON` not yet on a map) and `addBoundaries(map, client, iso3, level, options?)`.
  Options are Leaflet's `GeoJSONOptions` plus `part`, `preview` and `fit`.
- `toLatLngBounds(bbox)` turns an index bbox (`client.bbox(iso3, level)`) into
  the `[[south, west], [north, east]]` literal `map.fitBounds` takes.
- `collection(client, iso3, level, { part?, preview? })` fetches a level,
  concatenating the parts of a level that has no combined file.

Full guide: <https://andresgmg.github.io/World-GeoJSON/libraries/leaflet/>.
