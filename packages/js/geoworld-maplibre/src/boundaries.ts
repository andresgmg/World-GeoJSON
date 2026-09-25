import type { BBox, Feature, FeatureCollection, FeatureProperties, GeoWorld } from "geoworld";
import type {
  FeatureIdentifier,
  FillLayerSpecification,
  FitBoundsOptions,
  GeoJSONSourceSpecification,
  LineLayerSpecification,
  Map as MapLibreMap,
} from "maplibre-gl";

import { fitToBounds } from "./bounds.js";
import { whenStyleReady } from "./ready.js";

export type FillPaint = NonNullable<FillLayerSpecification["paint"]>;
export type LinePaint = NonNullable<LineLayerSpecification["paint"]>;

/**
 * The property that carries the feature id for MapLibre.
 *
 * `promoteId` reads a *property*, not the Feature's own `id`, and MapLibre
 * turns non-numeric ids into `NaN`; so the source data is a shallow copy of
 * the collection with `properties.id = feature.id`, and `promoteId: "id"`
 * makes `setFeatureState` and `e.features[0].id` see `"CHL:ADM1:CL-CO"`.
 */
export const ID_PROPERTY = "id";

export const DEFAULT_FILL: FillPaint = { "fill-color": "#00695c", "fill-opacity": 0.15 };
export const DEFAULT_LINE: LinePaint = { "line-color": "#00695c", "line-width": 1 };

export interface CollectionOptions {
  /** One part of a split level (its ADM1 key, or `"unassigned"`). */
  part?: string;
  /** The simplified preview instead of the full-resolution file. */
  preview?: boolean;
}

/** A feature whose `properties.id` repeats its `id`, for `promoteId`. */
export type PromotedFeature = Omit<Feature, "properties"> & {
  properties: FeatureProperties & { id: string };
};

export interface PromotedCollection {
  type: "FeatureCollection";
  bbox?: BBox;
  features: PromotedFeature[];
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

/** Shallow copies with `properties.id`; the client's cached objects are left untouched. */
export function withIdProperty(fc: FeatureCollection): PromotedCollection {
  const features = fc.features.map(
    (feature): PromotedFeature => ({
      ...feature,
      properties: { ...feature.properties, [ID_PROPERTY]: feature.id },
    }),
  );
  return fc.bbox ? { type: "FeatureCollection", bbox: fc.bbox, features } : { type: "FeatureCollection", features };
}

/** Default source id: `geoworld-CHL-ADM1`, `geoworld-USA-ADM2-US-CA`, `geoworld-CHL-ADM3-preview`. */
export function sourceId(iso3: string, level: string, options: CollectionOptions = {}): string {
  let id = `geoworld-${iso3.toUpperCase()}-${level.toUpperCase()}`;
  if (options.part !== undefined) id += `-${options.part}`;
  if (options.preview) id += "-preview";
  return id;
}

/** A GeoJSON source spec with the verified collection inline and `promoteId` set. */
export async function sourceSpec(
  client: GeoWorld,
  iso3: string,
  level: string,
  options: CollectionOptions = {},
): Promise<GeoJSONSourceSpecification> {
  const fc = await collection(client, iso3, level, options);
  return {
    type: "geojson",
    data: withIdProperty(fc) as unknown as GeoJSONSourceSpecification["data"],
    promoteId: ID_PROPERTY,
  };
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

export interface AddBoundariesOptions extends CollectionOptions {
  /** Source id; defaults to `sourceId(iso3, level, options)`. */
  source?: string;
  /** Fill paint, or `false` for no fill layer. */
  fill?: false | FillPaint;
  /** Line paint, or `false` for no line layer. */
  line?: false | LinePaint;
  /** Insert the layers below this existing layer id. */
  before?: string;
  /** Fit the map to the index bbox before the data arrives. */
  fit?: boolean | FitBoundsOptions;
}

export interface BoundaryLayers {
  readonly source: string;
  /** Layer ids, in the order they were added (`…-fill`, `…-line`). */
  readonly layers: readonly string[];
  readonly bbox: BBox;
  readonly iso3: string;
  readonly level: string;
  /** Remove the layers, then the source. Idempotent; call it before `map.remove()`. */
  remove(): void;
}

/**
 * Add one level as a GeoJSON source plus a fill and a line layer.
 *
 * Fails early on an unknown territory or level, fits the map (when asked)
 * from the index before downloading, waits for the style to be ready, and
 * throws if the source id is already taken: remove the previous handle
 * first rather than silently replacing it.
 */
export async function addBoundaries(
  map: MapLibreMap,
  client: GeoWorld,
  iso3: string,
  level: string,
  options: AddBoundariesOptions = {},
): Promise<BoundaryLayers> {
  const dataset = await client.dataset(iso3, level);
  const bbox = await bboxFor(client, iso3, level, options);
  if (options.fit) fitToBounds(map, bbox, options.fit === true ? undefined : options.fit);
  const spec = await sourceSpec(client, iso3, level, options);
  await whenStyleReady(map);
  const source = options.source ?? sourceId(iso3, level, options);
  if (map.getSource(source)) {
    throw new Error(`source "${source}" already exists; call remove() on the previous handle first`);
  }
  map.addSource(source, spec);
  const layers: string[] = [];
  if (options.fill !== false) {
    const fill: FillLayerSpecification = {
      id: `${source}-fill`,
      type: "fill",
      source,
      paint: options.fill ?? DEFAULT_FILL,
    };
    map.addLayer(fill, options.before);
    layers.push(fill.id);
  }
  if (options.line !== false) {
    const line: LineLayerSpecification = {
      id: `${source}-line`,
      type: "line",
      source,
      paint: options.line ?? DEFAULT_LINE,
    };
    map.addLayer(line, options.before);
    layers.push(line.id);
  }
  return {
    source,
    layers,
    bbox,
    iso3: iso3.toUpperCase(),
    level: dataset.level,
    remove(): void {
      for (const id of [...layers].reverse()) if (map.getLayer(id)) map.removeLayer(id);
      if (map.getSource(source)) map.removeSource(source);
    },
  };
}

/** `map.setFeatureState({ source, id }, state)` with the stable feature id. */
export function setFeatureState(
  map: MapLibreMap,
  source: string,
  id: string,
  state: Record<string, unknown>,
): void {
  map.setFeatureState({ source, id }, state);
}

/** Clear feature state for one feature (or the whole source), optionally one key only. */
export function clearFeatureState(map: MapLibreMap, source: string, id?: string, key?: string): void {
  const target: FeatureIdentifier = { source };
  if (id !== undefined) target.id = id;
  map.removeFeatureState(target, key);
}
