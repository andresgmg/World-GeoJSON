/** Errors thrown by the client. All extend `GeoWorldError`. */

export class GeoWorldError extends Error {
  constructor(message: string) {
    super(message);
    this.name = new.target.name;
  }
}

/** No territory with that ISO 3166-1 alpha-3 code in the index. */
export class UnknownCountry extends GeoWorldError {
  constructor(public readonly iso3: string) {
    super(`no territory "${iso3}" in this data version`);
  }
}

/** The territory exists but does not publish that level. */
export class UnknownLevel extends GeoWorldError {
  constructor(
    public readonly iso3: string,
    public readonly level: string,
    public readonly available: string[],
  ) {
    super(`${iso3} has no ${level}; available: ${available.join(", ") || "none"}`);
  }
}

/** The level is split but has no part with that code. */
export class UnknownPart extends GeoWorldError {
  constructor(
    public readonly iso3: string,
    public readonly level: string,
    public readonly code: string,
  ) {
    super(`${iso3} ${level} has no part "${code}"`);
  }
}

/** Parts were requested for a level that is published as one file. */
export class NotSplit extends GeoWorldError {
  constructor(
    public readonly iso3: string,
    public readonly level: string,
  ) {
    super(`${iso3} ${level} is not split into parts; use get()`);
  }
}

/** The level is published as parts only (Brazil ADM2); use `iterParts`. */
export class NoCombinedFile extends GeoWorldError {
  constructor(
    public readonly iso3: string,
    public readonly level: string,
  ) {
    super(
      `${iso3} ${level} has no combined file; use iterParts() or getPart() to read it part by part`,
    );
  }
}

/** The dataset has no simplified preview. */
export class NoPreview extends GeoWorldError {
  constructor(
    public readonly iso3: string,
    public readonly level: string,
  ) {
    super(`${iso3} ${level} has no preview`);
  }
}

/** No feature with that id in its dataset. */
export class UnknownFeature extends GeoWorldError {
  constructor(public readonly featureId: string) {
    super(`no feature "${featureId}"`);
  }
}

/** The string is not a `{ISO3}:{LEVEL}:{key}` id. */
export class InvalidFeatureId extends GeoWorldError {}

/** The index declares a `schema_version` newer than this client understands. */
export class UnsupportedSchema extends GeoWorldError {
  constructor(
    public readonly found: unknown,
    public readonly supported: number,
  ) {
    super(
      `index schema_version ${JSON.stringify(found)} is newer than this client supports (${supported}); upgrade geoworld`,
    );
  }
}

/** A file could not be fetched. */
export class DownloadError extends GeoWorldError {
  constructor(
    public readonly url: string,
    public readonly reason: string,
    public readonly status?: number,
  ) {
    super(`could not fetch ${url}${status ? ` (HTTP ${status})` : ""}: ${reason}`);
  }
}

/** The downloaded bytes do not hash to the `sha256` the index promises. */
export class ChecksumMismatch extends GeoWorldError {
  constructor(
    public readonly path: string,
    public readonly expected: string,
    public readonly actual: string,
  ) {
    super(
      `${path}: sha256 ${actual.slice(0, 12)}… does not match the index (${expected.slice(0, 12)}…)`,
    );
  }
}
