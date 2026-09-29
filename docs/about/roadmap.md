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

## Done — Europe

**51 territories, 97 datasets, 59,265 features.** The same pipeline and
sources as the Americas: outlines from Natural Earth, first-level and municipal
tiers from geoBoundaries under permissive licences only. geoBoundaries is now
read from a pinned commit of its repository rather than its API, so a rebuild
fetches exactly the same files.

Three attribution-only licences joined the allow-list for national data that
geoBoundaries redistributes: the UK's Open Government Licence v3.0, Germany's
Data licence Germany – attribution – 2.0 and Open Data Commons Attribution 1.0
(France's communes). France's 35,010 communes also add a fifth level, ADM5, to
the contract.

Seventeen countries have both a first level and a municipal tier: Belgium,
Bulgaria, Bosnia and Herzegovina, Belarus, Germany, Denmark, Spain, France,
the United Kingdom, Greece, Ireland, Italy, North Macedonia, the Netherlands,
Norway, Romania and Sweden. Kosovo is published as `XKX`, a user-assigned
code, with the dispute stated in its manifest — see
[Disputed boundaries](disputed-boundaries.md). **Svalbard and Jan Mayen**
ships nothing: Natural Earth draws both inside Norway's outline.

### Coverage gaps

**Nineteen countries have no first-level divisions here.** Their geoBoundaries
ADM1 is ODbL (Estonia, Finland, Croatia, Iceland, Liechtenstein, Lithuania,
Luxembourg, Monaco, Montenegro, Poland, Portugal, Russia, San Marino, Serbia,
Slovakia, Ukraine), CC-BY-SA (Austria, Kosovo) or under swisstopo's own
licence, which is not on the allow-list (Switzerland). Iceland, Luxembourg,
Portugal and Ukraine have a permissively licensed municipal tier, published
without an ADM1 above it. Åland, the Faroe Islands, Guernsey, Gibraltar, the
Isle of Man, Jersey and Vatican City have nothing below the outline upstream.

**Seventeen countries have no municipal tier here** because it is copyleft
or under a licence not on the allow-list: Austria, Switzerland, Czechia,
Estonia, Finland, Croatia, Hungary, Lithuania, Poland, Russia, Serbia,
Slovakia, Slovenia and Kosovo, plus Liechtenstein, Montenegro and San Marino,
whose municipalities are their first level. Czechia, Hungary and Slovenia
still publish their first level. Albania's 61 municipalities and Moldova's
communes are not in geoBoundaries at all.

Also outstanding for this continent:

- [ ] Intermediate levels. The pipeline builds ADM1 and one municipal tier
      per country, so permissively licensed levels in between are not here
      yet: France's 96 départements and 320 arrondissements, Italy's 20
      regions and 107 provinces, Germany's 38 government regions, Czechia's
      77 districts, Belgium's 43 arrondissements, and the second levels of
      Greece (14 units) and Bosnia and Herzegovina (12)
- [ ] Germany's municipalities (Gemeinden) — not in geoBoundaries; the
      published tier is the 401 districts
- [ ] Newer vintages where a reform has happened since: Belgium's 2019
      mergers, Norway's 2020 and 2024 reforms, Ukraine's 2020 raions,
      Iceland's mergers (74 units against 64), Albania's 2015 municipalities
- [ ] Catalog previews for the three levels too dense for 2 MB even at the
      coarsest simplification: Spain ADM3, France ADM5 and Italy ADM4

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

`scripts/*.py` stayed as compatibility shims for one release and were
retired in Phase 4, as planned.

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
- [x] Issue forms (new country, data problem, library bug), a pull request
      template and `CODEOWNERS`
- [x] The `scripts/*.py` compatibility shims kept since Phase 2 are removed

## Next — the other continents

One PR each, reusing the pipeline: Africa, Asia, Oceania.

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
| 19 countries have no permissively licensed ADM1 | Europe | Awaiting a permissive source |
| `shapeISO` is `""` on 58,492 features — every European municipal dataset but Portugal's | 20 municipal datasets from geoBoundaries | By design, as above; use `id` |
| 863 name-keyed ids carry a numeric suffix. Some are true namesakes (Lagoa and Calheta in Portugal, San Teodoro in Italy); others are one municipality drawn as several features upstream | FRA 791, ROU 48, UKR 10, NOR 6, PRT 5, BGR 1, GRC 1, ITA 1 | Stable per data version; may renumber on an upstream refresh — pin a version |
| 129 communes overlap none of the 13 metropolitan regions | FRA ADM5 (the five overseas departments) | Kept in `ADM5/unassigned.geojson` |
| No combined file: the level is published as its region parts only | FRA ADM5 | By design — a single file would exceed the 18 MiB budget. Use the parts (`iter_parts`) |
| No catalog preview: over 2 MB even at the coarsest simplification | ESP ADM3, FRA ADM5, ITA ADM4 | The data files are complete; only the catalog map is missing |
| Municipal tier assignment unverified for 11 territories | BEL, DEU, ESP, FRA, GBR, IRL, ISL, NOR, PRT, ROU, UKR | Marked `verify` and shipped as `review` |
| Budapest is drawn inside Pest county: the metadata counts 20 units, the file has 19 | HUN ADM1 | Upstream; awaiting a fix or another source |
| Sofia Province has 23 units against 22 municipalities: two are named Zlatitsa | BGR ADM2 (`BGR:ADM2:BG-23.zlatitsa-2`) | Upstream; awaiting a fix |
| The first level is the five NUTS 1 macro-regions, not the 20 regions | ITA ADM1 | Upstream tiering; regions and provinces are an open item above |
| Crimea: inside Russia's outline in Natural Earth, inside Ukraine's raions in geoBoundaries | RUS ADM0, UKR ADM0 and ADM2 | Documented in [Disputed boundaries](disputed-boundaries.md) |
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
