# Manifest format

Every dataset directory contains a `manifest.json`. It is the **only** input to
this documentation site: every catalog page is generated from it. There are 55
of them today, one per territory under `data/earth/`, and all 55 are embedded
verbatim in the [global index](index-json.md), `data/index.json`.

## Why it exists

The documentation build must never open a GeoJSON file.

Parsing tens of megabytes of geometry on every build would make `mkdocs serve`
unusable for editing, slow CI substantially, and force CI to check out data it
otherwise does not need. Instead, a separate script scans the data when the
*data* changes and writes a few kilobytes of metadata beside it. The docs build
reads only that.

This is what makes the catalog scale to hundreds of countries at constant build
cost, and what lets CI check out the repository *without any `.geojson` files
at all*.

## Example

`data/earth/CHL/manifest.json`, abridged to its first two datasets:

```json
{
  "schema_version": 1,
  "body": "earth",
  "iso_a3": "CHL",
  "iso_a2": "CL",
  "m49_region": "South America",
  "name": { "en": "Chile", "es": "Chile" },
  "crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 },
  "status": "ok",
  "source": {
    "name": "IDE Chile / SUBDERE — División Política Administrativa 2023",
    "url": "https://www.geoportal.cl/",
    "license": "mixed",
    "retrieved": "2026-08-11",
    "licenses": ["CC-BY-4.0", "public-domain"]
  },
  "datasets": [
    {
      "level": "ADM0",
      "path": "data/earth/CHL/CHL_ADM0.geojson",
      "bytes": 407948,
      "sha256": "9abf1248d9c64bb3e50a63a24723595093aa6a58b75cf3935b3465b090205889",
      "features": 1,
      "bbox": [-109.453725, -55.918504, -66.420806, -17.506588],
      "geometry_types": { "MultiPolygon": 1 },
      "properties": ["shapeGroup", "shapeISO", "shapeName", "shapeType"],
      "preview": "data/earth/CHL/preview/CHL_ADM0.preview.geojson",
      "preview_bytes": 18800,
      "simplification": { "method": "visvalingam", "tolerance_m": 100 },
      "license": "public-domain",
      "src_provider": "Natural Earth"
    },
    {
      "level": "ADM1",
      "path": "data/earth/CHL/CHL_ADM1.geojson",
      "bytes": 4815275,
      "sha256": "6679a263585d6ef01bf9778d629f6daaa9a765011109b7ad95c27863a0a7b5c5",
      "features": 16,
      "bbox": [-109.449861, -56.525107, -66.416176, -17.498399],
      "geometry_types": { "MultiPolygon": 10, "Polygon": 6 },
      "properties": ["parentID", "parentISO", "shapeGroup", "shapeISO", "shapeName",
                     "shapeType", "src_cut_reg", "src_superficie_km2"],
      "preview": "data/earth/CHL/preview/CHL_ADM1.preview.geojson",
      "preview_bytes": 226849,
      "simplification": { "method": "visvalingam", "tolerance_m": 100 },
      "license": "CC-BY-4.0"
    }
  ]
}
```

The licence is `"mixed"` because the outline is Natural Earth (public domain)
while the three subdivision levels are IDE Chile (CC BY 4.0); `licenses` lists
the distinct values. Chile's manifest has no `notes`.

## Fields

### Top level

| Field | Type | Meaning |
|---|---|---|
| `schema_version` | integer | Format version of this manifest. `1` today; bumped only on a breaking format change |
| `body` | string | `earth` (the Moon and Mars will use their own) |
| `iso_a3`, `iso_a2` | string | ISO 3166-1 codes |
| `m49_region` | string | UN M49 sub-region, used to group the catalog |
| `name` | object | `{ "en": …, "es": … }` display names |
| `crs` | object | Always `{ "authority": "OGC", "code": "CRS84", "epsg": 4326 }` for Earth — the files themselves cannot declare it. See [CRS](crs.md) |
| `status` | string | `ok`, or `review` when the municipal-tier assignment in `scripts/countries.json` is still marked `verify` |
| `source` | object | `name`, `url`, `license`, `retrieved` (ISO date). When the datasets carry different licences, `license` is `"mixed"` and `licenses` lists the distinct values, sorted |
| `notes` | string | Optional, one line. Known gaps, upstream quirks, disputes |
| `datasets` | array | One entry per level, sorted by level |

### Per dataset (`datasets[]`)

