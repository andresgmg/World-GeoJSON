import type { Map as MapLibreMap } from "maplibre-gl";

/**
 * Resolve once `addSource`/`addLayer` are safe to call.
 *
 * `isStyleLoaded()` is `true` when the style is in, `undefined` when the map
 * has no style yet (`addSource` then creates an empty one) and `false` while
 * the style JSON is still loading or a source has tiles in flight. In that
 * last case the first of `style.load` (style JSON arrived) or `idle` (style
 * in, sources settled) means ready. `load` is never used: it fires once per
 * map, so a second call on a busy map would wait forever.
 */
export function whenStyleReady(map: MapLibreMap): Promise<void> {
  if (map.isStyleLoaded() !== false) return Promise.resolve();
  return new Promise((resolve) => {
    const done = (): void => {
      map.off("style.load", done);
      map.off("idle", done);
      resolve();
    };
    map.once("style.load", done);
    map.once("idle", done);
  });
}
