/**
 * Shapes of what the client returns, mirroring `schemas/` in the repository.
 *
 * Written by hand from `index.schema.json`, `manifest.schema.json` and
 * `feature.schema.json` so the package needs no code generator. Everything is
 * plain JSON: what `response.json()` gives back is what you get.
 */

export type Body = "earth" | "moon" | "mars";
/** `ADM0` … `ADM4` or `QUAD`. */
export type Level = string;
export type Status = "ok" | "review" | "deprecated";
/** `[west, south, east, north]` in degrees. */
export type BBox = [number, number, number, number];

export interface Localised {
  en: string;
  es?: string;
}

export interface Crs {
  authority: string;
  code: string;
  epsg: number;
}

export interface Source {
  name: string;
  url: string;
  license: string;
  licenses?: string[];
  retrieved: string;
}

export interface Simplification {
  method: "visvalingam" | "douglas-peucker" | "none";
  tolerance_m: number;
}

export interface GeometryTypes {
  Polygon?: number;
  MultiPolygon?: number;
}

/** One file of a split level: `data/{body}/{ISO3}/{LEVEL}/{code}.geojson`. */
export interface Part {
  code: string;
  path: string;
  bytes: number;
  sha256: string;
  features: number;
  bbox: BBox;
  geometry_types: GeometryTypes;
  properties: string[];
}

export interface Dataset {
  level: Level;
  /** Absent when the level is published as parts only (Brazil ADM2). */
  path?: string;
  bytes: number;
  sha256?: string;
  features: number;
  bbox: BBox;
  geometry_types: GeometryTypes;
  properties: string[];
  preview?: string;
  preview_bytes?: number;
  simplification?: Simplification;
  license: string;
  src_provider?: string;
  src_year?: string | number;
  unassigned?: number;
  split_by?: "ADM1";
  parts?: Part[];
}

export interface Terms {
  adm1?: Localised;
  adm2?: Localised;
  municipal?: Localised;
}

/** One entry of `index.countries`: the manifest plus derived fields. */
export interface Country {
  body: Body;
  iso_a3: string;
  iso_a2?: string;
  m49_region?: string;
  name: Localised;
  status: Status;
  manifest: string;
  license: string;
  licenses: string[];
  levels: Level[];
  municipal_level: Level | null;
  terms?: Terms;
  crs: Crs;
  source: Source;
  notes?: string;
  datasets: Dataset[];
}

export interface Totals {
  countries: number;
  datasets: number;
  features: number;
  bytes: number;
}

/** `data/index.json`: every territory and dataset in one file. */
export interface Index {
  schema_version: number;
  bodies: Body[];
  totals: Totals;
  countries: Country[];
}

/** What `countries()` returns: the index entry without its datasets. */
export interface CountrySummary {
  iso_a3: string;
  iso_a2: string | null;
  name: Localised;
  m49_region: string | null;
  status: Status;
  license: string;
  licenses: string[];
  levels: Level[];
  municipal_level: Level | null;
  datasets: number;
  features: number;
  bytes: number;
}

/**
 * The documented keys of a feature's `properties`. `src_*` keys carry verbatim
 * upstream attributes and vary by source.
 */
export interface FeatureProperties {
  shapeName: string;
  shapeISO: string;
  shapeGroup: string;
  shapeType: Level;
  adm1ISO?: string;
  parentISO?: string;
  parentID?: string;
  [key: `src_${string}`]: string | number | boolean | null;
}

export interface Geometry {
  type: "Polygon" | "MultiPolygon";
  coordinates: unknown;
}

export interface Feature {
  type: "Feature";
  /** `{ISO3}:{LEVEL}:{key}`, unique within a data version. */
  id: string;
  properties: FeatureProperties;
  geometry: Geometry;
  bbox?: BBox;
}

export interface FeatureCollection {
  type: "FeatureCollection";
  bbox?: BBox;
  features: Feature[];
}

/** A parsed feature id. */
export interface FeatureId {
  iso3: string;
  level: Level;
  key: string;
}
