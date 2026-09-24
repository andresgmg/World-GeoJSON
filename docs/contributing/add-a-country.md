# Add a country

End-to-end runbook. Budget an hour for your first one. The scripts do most of
the work; the order matters — previews before the manifest, the index after
it.

## 0. Check the licence

[Approved sources & licensing](sources.md). Do this first — it is the step most
likely to stop the contribution, and everything after it is wasted effort if
the source turns out to be unusable. `fetch_sources.py --dry-run` (step 3)
tells you what geoBoundaries offers for a country and under which licence,
without downloading anything.

## 1. Set up

```bash
git clone https://github.com/andresgmg/World-GeoJSON.git
cd World-GeoJSON
python -m venv .venv && source .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r requirements-docs.txt -r requirements-dev.txt   # mkdocs, ijson, jsonschema
npm install                                          # mapshaper, pinned
git checkout -b add-nzl
```

Python 3.11 or newer, Node 18 or newer.

## 2. Declare it in the registry

Add an entry to `scripts/countries.json`. Using New Zealand and geoBoundaries
as the worked example:

```json
"NZL": {
  "iso_a2": "NZ",
  "m49_region": "Australia and New Zealand",
  "name": { "en": "New Zealand", "es": "Nueva Zelanda" },
  "adm1_term": { "en": "Region", "es": "Región" },
  "municipal_level": "ADM2",
  "municipal_term": { "en": "Territorial authority", "es": "Autoridad territorial" },
  "source": "geoboundaries",
  "verify": true,
  "note": "The Chatham Islands sit east of 180°; geometry is cut at the antimeridian."
}
```

`municipal_level` is the one field you have to research: which ADM level is
the municipal tier is a fact about the country, not something the data
reveals. `verify: true` ships the manifest with `status: "review"` until
someone has checked the level assignment and unit count against an official
source. [Data pipeline](pipeline.md#0-declare-the-country) documents every
field.

## 3. Fetch the sources

```bash
python scripts/fetch_sources.py --iso3 NZL --dry-run
python scripts/fetch_sources.py --iso3 NZL
```

The dry run lists each level with its licence and unit count and marks what is
rejected. Anything copyleft never reaches your disk. Accepted files land in
`.cache/sources/`, which is git-ignored.

## 4. Build the data

```bash
python scripts/build_data.py NZL
```

Writes `data/earth/NZL/NZL_ADM0.geojson`, `NZL_ADM1.geojson`, … — reprojected,
renamed onto the [standard schema](../reference/schema.md), simplified to a
100 m tolerance, split by ADM1 where the municipal tier needs it, and
**finalized**: every feature gets its `id`, its `adm1ISO`, `parentISO` and
`parentID`, a `shapeISO` corrected from `scripts/shapeiso_fixes.json` (or
`""` where the upstream has no code) and a recomputed `bbox`, in the
canonical one-feature-per-line layout — plus the manifest's identity and
provenance. Before the next steps the manifest looks like this, with
`license` and `simplification` already on each entry of `datasets`:

```json
{
  "schema_version": 1,
  "body": "earth",
  "iso_a3": "NZL",
  "iso_a2": "NZ",
  "m49_region": "Australia and New Zealand",
  "name": { "en": "New Zealand", "es": "Nueva Zelanda" },
  "crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 },
  "status": "review",
  "source": {
    "name": "geoBoundaries (gbOpen)",
    "url": "https://www.geoboundaries.org/",
    "license": "CC-BY-4.0",
    "retrieved": "2026-09-24"
  },
  "notes": "The Chatham Islands sit east of 180°; geometry is cut at the antimeridian."
}
```

`status`, `notes` and the `source` block's `name`, `url` and `retrieved` are
only filled in when absent, so you can edit them and re-run safely. `iso_a2`,
`m49_region` and `crs` are overwritten from the registry — change them there.

!!! note "If the build stops on a duplicate `id`"

    Two units with the same name and no code would get the same `id`;
    `finalize_geojson.py` refuses and names them. Fix the cause: an entry in
    `scripts/shapeiso_fixes.json` if the upstream code is wrong, or a pinned
    key in `scripts/id_overrides.json` otherwise. See
    [Data pipeline → The finalize step](pipeline.md#the-finalize-step).

!!! tip "New Zealand crosses the antimeridian"

    The Chatham Islands sit east of 180°. Check that the output is cut at the
    antimeridian rather than using longitudes beyond 180, and say so in
    `notes`. See [CRS](../reference/crs.md#the-antimeridian).

## 5. Generate the previews

```bash
node scripts/make_previews.mjs data/earth/NZL
```

Before the manifest, not after: `build_manifest.py` records a preview only if
it already exists. See [Simplification & previews](previews.md) for the size
budget.

## 6. Generate the manifest

```bash
python scripts/build_manifest.py data/earth/NZL
```

Fills in `datasets` with paths, sizes, checksums, feature counts, bounding
boxes, property lists and preview sizes. The hand-authored fields are left
alone.

## 7. Regenerate the index

```bash
python scripts/build_index.py
```

`data/index.json` embeds every manifest, so it changes whenever one does. CI
fails if the committed index is stale. Commit it with the rest.

## 8. Validate

```bash
python scripts/validate_data.py --checksums data/earth/NZL
python scripts/finalize_geojson.py --check data/earth/NZL
python scripts/build_index.py --check
```

Zero errors before you open the PR — these are the three checks CI runs.
Warnings — a dataset without a preview, coordinates beyond 6 decimals — do
not fail CI but do get review comments.

## 9. Check it renders

```bash
mkdocs serve
```

Your country appears under **Catalog** automatically. Confirm the feature count
is plausible, the bounding box is in the right hemisphere, and the preview map
looks like the country.

## 10. Open the PR

Work through the [Review checklist](checklist.md) first.

Your PR should contain the registry entry, the data file(s), the manifest, the
preview file(s) and the regenerated `data/index.json`. It should **not**
contain anything from `.cache/` or generated documentation pages — neither
exists as far as git is concerned.

## Adding a level to an existing country

Re-run steps 3 to 8 for that country. `build_data.py` leaves the manifest's
hand-authored fields alone; `build_manifest.py` rewrites `datasets` and
carries each entry's `license` forward.

## A source the scripts do not know

If the country's data comes from a national SDI rather than geoBoundaries,
build the files with mapshaper or ogr2ogr as
[Data pipeline](pipeline.md#building-by-hand) describes, drop them into
`data/earth/XXX/`, run `python scripts/finalize_geojson.py data/earth/XXX` to
give them their ids, hierarchy and canonical layout, and run steps 5 to 8.
Then add `license` to every entry in
`datasets` by hand — `validate_data.py` rejects a dataset without one, and
only `build_data.py` writes it — plus the identity block shown in step 4.
Teaching `build_data.py` the new provider is the better contribution if you
expect to repeat it.

## Correcting existing geometry

Say what changed and why in the PR description, and cite the source for the
correction. Boundary changes are the highest-scrutiny change in this
repository. If the correction reflects a sovereignty claim rather than a
mapping error, read
[Disputed boundaries](../about/disputed-boundaries.md) first.

--8<-- "abbreviations.md"
