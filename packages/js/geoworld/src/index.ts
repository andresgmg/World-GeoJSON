/**
 * geoworld — a thin client for the World GeoJSON administrative boundaries.
 *
 * ```ts
 * import { createClient } from "geoworld";
 * const world = createClient({ version: "1.0.0" });
 * const regions = await world.get("CHL", "ADM1");
 * regions.features[0].id; // "CHL:ADM1:CL-CO"
 * ```
 *
 * Reads `data/index.json` from a pinned data release, downloads files on
 * demand, caches them and verifies their `sha256` against the index. Zero
 * dependencies; needs `fetch` and Web Crypto (Node ≥ 20 or a browser).
 */

export { type CacheLike, MemoryCache } from "./cache.js";
export {
  type ClientOptions,
  createClient,
  DEFAULT_BASE_URL,
  DEFAULT_DATA_VERSION,
  GeoWorld,
  INDEX_PATH,
  normalise,
  parseId,
  summarise,
  SUPPORTED_SCHEMA_VERSION,
  type UrlOptions,
  VERSION,
} from "./client.js";
export {
  ChecksumMismatch,
  DownloadError,
  GeoWorldError,
  InvalidFeatureId,
  NoCombinedFile,
  NoPreview,
  NotSplit,
  UnknownCountry,
  UnknownFeature,
  UnknownLevel,
  UnknownPart,
  UnsupportedSchema,
} from "./errors.js";
export type * from "./types.js";
export { isSafePath, sha256Hex } from "./verify.js";
