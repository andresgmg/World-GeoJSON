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

**Phase 0 — engineering hygiene** (done)

- [x] Lint, type checks and tests — `ruff`, `mypy`, `pytest` — run by a CI
      workflow on every pull request
- [x] Pipeline bug fixes, listed in the [Changelog](changelog.md)
- [x] Every documentation page brought in line with what the data contains

**Phase 1 — data contract v1** (done; `v1.0.0` is tagged from the merge)

- [x] `data/index.json`: one file listing every territory, level and file with
      `bytes`, `sha256`, `bbox` and licence — see
      [Global index & schemas](../reference/index-json.md)
- [x] JSON Schemas in `schemas/` for the manifest, the index, a feature, its
      properties and the country registry, applied in CI
- [x] A stable Feature `id` on every feature: `{ISO3}:{LEVEL}:{key}`
- [x] `parentID`, `parentISO` and `adm1ISO` on every sub-national feature,
      not only Chile's
- [x] `shapeISO` no longer filled with opaque geoBoundaries ids, and the
      duplicated codes resolved (`US-SD`, `MX-CMX`, `EC-X`, Belize cleared)
- [x] A finalize step (now `wgj finalize`) that writes all of the
      above and the canonical file layout, checked in CI
- [x] Tagged data releases: a release workflow that publishes a GitHub Release
      with per-country zips, `index.json` and `SHA256SUMS` on every tag
      (tag pending merge)

**Phase 2 — the pipeline as a package** (done)

- [x] The scripts became an installable Python package, `wgj` under
      `pipeline/`, with a CLI — `wgj fetch`, `build`, `finalize`, `previews`,
      `manifest`, `index`, `validate` and `all` — documented in
      [Data pipeline](../contributing/pipeline.md)
- [x] Tests that run on `fixtures/data/` — three small territories and their
      index — so CI needs no data checkout
- [x] Previews generated from Python (mapshaper still runs through Node)

`scripts/*.py` stay as compatibility shims for one release and retire in
Phase 4, as planned.

**Phase 3 — client libraries** (done; first publication pending)

- [x] Python `geoworld` (`packages/python/geoworld`, PyPI)
- [x] TypeScript `geoworld` (`packages/js/geoworld`, npm)
- [ ] Published: `python-v0.1.0` and `js-v0.1.0` tags, once the PyPI and npm
      publishers are configured

Both are thin clients with the same API: read `index.json` from a pinned data
version, download on demand, cache, verify `sha256`, navigate by `id`. No
server involved — they fetch static files. See
[Client libraries](../libraries/index.md).

**Phase 4 — framework adapters and onboarding**

- [x] `geoworld-maplibre`, `geoworld-leaflet` and `geoworld-react` on top of
      `geoworld` — see [Client libraries](../libraries/index.md)
- [x] Worked examples in `examples/` (Leaflet, MapLibre, React; no build step)
- [ ] Issue and PR templates for country submissions
- [ ] Remove the `scripts/*.py` compatibility shims kept since Phase 2

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
| Most municipal units have no official code upstream, so `shapeISO` is `""` on 15,364 features | 22 municipal datasets from geoBoundaries | By design since 1.0.0 — an empty code is honest, an opaque id was not. Use `id`; a national source with codes would close it |
| 169 name-keyed ids carry a numeric suffix (`COL:ADM2:albania-2`) because the upstream has several units with the same name and no code | COL 84, HND 28, SLV 18, ARG 16, GTM 6, USA 6, MEX 4, BLZ 2, BRA 2, VIR 2, SUR 1 | Stable per data version; may renumber on an upstream refresh — pin a version |
| 12 municipal units overlap no ADM1 parent | ARG ADM2 (8, Buenos Aires city), BRA ADM2 (3), USA ADM2 (1) | Kept in `unassigned` parts with `adm1ISO: "unassigned"` and no `parentID` |
| Municipal tier assignment unverified for 19 territories | `pipeline/src/wgj/tables/countries.json` | Marked `verify` and shipped as `review` |
| Peru's districts unavailable — geoBoundaries stops at provinces | Peru | Awaiting a source |
| Legacy files still at the repository root | `comunas.geojson` and friends | Deprecated; stay through 1.x, removed in v2.0.0 |

## Not planned

- **A hosted API or tile service.** This is a data repository, and the
  [client libraries](../libraries/index.md) are client-side: they fetch
  static files. Cloudflare,
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
