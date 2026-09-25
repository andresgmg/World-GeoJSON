/**
 * geoworld-react — React hooks for the World GeoJSON client.
 *
 * ```tsx
 * import { createClient } from "geoworld";
 * import { GeoWorldProvider, useBoundaries } from "geoworld-react";
 *
 * const world = createClient({ version: "1.0.0" });
 * <GeoWorldProvider client={world}><Regions /></GeoWorldProvider>
 *
 * function Regions() {
 *   const { status, data } = useBoundaries("CHL", "ADM1");
 *   return status === "success" ? <span>{data.features.length} regions</span> : <span>{status}</span>;
 * }
 * ```
 *
 * Zero runtime dependencies: `react` and `geoworld` are peers.
 */

export { type GeoWorldContextValue, GeoWorldProvider, type GeoWorldProviderProps, useGeoWorld } from "./context.js";
export {
  collection,
  type Resource,
  useBoundaries,
  type UseBoundariesOptions,
  useChildren,
  useCountries,
  useCountry,
  useFeature,
  useIndex,
  useResource,
} from "./hooks.js";
export {
  type BoundariesKeyOptions,
  createStore,
  ensureLoaded,
  IDLE,
  keys,
  type LoadOptions,
  resourceKey,
  type ResourceState,
  type Store,
} from "./store.js";
