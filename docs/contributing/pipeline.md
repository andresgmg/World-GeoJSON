# Data pipeline

How source data becomes a file this repository will accept. One command,
`wgj`, with a subcommand per step, run in this order:

```
wgj fetch → wgj build → wgj previews → wgj manifest → wgj index → wgj validate
.cache/sources/  data/earth/XXX/  preview/       manifest datasets[]  data/index.json  CI checks
                 + finalize
```

The order is not negotiable: `wgj manifest` records a preview's path and
size only if the preview already exists, so previews come before the manifest;
`wgj index` embeds the manifests, so it comes after them. `wgj build` runs the
[finalize step](#the-finalize-step) itself, so a freshly built country
already carries its ids, hierarchy and canonical layout before the previews
are cut from it — and the previews carry those ids too.

Once the sources are fetched, `wgj all ARG` runs steps 2 to 6 — build,
previews, manifest, index, validate — for the countries you name, stopping at
the first failure. Every subcommand has `--help`, and `python -m wgj …` is
the same thing as `wgj …`.

## Requirements

- Python 3.11 or newer (CI tests 3.11 to 3.13 and validates the data on 3.12)
  and `pip install -r requirements-dev.txt`. That installs the pipeline
  itself as an editable package — the file contains
  `-e ./pipeline[pipeline]` — which puts the `wgj` command on your path,
  together with its runtime dependencies (`ijson`, with which `wgj manifest`
  streams files rather than parsing them whole, and `jsonschema`, with which
  `wgj validate` checks everything against the schemas) and the lint and test
  toolchain. `pip install -e ./pipeline[pipeline]` alone gives you the
  command without the toolchain.
- Node 18 or newer (CI uses 20) and `npm ci`, which installs the mapshaper
  version pinned in `package.json`. All geometry work is delegated to it:
  `wgj build` and `wgj previews` run it under the hood.

`just setup` does both if you have [`just`](https://github.com/casey/just);
the `justfile` also has `lint`, `fmt`, `test`, `validate`, `finalize`,
`previews`, `manifest`, `index`, `check-data` (everything CI checks about
committed data), `docs`, `serve` and `ci`.

## 0. Declare the country

`pipeline/src/wgj/tables/countries.json` is the registry every step reads. A
country that is not in it cannot be fetched or built. The file ships inside
the package, and the editable install means an edit is picked up at once.
Argentina's entry:

```json
"ARG": {
  "iso_a2": "AR",
  "m49_region": "South America",
  "name": { "en": "Argentina", "es": "Argentina" },
  "adm1_term": { "en": "Province", "es": "Provincia" },
  "municipal_level": "ADM2",
  "municipal_term": { "en": "Department", "es": "Departamento" },
  "source": "geoboundaries"
}
```

| Field | Meaning |
|---|---|
| `iso_a2`, `m49_region`, `name` | Identity, copied into the manifest |
| `source` | Which provider `wgj build` uses: `geoboundaries` or `ide-chile` |
| `municipal_level` | Which ADM level is the municipal tier (`ADM2`, `ADM3` or `ADM4`), or `null` when none is published. It cannot be inferred from the data: a Chilean comuna is ADM3, a Mexican municipio ADM2 |
| `adm1_term`, `adm2_term`, `municipal_term` | Local names for the levels, in both languages. They live here only, not in manifests |
| `verify` | `true` marks an entry whose level assignment or unit count has not been checked against an official source; its manifest ships with `status: "review"` |
| `note` | Copied into the manifest's `notes` on first build. One line |

## 1. Fetch the sources

```bash
wgj fetch --iso3 ARG          # one or more countries
wgj fetch --continent americas
wgj fetch --continent americas --dry-run
```

Downloads into `.cache/sources/`, which is git-ignored. Natural Earth's 10m
admin-0 file supplies every country outline; geoBoundaries' gbOpen release
supplies ADM1 and below, per country and level from
`https://www.geoboundaries.org/api/current/gbOpen/{ISO3}/{LEVEL}/`; Chile's
sub-national levels come from the IDE Chile / SUBDERE DPA 2023 package.

**The licence filter lives here, on purpose.** gbOpen is a container of
heterogeneous upstream licences, not a uniformly CC BY 4.0 dataset: a third of
its Americas entries are ODbL or CC-BY-SA. Those are refused before they reach
the working tree, let alone git history. `--dry-run` shows what would be
accepted and rejected without downloading anything.

## 2. Build the data

```bash
wgj build ARG
wgj build --continent americas --skip-existing
```

Reads the cache and writes `data/earth/ARG/`. For each level it:

- reprojects to WGS 84 and writes RFC 7946 GeoJSON — a top-level `bbox`, no
  `crs` member;
- renames source fields onto the [standard schema](../reference/schema.md)
  (`shapeName`, `shapeISO`, `shapeGroup`, `shapeType`) and keeps the rest
  under a `src_` prefix — geoBoundaries' opaque id becomes `src_shape_id`;
- simplifies to a **100 m ground tolerance** (Visvalingam), doubling it only
  when a file would exceed 18 MiB, and records what was applied in the
  manifest's `simplification` block;
- writes coordinates at 6 decimals, one feature per line;
- splits the municipal tier by ADM1 into `{LEVEL}/{code}.geojson` when an
  ADM1 exists. Features whose parent cannot be determined land in
  `{LEVEL}/unassigned.geojson`;
- writes the manifest's identity, `source` and `status`, and each dataset's
  `license` and `simplification`;
- **finalizes** every file it wrote — ids, hierarchy, `shapeISO` corrections,
  bbox, canonical layout. See the next section.

Nothing under `data/` is pretty-printed: mapshaper's output is rewritten by
the finalize step into one canonical layout. The 14-decimal, four-space-
indented format exists only in the legacy root files.

!!! danger "Zero-pad codes as strings"

    `shapeISO` must be a string. Official codes frequently have leading zeros
    that a JSON number cannot represent — Chile's Camiña is `01402`, not
    `1402`. Getting this wrong makes every downstream join fail silently, and
    `wgj validate` rejects the file.

### The finalize step

`wgj finalize` is the last thing `wgj build` does, and the step that turns
mapshaper's output into the [data contract](../reference/properties.md). It is
pure Python — no mapshaper, no network. It reads the country's
full-resolution files (combined level files and split parts) and rewrites
them so that every feature carries:

- `id` — `{ISO3}:{LEVEL}:{key}`, by the
  [key rule](../reference/properties.md#the-feature-id);
- `shapeISO` corrected from `pipeline/src/wgj/tables/shapeiso_fixes.json`,
  and cleared to `""` where the upstream shipped its opaque id instead of a
  code;
- `adm1ISO`, `parentISO` and `parentID` — the hierarchy, derived from the
  split parts and the level above;
- a `bbox` recomputed from the coordinates;

and writes the file in the canonical layout — one feature per line, compact
separators, at most 6 decimals — so running it twice is a no-op. It refuses
to run while two features would get the same `id`, and names them.

Two registries feed it. They live in the package's `tables/` directory next
to `countries.json`, and are the two files a contributor may need to edit by
hand:

| Registry | What goes in it |
|---|---|
| `pipeline/src/wgj/tables/shapeiso_fixes.json` | Corrections to upstream `shapeISO` values, keyed by ISO3, level and the feature's `src_shape_id` (`"*"` addresses every feature of a level; a value of `""` clears the code). Only documented upstream errors: the corrected value is the ISO 3166-2 code of the unit named in `shapeName`. Four entries today — `SU-SD` → `US-SD`, `MX-MEX` → `MX-CMX`, `EC-H` → `EC-X`, and Belize's ADM2 codes cleared |
| `pipeline/src/wgj/tables/id_overrides.json` | Manual `id` keys, addressed the same way, the value being the part after `{ISO3}:{LEVEL}:`. For when the automatic rule would collide or mislead. Empty today |

Do not use either to invent a code: a unit without an ISO 3166-2 code keeps
`shapeISO: ""` and gets a name-based `id`.

The step also runs on its own, over already-committed data:

```bash
wgj finalize data/earth/ARG           # one country
wgj finalize data/earth/*/            # everything
wgj finalize --check data/earth/*/    # CI: exit 1 if anything is stale
```

When an ADM1 code changes — a new entry in `shapeiso_fixes.json` — the
municipal parts must follow, because the part files are named after the ADM1
key. `--resplit` re-derives the parents and the parts from the committed
files without touching `.cache/sources` (the upstream may have moved on, and a
full rebuild would churn every checksum):

```bash
wgj build --resplit USA
wgj finalize data/earth/USA
```

then previews, manifest, index and validation as usual. That is how
`USA/ADM2/SU-SD.geojson` became `US-SD.geojson`.

## 3. Previews

```bash
wgj previews data/earth/ARG
wgj previews                                   # every country
npm run previews                               # the same, for Node habits
```

Writes `data/earth/ARG/preview/ARG_{LEVEL}.preview.geojson`, merging split
parts first. The command is Python but the simplification is mapshaper's, run
through Node — hence `npm ci`. Each preview feature keeps the `id` of its
full-resolution feature, which is why this step comes after finalize. Details
and the size budget are in [Simplification & previews](previews.md).

## 4. Manifest

```bash
wgj manifest data/earth/ARG
```

Scans the directory and writes the `datasets` array — path, bytes, SHA-256,
feature count, bbox, geometry types, property list (the hierarchy fields
included), preview and its size, and for split levels the `parts`. Everything
outside `datasets` is preserved verbatim, and the per-dataset keys it does not
compute itself (`license`, `src_provider`, `simplification`) are carried
forward from the previous run. See [Manifest format](../reference/manifest.md).

## 5. Index

```bash
wgj index
wgj index --check      # CI: exit 1 if the committed file is stale
```

Rebuilds `data/index.json` from all the manifests. Every manifest change must
be followed by this, because the index embeds them verbatim; CI checks that
the committed index is current. See
[Global index & schemas](../reference/index-json.md).

## 6. Validate

```bash
wgj validate                 # everything
wgj validate data/earth/ARG  # one country
wgj validate --checksums     # also re-hash every file, as CI does
```

The same checks CI runs on every pull request that touches `data/`,
`schemas/` or `pipeline/`. Every manifest, `data/index.json`, the country
registry and every feature of every full-resolution file is validated against
the [JSON Schemas](../reference/index-json.md#schemas) — which is where the
licence allow-list, the required properties, `shapeISO` as a string and the
`id` pattern now live — plus what a schema cannot say: feature ids unique per
file, every `parentID` resolving to a feature in the country, the in-file
`bbox` equal to the coordinates, manifest feature counts equal to the files,
`parts` summing to the level, previews present and under 2 MB, files under
50 MB, and with `--checksums` every byte count and SHA-256 matching the
manifest. Coordinates beyond 6 decimals are a warning.

CI runs three more checks beside it — `wgj finalize --check data/earth/*/`,
`wgj index --check`, and `wgj manifest data/earth/*/` followed by
`git diff --quiet` to make sure the committed manifests match a fresh
regeneration. `just check-data` runs all four. The
[Review checklist](checklist.md) says which items are automated and which
need eyes.

Then confirm by eye what no check can:

- [ ] feature count matches the official number of units
- [ ] `shapeName` values carry correct diacritics and are not mojibake

Mojibake is the common one: a shapefile whose `.cpg` is missing or wrong
decodes `Ñuble` as `Ã‘uble`. If you see `Ã` anywhere, the encoding was
misread — go back to the source and force UTF-8.

## Building by hand

If the source is a provider `wgj build` does not know, the files can be
produced with ogr2ogr or mapshaper and dropped into `data/earth/XXX/`, then
finalized — `wgj finalize data/earth/XXX` gives them their ids, hierarchy and
canonical layout — and steps 3 to 6 run as usual.

=== "ogr2ogr"

    ```bash
    ogr2ogr -f GeoJSON \
      -t_srs EPSG:4326 \
      -lco RFC7946=YES \
      -lco COORDINATE_PRECISION=6 \
      -lco WRITE_BBOX=YES \
      output.geojson input.shp
    ```

    `-lco RFC7946=YES` matters: without it GDAL writes the older 2008 draft
    dialect, which permits a `crs` member and uses different winding rules.

=== "mapshaper"

    ```bash
    npx mapshaper input.shp \
      -proj wgs84 \
      -rename-fields shapeName=NOMBRE,src_codigo=CODIGO \
      -each 'shapeGroup="XXX", shapeType="ADM1", shapeISO=String(src_codigo).padStart(2,"0")' \
      -filter-fields shapeName,shapeISO,shapeGroup,shapeType,src_codigo \
      -o precision=0.000001 bbox format=geojson data/earth/XXX/XXX_ADM1.geojson
    ```

Verify rather than assume the projection — a shapefile with a missing or
wrong `.prj` is passed through unchanged and lands your country in the Gulf of
Guinea. `npx mapshaper -i output.geojson -info` should show coordinates in the
−180…180 / −90…90 range and in the right hemisphere. Check any country with
territory near the antimeridian or the poles: RFC 7946 requires right-hand-rule
winding and geometries cut at 180°.

Two things `wgj build` would have done for you now have to be done by hand:

- **The manifest's per-dataset `license`.** `wgj manifest` writes
  `datasets[]` but does not know where the files came from, and
  `wgj validate` rejects any dataset without a `license` on the allow-list.
  Add `license` (and `src_provider`) to each entry after the first
  `wgj manifest` run; later runs carry them forward.
- **The identity block** — `body`, `iso_a3`, `iso_a2`, `m49_region`, `name`,
  `crs`, `source`, `status` — which [Add a country](add-a-country.md) shows.

Size is the last check: `wgj validate` fails any file over 50 MB, and GitHub
refuses pushes above 100 MB. Before reaching for Git LFS —
[don't](../about/versioning.md#why-not-git-lfs) — confirm the file is
simplified and trimmed to 6 decimals, and split it by ADM1 if it is still too
big.

## Where the code lives

The pipeline is the Python package `wgj` under `pipeline/` —
`pipeline/pyproject.toml` and `pipeline/src/wgj/` — one module per concern:

| Module | Role |
|---|---|
| `wgj.cli` | The `wgj` command: one subcommand per step, plus `all` |
| `wgj.paths` | Where things live; `WGJ_DATA` points the package at another data tree |
| `wgj.registry` | Loads the tables in `pipeline/src/wgj/tables/` — `countries.json`, `shapeiso_fixes.json`, `id_overrides.json`, `iso3166_2.json` |
| `wgj.licensing` | Upstream licence text mapped onto SPDX ids, and the allow-list |
| `wgj.levels`, `wgj.text` | The ADM levels and the file names built on them; small text helpers |
| `wgj.geojson_io` | Streaming scan, SHA-256, the canonical writer |
| `wgj.mapshaper`, `wgj.simplify` | The mapshaper subprocess; the tolerance rule and its size budget |
| `wgj.sources.natural_earth`, `wgj.sources.geoboundaries`, `wgj.sources.ide_chile` | One module per provider |
| `wgj.fetch`, `wgj.build`, `wgj.finalize`, `wgj.previews`, `wgj.manifest`, `wgj.index`, `wgj.validate` | The six steps above, in order |
| `wgj.schema` | The JSON Schemas under `schemas/`, loaded once with their `$ref`s resolved locally |
| `wgj.catalog` | The MkDocs hook that generates the catalog pages; `pipeline/mkdocs_hook.py` re-exports it, so building the docs needs no install |

The tests are in `pipeline/tests/` and run with `pytest` from the repository
root. They need no data checkout: `fixtures/data/` holds three small
territories — Aruba, Barbados and a reduced Dominican Republic — plus their
`index.json`, and the suite points the package at it with `WGJ_DATA`. Set
`WGJ_DATA=<dir>` yourself to run any `wgj` command against another data tree.

`scripts/*.py` still exist as ten-line shims that call into the package, so
`python scripts/validate_data.py` and its siblings keep working for one
release. They retire in Phase 4 of the [Roadmap](../about/roadmap.md); write
`wgj` from now on.

--8<-- "abbreviations.md"
