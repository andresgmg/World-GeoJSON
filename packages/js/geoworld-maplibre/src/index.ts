/**
 * geoworld-maplibre — MapLibre GL JS helpers for the World GeoJSON client.
 *
 * ```ts
 * import { createClient } from "geoworld";
 * import { addBoundaries, setFeatureState } from "geoworld-maplibre";
 *
 * const world = createClient({ version: "1.0.0" });
 * const regions = await addBoundaries(map, world, "CHL", "ADM1", { fit: true });
 * setFeatureState(map, regions.source, "CHL:ADM1:CL-RM", { hover: true });
 * ```
 *
 * Zero runtime dependencies: `maplibre-gl` and `geoworld` are peers and only
 * their types are imported.
 */

export { fitToBounds, toLngLatBounds } from "./bounds.js";
export {
  type AddBoundariesOptions,
  addBoundaries,
  bboxFor,
  type BoundaryLayers,
  clearFeatureState,
  collection,
  type CollectionOptions,
  DEFAULT_FILL,
  DEFAULT_LINE,
  type FillPaint,
  ID_PROPERTY,
  type LinePaint,
  type PromotedCollection,
  type PromotedFeature,
  setFeatureState,
  sourceId,
  sourceSpec,
  withIdProperty,
} from "./boundaries.js";
export { whenStyleReady } from "./ready.js";
