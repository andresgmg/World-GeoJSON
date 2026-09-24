# Roadmap

Honest about what is done, what is next, and what is aspirational.

## Now — foundations

Putting conventions and tooling in place before the data grows.

- [x] Documentation site with MkDocs + Material
- [x] Written conventions: naming, admin levels, property schema, CRS,
      planetary
- [x] Licensing policy and approved-source list
- [x] Disputed-boundaries policy
- [x] Catalog generator wired to manifests
- [x] CI building and deploying the site
- [x] Ingestion pipeline: fetch, normalise, simplify, split, manifest, preview
- [x] Chile from IDE Chile DPA 2023 — ADM1, ADM2 and ADM3
- [x] Preview generation and interactive maps
- [x] Data validation workflow with a licence allow-list

## Done — the Americas

**55 territories, 95 datasets, 16,195 features.** Country outlines from Natural
Earth; first-level and municipal tiers from geoBoundaries under permissive
licences only; Chile from IDE Chile.

Two of the 57 UN M49 territories ship nothing: **Bonaire, Sint Eustatius and
Saba** and **Bouvet Island** are absent from Natural Earth under their ISO codes
and have no permissively licensed subdivision data.

### Coverage gaps

**Fifteen countries have no first-level divisions here** because their
geoBoundaries ADM1 is copyleft — ODbL for Colombia, Costa Rica, Cuba,
Guatemala, Guyana, Honduras, Haiti, Nicaragua, Panama, Suriname, Trinidad and
Tobago, Uruguay and Saint Vincent and the Grenadines; CC-BY-SA for Grenada and
Greenland. Several of them do have a permissively licensed municipal tier, so
they appear in the catalog with an ADM2 and no ADM1 above it.

Closing a gap means finding a national SDI or an HDX release under permissive
terms — not relaxing the rule. See
[Approved sources](../contributing/sources.md).

Also outstanding for this continent:

- [ ] Peru's districts — geoBoundaries stops at its 196 provinces
- [ ] Verify the suspect unit counts before trusting them: Jamaica ADM2 (827
      against 14 parishes) and Saint Lucia ADM2 (547 against 10 quarters) look
      mis-tiered and were left out; Bahamas ADM1/ADM2 (32/34) are near-identical
- [ ] Guadeloupe, Martinique, French Guiana and the US Virgin Islands have a
      municipal tier but no ADM1 upstream, so they cannot be split
- [ ] Translate generated catalog pages into Spanish

## Next — from data repository to platform

The Americas proved the pipeline. The next releases turn the repository into
something a program can depend on: first a stable contract, then the tooling,
then libraries that speak it. In order:

**Phase 0 — engineering hygiene** (this pull request)

- [x] Lint, type checks and tests — `ruff`, `mypy`, `pytest` — run by a CI
      workflow on every pull request
- [x] Pipeline bug fixes, listed in the [Changelog](changelog.md)
- [x] Every documentation page brought in line with what the data contains

**Phase 1 — data contract v1**

- [ ] `data/index.json`: one file listing every territory, level and file with
      `bytes`, `sha256`, `bbox` and licence
- [ ] JSON Schemas in `schemas/` for the manifest, the index and feature
      properties
- [ ] A stable Feature `id` on every feature: `{ISO3}:{LEVEL}:{code}`
- [ ] `parentID` and `adm1ISO` on every sub-national feature, not only Chile's
- [ ] `shapeISO` no longer filled with opaque geoBoundaries ids, and the
      duplicated codes resolved
- [ ] Tagged data releases: tag `v1.0.0` and publish a GitHub Release with
      per-country zips

**Phase 2 — the pipeline as a package**

- [ ] The scripts become an installable Python package with a `wgj` CLI, tests
      and fixtures
- [ ] Previews generated from Python (mapshaper still runs through Node)

**Phase 3 — client libraries**

- [ ] Python `world-geojson` on PyPI
- [ ] TypeScript `@world-geojson/core` on npm

Both are thin clients: read `index.json` from a pinned data version, download
on demand, cache, verify `sha256`. No server involved — they fetch static files.

**Phase 4 — framework adapters and onboarding**

- [ ] `@world-geojson/react`, `@world-geojson/leaflet`, `@world-geojson/maplibre`
- [ ] Worked examples
- [ ] Issue and PR templates for country submissions

## Next — the other continents

One PR each, reusing the pipeline: Europe, Africa, Asia, Oceania.

## Later — global coverage

- [ ] ADM0 for every country (Natural Earth is the obvious starting point)
- [ ] ADM1 for every country (geoBoundaries)
- [ ] ADM2 where openly licensed sources exist
- [ ] TopoJSON alongside GeoJSON
- [ ] Versioned documentation (tagged data releases moved up to Phase 1)

ADM3 is explicitly not a goal at global scale. Very few countries publish it
openly and the file sizes become unmanageable.

## Eventually — the Moon and Mars

The conventions are [already written](../reference/planetary.md), deliberately:
the latitude convention in particular cannot be inferred from the data after
the fact, so getting it wrong is expensive to discover and expensive to fix.

- [ ] Lunar quadrangles, IAU 2015 body-fixed frame
- [ ] Martian quadrangles
- [ ] Named surface features from the IAU Gazetteer
- [ ] USGS Astrogeology WMS basemaps in preview maps

## Known data problems

Tracked, not hidden.

| Problem | Where | Status |
|---|---|---|
| Antártica commune (12202) absent — 345 of 346 | Chile ADM3 | Won't fix; the official DPA package excludes the Antarctic claim |
| 15 countries have no permissively licensed ADM1 | Americas | Awaiting a permissive source |
| `shapeISO` holds the opaque geoBoundaries id instead of a code on 22 municipal datasets | e.g. USA ADM2, MEX ADM2, BRA ADM2 — full list in the [Property dictionary](../reference/properties.md#known-issues-fixed-in-v100) | Fixed in v1.0.0 (planned) |
| `shapeISO` is not unique | BLZ ADM2; MEX ADM1 (`MX-MEX` ×2); ECU ADM1 (`EC-H` ×2) | Fixed in v1.0.0 (planned) |
| South Dakota's counties filed under geoBoundaries' typo `SU-SD` | USA ADM2 | Passed through and noted in the manifest; fixed in v1.0.0 (planned) |
| Municipal tier assignment unverified for 19 territories | `scripts/countries.json` | Marked `verify` and shipped as `review` |
| Peru's districts unavailable — geoBoundaries stops at provinces | Peru | Awaiting a source |
| Legacy files still at the repository root | `comunas.geojson` and friends | Deprecated; stay through 1.x, removed in v2.0.0 |

## Not planned

- **A hosted API or tile service.** This is a data repository, and the
  libraries in Phase 3 are client-side: they fetch static files. Cloudflare,
  jsDelivr and your own CDN do the serving better.
- **Geocoding or address data.** Different problem, different sources.
- **Historical boundaries.** Interesting, and a project of its own.
- **Sub-metre accuracy.** These are administrative boundaries, not cadastral
  surveys.

## Contributing to the roadmap

[Open an issue.](https://github.com/andresgmg/World-GeoJSON/issues) Countries
where you have local knowledge of the authoritative open source are especially
useful — finding a legally usable source is consistently the hardest part.

--8<-- "abbreviations.md"
