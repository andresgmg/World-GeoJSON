# Review checklist

Work through this before opening a PR. Reviewers use the same list.

Items marked **CI** are checked by `scripts/validate_data.py`, which runs on
every pull request that touches `data/`. Run it locally first:

```bash
python scripts/validate_data.py data/earth/XXX
```

Everything else needs a human.

## Licensing

- [ ] **CI** — `source.name`, `source.url`, `source.license` and
      `source.retrieved` are all filled in
- [ ] **CI** — `source.license` and every `datasets[].license` are on the
      permissive allow-list: `CC0-1.0`, `CC-BY-2.5`, `CC-BY-3.0`,
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
- [ ] **CI, warning only** — no more than 6 decimal places of coordinate
      precision
- [ ] Coordinates are longitude-first, EPSG:4326 / CRS84
- [ ] One feature per line, not pretty-printed
- [ ] Right-hand-rule winding
- [ ] Antimeridian crossings cut at 180°, if applicable
- [ ] `npx @mapbox/geojsonhint file.geojson` is clean

## Properties

- [ ] **CI** — `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` on every
      feature
- [ ] **CI** — `shapeISO` is a **string** on every feature
- [ ] `shapeISO` is zero-padded where the official code requires
- [ ] `shapeType` matches the file's level
- [ ] Source attributes preserved under `src_`
- [ ] Esri artifacts removed (`objectid`, `st_area_sh`, `st_length_`,
      `shape_leng`)
- [ ] Names carry correct diacritics and show no mojibake (`Ã`, `Â`, `â€`)
- [ ] Names are not abbreviated

## Nesting, where multiple levels are present

- [ ] Every ADM*n* feature nests inside exactly one ADM*n-1* feature
- [ ] Split parts carry `adm1ISO`, and `parentISO` resolves where present
      (today only Chile carries it; v1.0.0 adds it everywhere)
- [ ] All levels come from the same vintage

## Manifest

- [ ] **CI** — `manifest.json` exists in the country directory and is a JSON
      object
- [ ] **CI** — `body`, `name`, `crs`, `source` and `status` are present
- [ ] **CI** — every dataset entry has a feature count and a `license`
- [ ] **CI** — for split levels, `parts[].features` sum to the level's
      `features`
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

## Documentation

- [ ] If the country has quirks — missing levels, disputed areas, unusual
      codes — they are in `notes`
- [ ] If a new convention was needed, [Reference](../reference/index.md) is
      updated in the same PR

## Build

- [ ] `mkdocs build --strict` passes
- [ ] The new pages render correctly under `mkdocs serve`

--8<-- "abbreviations.md"
