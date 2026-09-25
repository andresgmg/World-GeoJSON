import type { BBox, Feature, FeatureCollection, FeatureProperties, GeoWorld } from "geoworld";
import type * as Leaflet from "leaflet";

/**
 * What the adapter needs from Leaflet. Passed in by the caller (`window.L`
 * or `import * as L from "leaflet"`) so this package never imports Leaflet
 * at runtime: Leaflet's UMD build touches `window` when loaded, and
 * constructors rather than factories keep Leaflet 2 in reach.
 */
export type LeafletNamespace = Pick<typeof Leaflet, "GeoJSON" | "LatLngBounds">;

export type BoundaryLayer = Leaflet.GeoJSON<FeatureProperties>;

export interface CollectionOptions {
  /** One part of a split level (its ADM1 key, or `"unassigned"`). */
  part?: string;
  /** The simplified preview instead of the full-resolution file. */
  preview?: boolean;
}

export interface BoundariesOptions extends Leaflet.GeoJSONOptions<FeatureProperties>, CollectionOptions {}

export interface AddBoundariesOptions extends BoundariesOptions {
  /** Fit the map to the index bbox (no download needed for the bounds). */
  fit?: boolean | Leaflet.FitBoundsOptions;
}

/** The style used when the options give none: the one on the documentation site. */
export const DEFAULT_STYLE: Leaflet.PathOptions = {
  weight: 1,
  color: "#00695c",
  fillColor: "#00695c",
  fillOpacity: 0.12,
};

/** `[west, south, east, north]` → `[[south, west], [north, east]]`, a Leaflet `LatLngBoundsLiteral`. */
export function toLatLngBounds(bbox: BBox): [[number, number], [number, number]] {
  return [
    [bbox[1], bbox[0]],
    [bbox[3], bbox[2]],
  ];
}

/**
 * The FeatureCollection of a level: the preview, one part, the combined file,
 * or every part concatenated when the level has no combined file (Brazil ADM2).
 */
export async function collection(
  client: GeoWorld,
  iso3: string,
  level: string,
  options: CollectionOptions = {},
): Promise<FeatureCollection> {
  if (options.preview) return client.preview(iso3, level);
  if (options.part !== undefined) return client.getPart(iso3, level, options.part);
  const dataset = await client.dataset(iso3, level);
  if (dataset.path !== undefined) return client.get(iso3, level);
  const features: Feature[] = [];
  for await (const [, part] of client.iterParts(iso3, level)) features.push(...part.features);
  return { type: "FeatureCollection", features };
}

/** The index bbox of the level, or of the part when one is named. */
export async function bboxFor(
  client: GeoWorld,
  iso3: string,
  level: string,
  options: CollectionOptions = {},
): Promise<BBox> {
  const dataset = await client.dataset(iso3, level);
  if (options.part !== undefined) {
    const wanted = options.part.toLowerCase();
    const part = dataset.parts?.find((p) => p.code.toLowerCase() === wanted);
    if (part) return [...part.bbox] as BBox;
  }
  return [...dataset.bbox] as BBox;
}

/** The sub-layer of a GeoJSON layer whose feature has this stable id. */
export function layerById(layer: Leaflet.GeoJSON, id: string): Leaflet.Layer | undefined {
  return layer.getLayers().find((sub) => {
    const feature = (sub as { feature?: { id?: unknown } }).feature;
    return feature !== undefined && feature.id === id;
  });
}

export interface GeoWorldLeaflet {
  /** `new L.LatLngBounds` from an index bbox (`client.bbox(iso3, level)`). */
  bounds(bbox: BBox): Leaflet.LatLngBounds;
  /** A `L.GeoJSON` layer for one level, not yet on a map. */
  boundaries(
    client: GeoWorld,
    iso3: string,
    level: string,
    options?: BoundariesOptions,
  ): Promise<BoundaryLayer>;
  /** `boundaries()` added to the map and, with `fit`, the map fitted to the index bbox. */
  addBoundaries(
    map: Leaflet.Map,
    client: GeoWorld,
    iso3: string,
    level: string,
    options?: AddBoundariesOptions,
  ): Promise<BoundaryLayer>;
}

type GeoJSONInput = ConstructorParameters<LeafletNamespace["GeoJSON"]>[0];

function split(options: BoundariesOptions): {
  collection: CollectionOptions;
  layer: Leaflet.GeoJSONOptions<FeatureProperties>;
} {
  const { part, preview, ...layer } = options;
  const collection: CollectionOptions = {};
  if (part !== undefined) collection.part = part;
  if (preview !== undefined) collection.preview = preview;
  return { collection, layer };
}

/** Bind the adapter to a Leaflet namespace: `withLeaflet(L)` or `withLeaflet(window.L)`. */
export function withLeaflet(L: LeafletNamespace): GeoWorldLeaflet {
  const api: GeoWorldLeaflet = {
    bounds(bbox) {
      return new L.LatLngBounds(toLatLngBounds(bbox));
    },
    async boundaries(client, iso3, level, options = {}) {
      const parts = split(options);
      const fc = await collection(client, iso3, level, parts.collection);
      const layerOptions: Leaflet.GeoJSONOptions<FeatureProperties> = { style: DEFAULT_STYLE, ...parts.layer };
      return new L.GeoJSON<FeatureProperties>(fc as unknown as GeoJSONInput, layerOptions);
    },
    async addBoundaries(map, client, iso3, level, options = {}) {
      const { fit, ...rest } = options;
      const layer = await api.boundaries(client, iso3, level, rest);
      layer.addTo(map);
      if (fit) {
        const bbox = await bboxFor(client, iso3, level, split(rest).collection);
        map.fitBounds(toLatLngBounds(bbox), fit === true ? undefined : fit);
      }
      return layer;
    },
  };
  return api;
}
