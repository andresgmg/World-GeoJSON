/** The client: a pinned data version, an index, files fetched on demand. */

import { type CacheLike, MemoryCache } from "./cache.js";
import {
  ChecksumMismatch,
  DownloadError,
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
import type {
  BBox,
  Country,
  CountrySummary,
  Dataset,
  Feature,
  FeatureCollection,
  FeatureId,
  Index,
  Part,
} from "./types.js";
import { sha256Hex } from "./verify.js";

export const VERSION = "0.2.0";

/** The newest `index.schema_version` this client understands. */
export const SUPPORTED_SCHEMA_VERSION = 1;

/** The data release used when none is given. */
export const DEFAULT_DATA_VERSION = "1.0.0";

/** Files are read from `${DEFAULT_BASE_URL}/v${version}/${path}` unless `baseUrl` is given. */
export const DEFAULT_BASE_URL = "https://raw.githubusercontent.com/andresgmg/World-GeoJSON";

export const INDEX_PATH = "data/index.json";

const FEATURE_ID = /^([A-Z]{3}):(ADM[0-4]|QUAD):(\S+)$/;

/** Split `"CHL:ADM3:01402"` into its territory, level and key. */
export function parseId(featureId: string): FeatureId {
  const match = FEATURE_ID.exec(featureId);
  if (!match) {
    throw new InvalidFeatureId(
      `not a feature id ({ISO3}:{LEVEL}:{key}): ${JSON.stringify(featureId)}`,
    );
  }
  return { iso3: match[1]!, level: match[2]!, key: match[3]! };
}

/**
 * Accent- and case-insensitive form used by `search()`. Mirrors the Python
 * client exactly (NFKD, drop marks, lower-case, collapse whitespace).
 */
export function normalise(text: string): string {
  return text
    .normalize("NFKD")
    .replace(/\p{M}/gu, "")
    .toLowerCase()
    .split(/\s+/)
    .filter(Boolean)
    .join(" ");
}

/** The index entry without its datasets, plus totals across them. */
export function summarise(country: Country): CountrySummary {
  const datasets = country.datasets;
  return {
    iso_a3: country.iso_a3,
    iso_a2: country.iso_a2 ?? null,
    name: country.name,
    m49_region: country.m49_region ?? null,
    status: country.status,
    license: country.license,
    licenses: [...country.licenses],
    levels: [...country.levels],
    municipal_level: country.municipal_level,
    datasets: datasets.length,
    features: datasets.reduce((sum, d) => sum + d.features, 0),
    bytes: datasets.reduce((sum, d) => sum + d.bytes, 0),
  };
}

export interface ClientOptions {
  /** A data release tag without the `v` (`"1.0.0"`), or `"main"` to follow the branch (warns). */
  version?: string;
  /**
   * Where the repository tree is served from. Defaults to
   * `raw.githubusercontent.com` at the release tag; any static host with the
   * same layout works.
   */
  baseUrl?: string;
  /** A `fetch` implementation; defaults to the global one. */
  fetch?: typeof globalThis.fetch;
  /**
   * `"memory"` (default) keeps parsed files for the life of the client;
   * `"none"` refetches on every call (the index is still read once); a
   * `CacheLike` also persists the raw bytes, e.g. `diskCache()` from
   * `geoworld/node`.
   */
  cache?: "memory" | "none" | CacheLike;
  /**
   * Check every download and cached file against the `sha256` in the index
   * (default `true`). Previews are not hashed upstream and are not checked.
   */
  verify?: boolean;
  /** Abort a request after this many milliseconds. */
  timeoutMs?: number;
  /** Extra request headers. */
  headers?: Record<string, string>;
}

export interface UrlOptions {
  part?: string;
  preview?: boolean;
}

/**
 * Read one version of the World GeoJSON data.
 *
 * Objects returned by `get`, `getPart`, `preview` and `index` are cached in
 * memory and shared between calls: copy them before mutating.
 */
export class GeoWorld {
  readonly version: string;
  readonly baseUrl: string;
  readonly verify: boolean;
  private readonly fetchImpl: typeof globalThis.fetch;
  private readonly store: CacheLike | null;
  private readonly memo: Map<string, Promise<unknown>> | null;
  private readonly timeoutMs: number | undefined;
  private readonly headers: Record<string, string>;
  private indexPromise: Promise<Index> | null = null;

  constructor(options: ClientOptions = {}) {
    this.version = String(options.version ?? DEFAULT_DATA_VERSION);
    const ref = this.version === "main" ? "main" : `v${this.version}`;
    this.baseUrl = (options.baseUrl ?? `${DEFAULT_BASE_URL}/${ref}`).replace(/\/+$/, "");
    this.verify = options.verify ?? true;
    this.timeoutMs = options.timeoutMs;
    this.headers = { "user-agent": `geoworld-js/${VERSION}`, ...options.headers };
    const fetchImpl = options.fetch ?? globalThis.fetch;
    if (typeof fetchImpl !== "function") {
      throw new TypeError("no fetch available: pass one in options.fetch");
    }
    this.fetchImpl = fetchImpl;
    let cache = options.cache ?? "memory";
    if (this.version === "main") {
      console.warn(
        "geoworld: version 'main' follows a moving branch: results change between runs and " +
          "nothing is persisted. Pin a release, e.g. createClient({ version: '1.0.0' }).",
      );
      if (typeof cache !== "string") cache = "memory";
    }
    this.store = typeof cache === "string" ? null : cache;
    this.memo = cache === "none" ? null : new Map();
  }

  // -- transport ------------------------------------------------------------

  /** Absolute URL of a repository path such as `data/index.json`. */
  urlFor(path: string): string {
    return `${this.baseUrl}/${path}`;
  }

  private async download(url: string): Promise<Uint8Array> {
    const init: RequestInit = { headers: this.headers };
    if (this.timeoutMs !== undefined) init.signal = AbortSignal.timeout(this.timeoutMs);
    // Called as a plain function, not as `this.fetchImpl(...)`: a browser's
    // native fetch throws "Illegal invocation" when its receiver is not the
    // window, and calling through a local binding leaves the receiver undefined.
    const fetchImpl = this.fetchImpl;
    let response: Response;
    try {
      response = await fetchImpl(url, init);
    } catch (error) {
      throw new DownloadError(url, error instanceof Error ? error.message : String(error));
    }
    if (!response.ok) {
      throw new DownloadError(url, response.statusText || "request failed", response.status);
    }
    return new Uint8Array(await response.arrayBuffer());
  }

  private async read(path: string, sha256?: string): Promise<Uint8Array> {
    const expected = this.verify ? sha256 : undefined;
    const key = `${this.version}/${path}`;
    if (this.store) {
      const cached = await this.store.get(key);
      if (cached) {
        if (expected === undefined || (await sha256Hex(cached)) === expected) return cached;
        await this.store.delete(key);
      }
    }
    const data = await this.download(this.urlFor(path));
    if (expected !== undefined) {
      const actual = await sha256Hex(data);
      if (actual !== expected) throw new ChecksumMismatch(path, expected, actual);
    }
    if (this.store) await this.store.set(key, data);
    return data;
  }

  private load<T>(path: string, sha256?: string): Promise<T> {
    const memoised = this.memo?.get(path) as Promise<T> | undefined;
    if (memoised) return memoised;
    const pending = this.read(path, sha256).then(
      (bytes) => JSON.parse(new TextDecoder().decode(bytes)) as T,
    );
    if (this.memo) {
      this.memo.set(path, pending);
      pending.catch(() => this.memo?.delete(path));
    }
    return pending;
  }

  /** Forget everything held in memory and, by default, in the persistent store. */
  async clearCache(options: { store?: boolean } = {}): Promise<void> {
    this.memo?.clear();
    this.indexPromise = null;
    if ((options.store ?? true) && this.store) await this.store.clear();
  }

  // -- index ----------------------------------------------------------------

  /** `data/index.json` for this version, fetched once. */
  index(): Promise<Index> {
    if (!this.indexPromise) {
      this.indexPromise = this.load<unknown>(INDEX_PATH).then((raw) => {
        const found =
          raw && typeof raw === "object" ? (raw as { schema_version?: unknown }).schema_version : undefined;
        if (typeof found !== "number" || found > SUPPORTED_SCHEMA_VERSION) {
          throw new UnsupportedSchema(found, SUPPORTED_SCHEMA_VERSION);
        }
        return raw as Index;
      });
      this.indexPromise.catch(() => {
        this.indexPromise = null;
      });
    }
    return this.indexPromise;
  }

  /** Every territory in the index, without the per-dataset detail. */
  async countries(): Promise<CountrySummary[]> {
    return (await this.index()).countries.map(summarise);
  }

  /** The full index entry of one territory. */
  async country(iso3: string): Promise<Country> {
    const code = iso3.toUpperCase();
    const found = (await this.index()).countries.find((c) => c.iso_a3 === code);
    if (!found) throw new UnknownCountry(code);
    return found;
  }

  /** Published levels, lowest number first (`["ADM0", "ADM1", …]`). */
  async levels(iso3: string): Promise<string[]> {
    return [...(await this.country(iso3)).levels];
  }

  /** The index entry of one level of one territory. */
  async dataset(iso3: string, level: string): Promise<Dataset> {
    const country = await this.country(iso3);
    const wanted = level.toUpperCase();
    const found = country.datasets.find((d) => d.level === wanted);
    if (!found) throw new UnknownLevel(country.iso_a3, wanted, [...country.levels]);
    return found;
  }

  /** `[west, south, east, north]` of a level, from the index (no download). */
  async bbox(iso3: string, level: string): Promise<BBox> {
    return [...(await this.dataset(iso3, level)).bbox] as BBox;
  }

  /** Part codes of a split level, in index order. */
  async parts(iso3: string, level: string): Promise<string[]> {
    return (await this.partList(iso3, level)).map((p) => p.code);
  }

  /** URL of a level's file, one of its parts, or its preview (no download). */
  async url(iso3: string, level: string, options: UrlOptions = {}): Promise<string> {
    const dataset = await this.dataset(iso3, level);
    if (options.preview) {
      if (options.part !== undefined) {
        throw new TypeError("previews cover whole levels; give either part or preview");
      }
      return this.urlFor(previewPath(dataset, iso3));
    }
    if (options.part !== undefined) {
      return this.urlFor((await this.part(iso3, level, options.part)).path);
    }
    if (dataset.path === undefined) throw new NoCombinedFile(iso3.toUpperCase(), dataset.level);
    return this.urlFor(dataset.path);
  }

  // -- files ----------------------------------------------------------------

  /** The full-resolution FeatureCollection of a level. */
  async get(iso3: string, level: string): Promise<FeatureCollection> {
    const dataset = await this.dataset(iso3, level);
    if (dataset.path === undefined) throw new NoCombinedFile(iso3.toUpperCase(), dataset.level);
    return this.load<FeatureCollection>(dataset.path, dataset.sha256);
  }

  /** One part of a split level (`code` is the ADM1 key, or `"unassigned"`). */
  async getPart(iso3: string, level: string, code: string): Promise<FeatureCollection> {
    const part = await this.part(iso3, level, code);
    return this.load<FeatureCollection>(part.path, part.sha256);
  }

  /** `[code, FeatureCollection]` for every part of a split level, in index order. */
  async *iterParts(iso3: string, level: string): AsyncGenerator<[string, FeatureCollection]> {
    for (const part of await this.partList(iso3, level)) {
      yield [part.code, await this.load<FeatureCollection>(part.path, part.sha256)];
    }
  }

  /** The simplified preview of a level (≤ 2 MB; name, code and type properties only). */
  async preview(iso3: string, level: string): Promise<FeatureCollection> {
    const dataset = await this.dataset(iso3, level);
    return this.load<FeatureCollection>(previewPath(dataset, iso3));
  }

  /** Every feature of a level, from the combined file or across its parts. */
  async *features(iso3: string, level: string): AsyncGenerator<Feature> {
    const dataset = await this.dataset(iso3, level);
    if (dataset.path !== undefined) {
      yield* (await this.get(iso3, level)).features;
    } else {
      for await (const [, collection] of this.iterParts(iso3, level)) yield* collection.features;
    }
  }

  // -- navigation -----------------------------------------------------------

  /** The feature with this id, downloading only what is needed to reach it. */
  async find(featureId: string): Promise<Feature> {
    const parsed = parseId(featureId);
    const dataset = await this.dataset(parsed.iso3, parsed.level);
    if (dataset.parts?.length) {
      // Municipal keys are "{adm1 key}.{slug}" when the upstream has no code,
      // and that adm1 key names the part: one small file instead of the
      // combined one.
      const prefix = parsed.key.split(".", 1)[0]!;
      if (dataset.parts.some((p) => p.code === prefix)) {
        const collection = await this.getPart(parsed.iso3, parsed.level, prefix);
        const found = collection.features.find((f) => f.id === featureId);
        if (found) return found;
      }
    }
    for await (const feature of this.features(parsed.iso3, parsed.level)) {
      if (feature.id === featureId) return feature;
    }
    throw new UnknownFeature(featureId);
  }

  /** The feature named by `parentID`, or `null` at the top level. */
  async parent(featureId: string): Promise<Feature | null> {
    const parentId = (await this.find(featureId)).properties.parentID;
    return parentId ? this.find(parentId) : null;
  }

  /** Features of the next published level whose `parentID` is this id. */
  async children(featureId: string): Promise<Feature[]> {
    const parsed = parseId(featureId);
    const country = await this.country(parsed.iso3);
    const position = country.levels.indexOf(parsed.level);
    if (position < 0) throw new UnknownLevel(country.iso_a3, parsed.level, [...country.levels]);
    const childLevel = country.levels[position + 1];
    if (childLevel === undefined) return [];
    const dataset = await this.dataset(parsed.iso3, childLevel);
    const hits: Feature[] = [];
    if (parsed.level === "ADM1" && dataset.parts?.some((p) => p.code === parsed.key)) {
      // A split level's parts are keyed by ADM1: the children all live in one part.
      const collection = await this.getPart(parsed.iso3, childLevel, parsed.key);
      for (const f of collection.features) if (f.properties.parentID === featureId) hits.push(f);
      return hits;
    }
    for await (const f of this.features(parsed.iso3, childLevel)) {
      if (f.properties.parentID === featureId) hits.push(f);
    }
    return hits;
  }

  /**
   * Features whose `shapeName` contains `text` (accent- and case-insensitive)
   * or whose `shapeISO` equals it, in one territory and, optionally, one level.
   */
  async search(text: string, iso3: string, level?: string): Promise<Feature[]> {
    const query = normalise(text);
    if (!query) return [];
    const levels = level ? [level.toUpperCase()] : await this.levels(iso3);
    const hits: Feature[] = [];
    for (const each of levels) {
      for await (const feature of this.features(iso3, each)) {
        const props = feature.properties;
        const name = normalise(String(props.shapeName ?? ""));
        const code = normalise(String(props.shapeISO ?? ""));
        if (name.includes(query) || (code !== "" && code === query)) hits.push(feature);
      }
    }
    return hits;
  }

  // -- helpers --------------------------------------------------------------

  private async partList(iso3: string, level: string): Promise<Part[]> {
    const dataset = await this.dataset(iso3, level);
    if (!dataset.parts?.length) throw new NotSplit(iso3.toUpperCase(), dataset.level);
    return dataset.parts;
  }

  private async part(iso3: string, level: string, code: string): Promise<Part> {
    const parts = await this.partList(iso3, level);
    const exact = parts.find((p) => p.code === code);
    if (exact) return exact;
    const folded = code.toLowerCase();
    const loose = parts.find((p) => p.code.toLowerCase() === folded);
    if (loose) return loose;
    throw new UnknownPart(iso3.toUpperCase(), level.toUpperCase(), code);
  }
}

function previewPath(dataset: Dataset, iso3: string): string {
  if (!dataset.preview) throw new NoPreview(iso3.toUpperCase(), dataset.level);
  return dataset.preview;
}

/** Same as `new GeoWorld(options)`. */
export function createClient(options: ClientOptions = {}): GeoWorld {
  return new GeoWorld(options);
}
