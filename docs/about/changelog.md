# Changelog

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/) as adapted for
data in [Versioning & stability](versioning.md).

## Unreleased

### Added

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

The next release restructures the data tree. See
[Versioning & stability](versioning.md#the-upcoming-breaking-change).

- `regiones.geojson` → `data/earth/CHL/CHL_ADM1.geojson`
- `comunas.geojson` → `data/earth/CHL/CHL_ADM3.geojson`
- Properties renamed to the standard schema
- `cod_comuna` becomes `shapeISO`, a zero-padded **string**
- Esri artifacts removed
- Duplicate `.json` files removed

The four root-level files remain in place, deprecated, for one full major
version. They will not disappear silently.

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
