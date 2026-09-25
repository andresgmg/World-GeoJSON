import type { BBox } from "geoworld";
import type { FitBoundsOptions, Map as MapLibreMap } from "maplibre-gl";

/** `[west, south, east, north]` → `[[west, south], [east, north]]`, what MapLibre's `fitBounds` takes. */
export function toLngLatBounds(bbox: BBox): [[number, number], [number, number]] {
  return [
    [bbox[0], bbox[1]],
    [bbox[2], bbox[3]],
  ];
}

/**
 * Fit the map to an index bbox. Works before the style has loaded. A dataset
 * that crosses the antimeridian (RUS, FJI, USA) has a naive index bbox of
 * `[-180, …, 180, …]` and fits the whole world.
 */
export function fitToBounds(map: MapLibreMap, bbox: BBox, options?: FitBoundsOptions): void {
  map.fitBounds(toLngLatBounds(bbox), options);
}
