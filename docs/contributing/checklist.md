# Review checklist

Work through this before opening a PR. Reviewers use the same list.

Items marked **CI** are checked automatically on every pull request that
touches `data/`, `schemas/` or `scripts/` — by `scripts/validate_data.py`
(run with `--checksums`), `finalize_geojson.py --check` and
`build_index.py --check`. Run them locally first:

```bash
python scripts/validate_data.py --checksums data/earth/XXX
python scripts/finalize_geojson.py --check data/earth/XXX
python scripts/build_index.py --check
```

Everything else needs a human.

## Licensing

- [ ] **CI** — `source.name`, `source.url`, `source.license` and
      `source.retrieved` are all filled in
- [ ] **CI** — `source.license` and every `datasets[].license` are on the
      permissive allow-list — the `license` enum of
      `schemas/manifest.schema.json`: `CC0-1.0`, `CC-BY-2.5`, `CC-BY-3.0`,
      `CC-BY-3.0-IGO`, `CC-BY-4.0`, `Etalab-2.0`, `OGL-Canada-2.0`,
      `public-domain`. Anything else — every ODbL and CC-BY-SA variant
      included — is rejected
- [ ] **CI** — if `source.license` is `mixed`, `source.licenses` lists the
      actual licences
- [ ] Source appears on the [green list](sources.md#green-use-freely), or its
      terms have been checked and explicitly cleared
- [ ] Attribution requirements, if any, are satisfiable by the catalog page
- [ ] Data is **not** from GADM, a proprietary provider, or an unlicensed source

## Naming and layout

- [ ] Path is `data/{body}/{CODE}/{CODE}_{LEVEL}.geojson`
- [ ] `CODE` is the correct uppercase ISO 3166-1 alpha-3
- [ ] Extension is `.geojson`, and there is no duplicate `.json`
- [ ] Split parts, if any, are in `{LEVEL}/{code}.geojson`
- [ ] Previews are in `preview/` named `{stem}.preview.geojson`
- [ ] No spaces, accents or non-ASCII characters in any path
- [ ] The country has an entry in `scripts/countries.json`

## File contents

- [ ] **CI** — valid JSON, and a `FeatureCollection`
- [ ] **CI** — top-level `bbox` present
- [ ] **CI** — **no `crs` member** — forbidden by RFC 7946
- [ ] **CI** — at least one feature, and no `null` geometries
- [ ] **CI** — under 50 MB
- [ ] **CI** — canonical layout: one feature per line, compact, coordinates
      at most 6 decimals — `finalize_geojson.py --check` passes
- [ ] **CI** — `bbox` equals the extent of the coordinates
- [ ] Coordinates are longitude-first, EPSG:4326 / CRS84
- [ ] Right-hand-rule winding
- [ ] Antimeridian crossings cut at 180°, if applicable
- [ ] `npx @mapbox/geojsonhint file.geojson` is clean

## Properties

- [ ] **CI** — every feature validates against
      `schemas/feature-properties.schema.json`: `shapeName`, `shapeISO`,
      `shapeGroup`, `shapeType` present, only the known optional keys, `src_*`
      for everything else
- [ ] **CI** — `shapeISO` is a **string** on every feature; `""` where the
      upstream has no code, never an opaque id; unique within the level
      where non-empty
- [ ] **CI** — every feature has an `id` of the form `{ISO3}:{LEVEL}:{key}`,
      unique within the file
- [ ] `shapeISO` is zero-padded where the official code requires
- [ ] `shapeType` matches the file's level
- [ ] Source attributes preserved under `src_`
- [ ] Esri artifacts removed (`objectid`, `st_area_sh`, `st_length_`,
      `shape_leng`)
- [ ] Names carry correct diacritics and show no mojibake (`Ã`, `Â`, `â€`)
- [ ] Names are not abbreviated

## Nesting, where multiple levels are present

- [ ] Every ADM*n* feature nests inside exactly one ADM*n-1* feature
- [ ] **CI** — every `parentID` resolves to a feature that exists in the
      country
- [ ] Every feature below ADM1 carries `adm1ISO` (or `"unassigned"`), and
      every feature with a published parent level carries `parentISO` and
      `parentID` — `finalize_geojson.py` writes them; an `unassigned` count
      is explained in `notes`
- [ ] All levels come from the same vintage

## Manifest

- [ ] **CI** — `manifest.json` exists in the country directory and
      validates against `schemas/manifest.schema.json`
- [ ] **CI** — `body`, `name`, `crs`, `source` and `status` are present
- [ ] **CI** — every dataset entry has a feature count and a `license`
- [ ] **CI** — feature counts match the files, and for split levels
      `parts[].features` sum to the level's `features`
- [ ] **CI** — `bytes` and `sha256` of every file match (`--checksums`)
- [ ] **CI** — `data/index.json` was regenerated (`build_index.py --check`)
- [ ] **CI** — `notes`, if present, is a single line
- [ ] `iso_a3`, `iso_a2` and `m49_region` match the registry
- [ ] `datasets` regenerated with `build_manifest.py`, not hand-edited
- [ ] Feature count matches the official number of units, or `notes` explains
      the discrepancy
- [ ] Bounding box is in the correct hemisphere

## Previews

- [ ] **CI** — every preview recorded in the manifest exists and is under
      2 MB. A dataset with no preview recorded is a warning, not an error —
      but the catalog map will be empty, so fix it
- [ ] Previews were generated **before** `build_manifest.py`, so the manifest
      records their path and size
- [ ] Preview feature count equals the source feature count
      (`make_previews.mjs` refuses to write one that does not)
- [ ] Rendered preview looks like the country — no missing islands, no slivers

## Size

- [ ] **CI** — every `.geojson` is under 50 MB
- [ ] No Git LFS

## Registries

- [ ] A new entry in `scripts/shapeiso_fixes.json` corrects a documented
      upstream error to the unit's real ISO 3166-2 code, and the PR says where
      the error is documented — the file is not for inventing codes
- [ ] A new entry in `scripts/id_overrides.json` is explained in the PR
- [ ] If an ADM1 code was corrected, the municipal parts were re-derived
      (`build_data.py --resplit XXX`, then `finalize_geojson.py`) and the
      part under the old code is gone

## Documentation

- [ ] If the country has quirks — missing levels, disputed areas, unusual
      codes — they are in `notes`
- [ ] If a new convention was needed, [Reference](../reference/index.md) is
      updated in the same PR

## Build

- [ ] `mkdocs build --strict` passes
- [ ] The new pages render correctly under `mkdocs serve`

--8<-- "abbreviations.md"
