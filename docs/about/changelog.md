# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/) as adapted for
data in [Versioning & stability](versioning.md).

## Unreleased

### Added — the Americas

- **55 territories, 95 datasets, 16,195 features.** Country outlines from
  Natural Earth 10m (public domain); first-level and municipal divisions from
  geoBoundaries `gbOpen`, permissive licences only; Chile from IDE Chile.
- Municipal levels are split by first-level parent. The parent is derived by
  largest-overlap spatial join, because geoBoundaries carries no parent
  reference and frequently ships an empty `shapeISO`.
- Each dataset records its own licence, upstream provider and vintage. A
  country-level licence would be a false claim: Brazil's outline is public
  domain, its states CC BY 2.5 and its municipalities CC BY 3.0 IGO.
- mapshaper is pinned in `package.json` and installed locally rather than
  resolved through `npx` on every call.

**Not included, and why.** Fifteen countries have no first-level divisions
because their geoBoundaries ADM1 is ODbL or CC-BY-SA. Bonaire/Sint Eustatius
and Saba and Bouvet Island ship nothing at all. Jamaica's and Saint Lucia's
ADM2 were left out as apparently mis-tiered — 827 units against 14 parishes,
547 against 10 quarters. See the [Roadmap](roadmap.md).

**Upstream quirks worth knowing.** geoBoundaries' `admUnitCount` metadata
disagrees with the files it serves in several cases (Suriname reports 62 ADM2
units and ships 58); the counts here are what the files actually contain.
Argentina's ADM1 omits the Autonomous City of Buenos Aires, so its 8 comunas
overlap no province and are kept in an `unassigned` part rather than dropped.
Ecuador and Peru each ship an ADM1 whose `shapeISO` contains an asterisk.

### Added — data pipeline and Chile

- **Chile at `data/earth/CHL/`**, from IDE Chile's *División Política
  Administrativa* 2023 under CC BY: 16 regions, 56 provinces and 345 communes.
  The provincial tier had no openly licensed source before now.
- The municipal level is **split by region** into 16 files so no single file is
  unwieldy, plus a whole-country file where it fits under the CDN ceiling.
- Ingestion pipeline: `fetch_sources.py`, `build_data.py`,
  `build_manifest.py`, `make_previews.mjs`, and a curated
  `scripts/countries.json` recording which ADM level is each country's
  municipal tier.
- All geometry simplified to a **100 m ground tolerance**, recorded per dataset
  in the manifest. A distance rather than a percentage, so the whole repository
  shares one real-world resolution.
- `validate-data.yml` — checks manifests against a clean regeneration, verifies
  split parts sum to the level total, enforces size budgets, and rejects any
  `source.license` outside the permissive allow-list.
- Interactive preview maps, served from the docs site itself so they work under
  `mkdocs serve` and during PR review rather than depending on CDN propagation.

### Changed

- **Chile's source moved from BCN to IDE Chile DPA 2023.** geoBoundaries was
  evaluated and rejected for Chile: its ADM2 is OpenStreetMap under ODbL, and
  its communes are a 2020 vintage.
- **geoBoundaries is no longer described as a CC BY 4.0 source.** `gbOpen` is a
  container of per-file licences and 33% of its Americas entries are copyleft.
  `contributing/sources.md` was wrong and has been corrected.
- Natural Earth is now the designated source for country outlines.

### Deprecated

- `regiones.geojson`, `comunas.geojson` and their `.json` duplicates remain at
  the repository root, unchanged, for one full major version. They are not
  byte-equivalent to their replacements — different source, schema and
  resolution.

### Added — documentation site

- Documentation site built with MkDocs and Material for MkDocs, deployed to
  GitHub Pages.
- Written conventions for repository layout, administrative levels, property
  schema, coordinate reference systems and planetary bodies.
- Approved-source list and licensing policy, including the explicit exclusion
  of GADM and the share-alike problem with OpenStreetMap.
- Disputed-boundaries policy.
- Code of conduct.
- Catalog generator (`scripts/gen_catalog.py`) producing dataset pages from
  `manifest.json` sidecars.
- CI workflow building the site with `--strict` on pull requests and deploying
  to GitHub Pages on `main`.

### Fixed

- `.gitattributes` now pins `*.geojson` to LF line endings. Previously
  `* text=auto` caused CRLF conversion on Windows checkout, making the working
  file 1.8 MB larger than the stored blob and producing checksums that could
  not match Linux CI or `raw.githubusercontent.com`.

### Planned — breaking

The legacy root files are removed in the next major release. See
[Versioning & stability](versioning.md#the-legacy-root-files).

---

## [0.2.0] — 2023

### Added

- `comunas.geojson` — 343 Chilean communes.
- `comunas.json` — byte-identical duplicate.

## [0.1.0] — 2023

### Added

- `regiones.geojson` — 16 Chilean regions.
- `regiones.json` — byte-identical duplicate.
- MIT licence.

Source for both: Biblioteca del Congreso Nacional de Chile (BCN) / IDE Chile.

--8<-- "abbreviations.md"
