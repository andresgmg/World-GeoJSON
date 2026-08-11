# Review checklist

Work through this before opening a PR. Reviewers use the same list.

## Licensing

- [ ] Source appears on the [green list](sources.md#green-use-freely), or its
      terms have been checked and explicitly cleared
- [ ] `source.name`, `source.url`, `source.license` and `source.retrieved` are
      all filled in
- [ ] `license` is a valid [SPDX identifier](https://spdx.org/licenses/)
- [ ] Attribution requirements, if any, are satisfiable by the catalog page
- [ ] Data is **not** from GADM, a proprietary provider, or an unlicensed source

## Naming and layout

- [ ] Path is `data/{body}/{CODE}/{CODE}_{LEVEL}.geojson`
- [ ] `CODE` is the correct uppercase ISO 3166-1 alpha-3
- [ ] Extension is `.geojson`, and there is no duplicate `.json`
- [ ] Previews are in `preview/` named `{stem}.preview.geojson`
- [ ] No spaces, accents or non-ASCII characters in any path

## File contents

- [ ] Valid GeoJSON (`npx @mapbox/geojsonhint file.geojson`)
- [ ] `FeatureCollection` with a top-level `bbox`
- [ ] **No `crs` member** — forbidden by RFC 7946
- [ ] Coordinates are longitude-first, EPSG:4326 / CRS84
- [ ] No more than 6 decimal places of coordinate precision
- [ ] Minified, not pretty-printed
- [ ] Right-hand-rule winding
- [ ] Antimeridian crossings cut at 180°, if applicable
- [ ] No `null` geometries

## Properties

- [ ] `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` on every feature
- [ ] `shapeISO` is a **string**, zero-padded where the official code requires
- [ ] `shapeType` matches the file's level
- [ ] Source attributes preserved under `src_`
- [ ] Esri artifacts removed (`objectid`, `st_area_sh`, `st_length_`,
      `shape_leng`)
- [ ] Names carry correct diacritics and show no mojibake (`Ã`, `Â`, `â€`)
- [ ] Names are not abbreviated

## Nesting, where multiple levels are present

- [ ] Every ADM*n* feature nests inside exactly one ADM*n-1* feature
- [ ] `parentISO` is populated and resolves
- [ ] All levels come from the same vintage

## Manifest

- [ ] `manifest.json` exists in the country directory
- [ ] Hand-authored fields complete: `body`, `iso_a3`, `iso_a2`, `m49_region`,
      `name`, `crs`, `source`, `status`
- [ ] `datasets` regenerated with `build_manifest.py`, not hand-edited
- [ ] Feature count matches the official number of units, or `notes` explains
      the discrepancy
- [ ] Bounding box is in the correct hemisphere

## Previews

- [ ] A preview exists for every dataset
- [ ] Each preview is under 2 MB (target: under 800 KB)
- [ ] Preview feature count equals the source feature count
- [ ] Rendered preview looks like the country — no missing islands, no slivers

## Size

- [ ] Every `.geojson` is under 50 MB
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
