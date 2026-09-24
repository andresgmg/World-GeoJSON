# Data pipeline

How source data becomes a file this repository will accept. Six scripts, run
in this order:

```
fetch_sources.py → build_data.py → make_previews.mjs → build_manifest.py → build_index.py → validate_data.py
.cache/sources/    data/earth/XXX/   preview/            manifest datasets[]   data/index.json    CI checks
                   + finalize
```

The order is not negotiable: `build_manifest.py` records a preview's path and
size only if the preview already exists, so previews come before the manifest;
`build_index.py` embeds the manifests, so it comes after them. `build_data.py`
runs the [finalize step](#the-finalize-step) itself, so a freshly built
country already carries its ids, hierarchy and canonical layout before the
previews are cut from it.

## Requirements

- Python 3.11 or newer (CI uses 3.12) and `pip install -r
  requirements-dev.txt` — `ijson`, with which `build_manifest.py` streams
  files rather than parsing them whole, and `jsonschema`, with which
  `validate_data.py` checks everything against the schemas.
- Node 18 or newer (CI will use 20) and `npm install`, which pins
  mapshaper 0.6.109. All geometry work is delegated to it.

## 0. Declare the country

`scripts/countries.json` is the registry every script reads. A country that is
not in it cannot be fetched or built. Argentina's entry:

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
| `source` | Which provider `build_data.py` uses: `geoboundaries` or `ide-chile` |
| `municipal_level` | Which ADM level is the municipal tier (`ADM2`, `ADM3` or `ADM4`), or `null` when none is published. It cannot be inferred from the data: a Chilean comuna is ADM3, a Mexican municipio ADM2 |
| `adm1_term`, `adm2_term`, `municipal_term` | Local names for the levels, in both languages. They live here only, not in manifests |
| `verify` | `true` marks an entry whose level assignment or unit count has not been checked against an official source; its manifest ships with `status: "review"` |
| `note` | Copied into the manifest's `notes` on first build. One line |

## 1. Fetch the sources

```bash
python scripts/fetch_sources.py --iso3 ARG          # one or more countries
python scripts/fetch_sources.py --continent americas
python scripts/fetch_sources.py --continent americas --dry-run
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
python scripts/build_data.py ARG
python scripts/build_data.py --continent americas --skip-existing
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
    `validate_data.py` rejects the file.

### The finalize step

`scripts/finalize_geojson.py` is the last thing `build_data.py` does, and the
step that turns mapshaper's output into the
[data contract](../reference/properties.md). It is pure Python — no mapshaper,
no network. It reads the country's full-resolution files (combined level files
and split parts) and rewrites them so that every feature carries:

- `id` — `{ISO3}:{LEVEL}:{key}`, by the
  [key rule](../reference/properties.md#the-feature-id);
- `shapeISO` corrected from `scripts/shapeiso_fixes.json`, and cleared to
  `""` where the upstream shipped its opaque id instead of a code;
- `adm1ISO`, `parentISO` and `parentID` — the hierarchy, derived from the
  split parts and the level above;
- a `bbox` recomputed from the coordinates;

and writes the file in the canonical layout — one feature per line, compact
separators, at most 6 decimals — so running it twice is a no-op. It refuses
to run while two features would get the same `id`, and names them.

Two registries feed it. They are the two files a contributor may need to edit
by hand:

| Registry | What goes in it |
|---|---|
| `scripts/shapeiso_fixes.json` | Corrections to upstream `shapeISO` values, keyed by ISO3, level and the feature's `src_shape_id` (`"*"` addresses every feature of a level; a value of `""` clears the code). Only documented upstream errors: the corrected value is the ISO 3166-2 code of the unit named in `shapeName`. Four entries today — `SU-SD` → `US-SD`, `MX-MEX` → `MX-CMX`, `EC-H` → `EC-X`, and Belize's ADM2 codes cleared |
| `scripts/id_overrides.json` | Manual `id` keys, addressed the same way, the value being the part after `{ISO3}:{LEVEL}:`. For when the automatic rule would collide or mislead. Empty today |

Do not use either to invent a code: a unit without an ISO 3166-2 code keeps
`shapeISO: ""` and gets a name-based `id`.

The step also runs on its own, over already-committed data:

```bash
python scripts/finalize_geojson.py data/earth/ARG           # one country
python scripts/finalize_geojson.py data/earth/*/            # everything
python scripts/finalize_geojson.py --check data/earth/*/    # CI: exit 1 if anything is stale
```

When an ADM1 code changes — a new entry in `shapeiso_fixes.json` — the
municipal parts must follow, because the part files are named after the ADM1
key. `--resplit` re-derives the parents and the parts from the committed
files without touching `.cache/sources` (the upstream may have moved on, and a
full rebuild would churn every checksum):

```bash
python scripts/build_data.py --resplit USA
python scripts/finalize_geojson.py data/earth/USA
```

then previews, manifest, index and validation as usual. That is how
`USA/ADM2/SU-SD.geojson` became `US-SD.geojson`.

## 3. Previews

```bash
node scripts/make_previews.mjs data/earth/ARG
npm run previews                                   # every country
```

Writes `data/earth/ARG/preview/ARG_{LEVEL}.preview.geojson`, merging split
parts first. Details and the size budget are in
[Simplification & previews](previews.md).

## 4. Manifest

```bash
python scripts/build_manifest.py data/earth/ARG
```

Scans the directory and writes the `datasets` array — path, bytes, SHA-256,
feature count, bbox, geometry types, property list (the hierarchy fields
included), preview and its size, and for split levels the `parts`. Everything
outside `datasets` is preserved verbatim, and the per-dataset keys it does not
compute itself (`license`, `src_provider`, `simplification`) are carried
forward from the previous run. See [Manifest format](../reference/manifest.md).

## 5. Index

```bash
python scripts/build_index.py
python scripts/build_index.py --check      # CI: exit 1 if the committed file is stale
```

Rebuilds `data/index.json` from all the manifests. Every manifest change must
be followed by this, because the index embeds them verbatim; CI checks that
the committed index is current. See
[Global index & schemas](../reference/index-json.md).

## 6. Validate

```bash
python scripts/validate_data.py                 # everything
python scripts/validate_data.py data/earth/ARG  # one country
python scripts/validate_data.py --checksums     # also re-hash every file, as CI does
```

The same checks CI runs on every pull request that touches `data/`,
`schemas/` or `scripts/`. Every manifest, `data/index.json`,
`scripts/countries.json` and every feature of every full-resolution file is
validated against the [JSON Schemas](../reference/index-json.md#schemas) —
which is where the licence allow-list, the required properties, `shapeISO` as
a string and the `id` pattern now live — plus what a schema cannot say: feature
ids unique per file, every `parentID` resolving to a feature in the country,
the in-file `bbox` equal to the coordinates, manifest feature counts equal to
the files, `parts` summing to the level, previews present and under 2 MB,
files under 50 MB, and with `--checksums` every byte count and SHA-256
matching the manifest. Coordinates beyond 6 decimals are a warning.

CI runs two more checks beside it — `finalize_geojson.py --check
data/earth/*/` and `build_index.py --check` — and regenerates the manifests to
make sure the committed ones match. The [Review checklist](checklist.md) says
which items are automated and which need eyes.

Then confirm by eye what no script can:

- [ ] feature count matches the official number of units
- [ ] `shapeName` values carry correct diacritics and are not mojibake

Mojibake is the common one: a shapefile whose `.cpg` is missing or wrong
decodes `Ñuble` as `Ã‘uble`. If you see `Ã` anywhere, the encoding was
misread — go back to the source and force UTF-8.

## Building by hand

If the source is a provider `build_data.py` does not know, the files can be
produced with ogr2ogr or mapshaper and dropped into `data/earth/XXX/`, then
finalized — `python scripts/finalize_geojson.py data/earth/XXX` gives them
their ids, hierarchy and canonical layout — and steps 3 to 6 run as usual.

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

Two things `build_data.py` would have done for you now have to be done by
hand:

- **The manifest's per-dataset `license`.** `build_manifest.py` writes
  `datasets[]` but does not know where the files came from, and
  `validate_data.py` rejects any dataset without a `license` on the
  allow-list. Add `license` (and `src_provider`) to each entry after the first
  `build_manifest.py` run; later runs carry them forward.
- **The identity block** — `body`, `iso_a3`, `iso_a2`, `m49_region`, `name`,
  `crs`, `source`, `status` — which [Add a country](add-a-country.md) shows.

Size is the last check: `validate_data.py` fails any file over 50 MB, and
GitHub refuses pushes above 100 MB. Before reaching for Git LFS —
[don't](../about/versioning.md#why-not-git-lfs) — confirm the file is
simplified and trimmed to 6 decimals, and split it by ADM1 if it is still too
big.

--8<-- "abbreviations.md"
