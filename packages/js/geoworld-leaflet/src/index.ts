/**
 * geoworld-leaflet — Leaflet helpers for the World GeoJSON client.
 *
 * ```ts
 * import { createClient } from "geoworld";
 * import { withLeaflet } from "geoworld-leaflet";
 *
 * const world = createClient({ version: "1.0.0" });
 * const gw = withLeaflet(L);                       // window.L or import * as L from "leaflet"
 * const regions = await gw.addBoundaries(map, world, "CHL", "ADM1", { fit: true });
 * ```
 *
 * Zero runtime dependencies: Leaflet is handed in, never imported.
 */

export {
  type AddBoundariesOptions,
  bboxFor,
  type BoundariesOptions,
  type BoundaryLayer,
  collection,
  type CollectionOptions,
  DEFAULT_STYLE,
  type GeoWorldLeaflet,
  layerById,
  type LeafletNamespace,
  toLatLngBounds,
  withLeaflet,
} from "./adapter.js";