| Field | Meaning |
|---|---|
| `level` | `ADM0`–`ADM4` |
| `path` | The whole-level file, relative to the repository root. Absent when the combined file was too large to publish (Brazil's ADM2 today) |
| `bytes`, `sha256` | Size and hash of `path`; for a split level without one, `bytes` is the sum of the parts |
| `features` | Feature count of the **whole level**, so the catalog can always report a total |
| `bbox` | `[west, south, east, north]`, naive min/max over all coordinates — see the antimeridian note below |
| `geometry_types` | Count per GeoJSON geometry type, e.g. `{ "MultiPolygon": 10, "Polygon": 6 }` |
| `properties` | Every property key present on any feature, **sorted** — the four standard keys, the hierarchy keys (`adm1ISO`, `parentISO`, `parentID`) where the level carries them, and the `src_*` fields |
| `preview`, `preview_bytes` | The simplified companion file in `preview/` and its size |
| `simplification` | What was applied: `{ "method": "visvalingam", "tolerance_m": 100 }` |
| `license` | SPDX-style identifier for **this dataset** — licences differ between levels of one country |
| `src_provider` | Who produced the geometry upstream: `Natural Earth`, `Instituto Nacional de Estadística y Geografía (INEGI)`, … Absent on Chile's subdivision levels, where `source` already says |
| `src_year` | Optional. The year the boundaries represent, as reported upstream (`"2018"`) |
| `split_by` | `"ADM1"` when the level is split into parts. Optional |
| `unassigned` | Optional count of units that could not be matched to an ADM1 parent and were kept in `unassigned.geojson` |
| `parts` | Optional array, present on split levels — see below |

### Per part (`datasets[].parts[]`)

Each part has `code` (the ADM1 code the file is named after, or `unassigned`),
`path`, `bytes`, `sha256`, `features`, `bbox`, `geometry_types` and
`properties` — the same measurements as a dataset, for one file.

## Split levels

A split level carries a `parts` array alongside the optional combined file.
Chile's ADM3, abridged:

```json
{
  "level": "ADM3",
  "path": "data/earth/CHL/CHL_ADM3.geojson",
  "bytes": 6982386,
  "features": 345,
  "properties": ["adm1ISO", "parentID", "parentISO", "shapeGroup", "shapeISO",
                 "shapeName", "shapeType", "src_cut_com", "src_cut_prov",
                 "src_cut_reg", "src_provincia", "src_region"],
  "preview": "data/earth/CHL/preview/CHL_ADM3.preview.geojson",
  "split_by": "ADM1",
  "license": "CC-BY-4.0",
  "parts": [
    {
      "code": "CL-AI",
      "path": "data/earth/CHL/ADM3/CL-AI.geojson",
      "bytes": 1281666,
      "sha256": "604104c46aa2863ed43158ff48be1450768e794f86276d840dd856c1e746c1f8",
      "features": 10,
      "bbox": [-75.64927, -49.158776, -71.091675, -43.637991],
      "geometry_types": { "MultiPolygon": 4, "Polygon": 6 },
      "properties": ["adm1ISO", "parentID", "parentISO", "shapeGroup", "shapeISO",
                     "shapeName", "shapeType", "src_cut_com", "src_cut_prov",
                     "src_cut_reg", "src_provincia", "src_region"]
    }
  ]
}
```

- `features` on the entry is the **whole level**, so the catalog can always
  report a total whether or not a combined file exists.
- `path` is the optional whole-country file, present only when it fits under
  the 18 MiB budget. Brazil's ADM2 has 28 parts and no `path`; its absence is
  normal and the catalog says so.
- `code` is the ADM1 unit's key: its `shapeISO` after the corrections in
  `scripts/shapeiso_fixes.json`, which is also the `adm1ISO` value on every
  feature in the part and the key of the ADM1's own `id`. Upstream typos are
  corrected there rather than passed through — South Dakota's 66 counties are
  in the part coded `US-SD` although geoBoundaries codes the state `SU-SD`.
  A part coded `unassigned` holds the units no parent could be found for; the
  USA ADM2 entry also has `"unassigned": 1`.

CI checks that the parts sum exactly to the level's feature count — that is how
a split that lost or duplicated a municipality gets caught.

!!! warning "`bbox` is a naive min/max — in the manifest and in the file"

    The manifest's `bbox` is the plain minimum and maximum of every
    coordinate, and so is the file's own top-level `bbox`: the finalize step
    recomputes it from the coordinates, CI checks that the two agree, and
    neither uses the west-greater-than-east form RFC 7946 §5.2 allows. For a
    territory that crosses the antimeridian that is nearly the whole globe —
    the USA entries and `USA_ADM0.geojson` alike read
    `[-179.14…, 18.90…, 179.78…, 71.41…]`. Do not use the `bbox` to decide
    whether such a country touches your area of interest near 180°. See
    [CRS → The antimeridian](crs.md#the-antimeridian).

## Simplification

Every dataset records what was done to it:

```json
"simplification": { "method": "visvalingam", "tolerance_m": 100 }
```

`tolerance_m` is a **ground distance**, not a percentage. That is deliberate: a
percentage keeps a fixed share of each file's vertices, so the resulting
resolution depends on how densely the source happened to be digitised and two
neighbouring countries end up at different fidelities. A distance gives the
whole repository one consistent real-world resolution.

The standard tolerance is **100 m**. Chile's 16 regions — one of the world's
most complex coastlines — measure 49.7 MB at 10 m, 10.0 MB at 50 m, 4.6 MB at
100 m and 1.6 MB at 250 m. A dataset that would still exceed the 18 MiB budget
at the standard tolerance gets the tolerance doubled until it fits, and the
value recorded here is always the value actually applied.

## Who writes what

Three things touch a manifest, and the split matters because it is what makes
regeneration safe.

| Field | Written by | Notes |
|---|---|---|
| `schema_version` | either script, if absent | Bumped by hand only on a breaking format change |
| `body`, `iso_a3`, `iso_a2`, `m49_region`, `name`, `crs` | **`build_data.py`** | Identity, taken from `scripts/countries.json`. **Overwritten** on every build — edit `countries.json`, not the manifest |
| `source.name`, `source.url`, `source.retrieved` | `build_data.py`, if absent | Hand edits survive; `retrieved` is only set when missing |
| `source.license`, `source.licenses` | both scripts | Rolled up from `datasets[].license` |
| `status` | `build_data.py`, if absent | Hand edits survive. `review` when `countries.json` marks the entry `verify` |
| `notes` | `build_data.py`, if absent | Seeded from the `note` in `countries.json`; hand edits survive |
| `datasets[].simplification`, `license`, `src_provider`, `src_year`, `unassigned` | **`build_data.py`** | Provenance of the build; `build_manifest.py` carries them over unchanged |
| everything else in `datasets[]` | **`build_manifest.py`** | Measured from the files: `path`, `bytes`, `sha256`, `features`, `bbox`, `geometry_types`, `properties`, `preview`, `preview_bytes`, `split_by`, `parts` |

`scripts/build_manifest.py` replaces the `datasets` array wholesale and leaves
every other key untouched. Curated metadata — `status`, `notes`,
`source.retrieved` — therefore survives regeneration, which is what makes it
safe to re-run the scanner routinely. Local terms (`adm1_term`,
`municipal_term`) are **not** in the manifest; they live only in
`scripts/countries.json`.

## Regenerating

Previews first, then the manifest — `build_manifest.py` only records `preview`
and `preview_bytes` for a preview that already exists — then the index, which
embeds the manifest:

```bash
node scripts/make_previews.mjs data/earth/CHL
python scripts/build_manifest.py data/earth/CHL
python scripts/build_index.py
```

The scanner streams each file with `ijson` in constant memory, so even the
largest file in the repository (Canada's ADM1, 14.9 MB) costs a few seconds and
a few tens of megabytes of RAM rather than a gigabyte-plus of parsed Python
objects.

Do not hand-edit the measured fields; CI regenerates the manifest and the
index and fails the build if a committed version disagrees.

## Checksums and line endings

`sha256` is over the raw bytes of the file as stored with **LF** line endings.

This matters more than it sounds. Git normalises line endings on checkout, so
the same file checked out on Windows with CRLF is one byte per line larger —
and, since every feature is on its own line, hashes to something completely
different.

The repository's `.gitattributes` pins `*.geojson` to `eol=lf` so that hashes
computed on Windows, on Linux CI and by `raw.githubusercontent.com` all agree.
If you get a mismatch, check your Git line-ending configuration before
suspecting the data.

Catalog pages show the first 16 hex characters of each hash; the manifest has
the full value.

## Validation

Every manifest is validated against
[`schemas/manifest.schema.json`](index-json.md#schemas) — the same JSON Schema
a consumer can validate against — and its `license` enum is the
[licence allow-list](../contributing/sources.md), so there is one definition of
what a manifest may contain. `scripts/validate_data.py` runs in CI for every
change to `data/`, `schemas/` or `scripts/` and checks:

- every manifest, `data/index.json` and `scripts/countries.json` validate
  against their schema, and every feature of every full-resolution file
  against the feature schemas;
- feature ids are unique per file and every `parentID` points at an id that
  exists in the country;
- every file's in-file `bbox` equals the extent of its coordinates;
- every `.geojson` is under 50 MB, and every preview exists and is under 2 MB;
- manifest feature counts equal the files, and the parts of a split level sum
  exactly to its `features`;
- with `--checksums`, as CI runs it, every file's `bytes` and `sha256` match
  the manifest.

Two more checks run beside it: `finalize_geojson.py --check` (every file is
in canonical form, with its ids and hierarchy) and `build_index.py --check`,
and the committed manifests must match a fresh regeneration.

## The global index and the release assets

The manifests are embedded, verbatim, in **`data/index.json`** — one 340 KB
file for the whole corpus, so a client discovers every territory, level and
file with `bytes`, `sha256`, `bbox` and licence in a single request instead of
55. It is documented on [Global index & schemas](index-json.md), alongside the
five JSON Schemas.

Tagged releases distribute the same files a second way: one zip per territory
— the country folder with its files, manifest and previews — attached to the
GitHub Release, plus `index.json` and a `SHA256SUMS`. See
[Download & CDN → Release assets](../get-started/download.md#release-assets).

--8<-- "abbreviations.md"
