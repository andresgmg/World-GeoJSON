# Leaflet adapter

`geoworld-leaflet` on [npm](https://www.npmjs.com/package/geoworld-leaflet):
helpers that put a level from the [JavaScript client](javascript.md) on a
[Leaflet](https://leafletjs.com/) map. Zero runtime dependencies: Leaflet is
handed in, never imported, so the same package works with `window.L` from a
`<script>` tag, with a bundler, and, when the time comes, with Leaflet 2.
The source lives in
[`packages/js/geoworld-leaflet`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/js/geoworld-leaflet).

```bash
npm install geoworld geoworld-leaflet leaflet
```

## One call per level

```ts
import { createClient } from "geoworld";
import { withLeaflet } from "geoworld-leaflet";

const world = createClient({ version: "1.0.0" });
const gw = withLeaflet(L);                        // window.L, or import * as L from "leaflet"

const regions = await gw.addBoundaries(map, world, "CHL", "ADM1", {
  fit: true,                                      // fitBounds from the index bbox
  onEachFeature: (feature, layer) => layer.bindTooltip(feature.properties.shapeName),
});
regions.remove();                                 // it is a plain L.GeoJSON
```

`withLeaflet(L)` returns three functions:

| Function | Returns |
|---|---|
| `bounds(bbox)` | `new L.LatLngBounds` from an index bbox (`client.bbox(iso3, level)`) |
| `boundaries(client, iso3, level, options?)` | an `L.GeoJSON` layer, not yet on a map |
| `addBoundaries(map, client, iso3, level, options?)` | the same layer added to the map, fitted when `fit` is set |

Options are Leaflet's own `GeoJSONOptions` (`style`, `onEachFeature`,
`filter`, …) plus:

| Option | Default | Meaning |
|---|---|---|
| `part` | — | One part of a split level (`"US-CA"`, `"unassigned"`) |
| `preview` | `false` | The simplified preview instead of the full file |
| `fit` | `false` | `true` or `FitBoundsOptions` to fit the map to the index bbox |

Without a `style` the layer uses the documentation site's:
`{ weight: 1, color: "#00695c", fillColor: "#00695c", fillOpacity: 0.12 }`.
A level published as parts only (Brazil's municipalities) is concatenated
unless `part` is given.

## Sub-layers by stable id

```ts
import { layerById } from "geoworld-leaflet";

const santiago = layerById(regions, "CHL:ADM1:CL-RM");
santiago?.setStyle({ fillOpacity: 0.5 });
santiago?.openTooltip();
```

`layerById` looks through `layer.getLayers()` for the sub-layer whose
feature carries that id; it returns `undefined` when there is none.

## Bounds without Leaflet

`toLatLngBounds(bbox)` turns an index bbox into the
`[[south, west], [north, east]]` literal `map.fitBounds` accepts, so a map
can be framed before any GeoJSON is downloaded:

```ts
import { toLatLngBounds } from "geoworld-leaflet";
map.fitBounds(toLatLngBounds(await world.bbox("CHL", "ADM3")), { padding: [8, 8] });
```

`collection(client, iso3, level, { part?, preview? })` fetches a level the
way the adapter does, for use with your own `L.GeoJSON` options.

## Example

[`examples/leaflet.html`](https://github.com/andresgmg/World-GeoJSON/blob/main/examples/leaflet.html)
is a complete page with Leaflet from a script tag, a territory and level
picker, tooltips and hover styling. `just examples` serves it.

--8<-- "abbreviations.md"
