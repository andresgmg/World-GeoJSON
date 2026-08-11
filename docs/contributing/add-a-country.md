# Add a country

End-to-end runbook. Budget an hour for your first one.

## 0. Check the licence

[Approved sources & licensing](sources.md). Do this first — it is the step most
likely to stop the contribution, and everything after it is wasted effort if
the source turns out to be unusable.

## 1. Set up

```powershell
git clone https://github.com/andresgmg/World-GeoJSON.git
cd World-GeoJSON
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-docs.txt
git checkout -b add-nzl
```

You also need [mapshaper](https://github.com/mbloch/mapshaper), which runs via
`npx` with no install step. Node 18 or newer.

## 2. Get the data

Using New Zealand and geoBoundaries as the worked example:

```bash
curl -LO https://www.geoboundaries.org/data/geoBoundaries-3_0_0/NZL/ADM1/geoBoundaries-3_0_0-NZL-ADM1.geojson
```

## 3. Normalise it

The full detail is in [Data pipeline](pipeline.md). The short version:

```bash
npx mapshaper geoBoundaries-3_0_0-NZL-ADM1.geojson \
  -rename-fields shapeName=shapeName \
  -each 'shapeGroup="NZL", shapeType="ADM1"' \
  -o precision=0.000001 format=geojson \
     data/earth/NZL/NZL_ADM1.geojson
```

Then confirm against [Property schema](../reference/schema.md):

- `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` present on every feature
- source attributes preserved under `src_`
- Esri artifacts (`objectid`, `st_area_sh`, …) removed
- `shapeISO` is a **string**, zero-padded where the official code is

And against [CRS](../reference/crs.md):

- EPSG:4326 / CRS84, longitude first
- no `crs` member in the file
- coordinates at 6 decimal places or fewer
- top-level `bbox` present

## 4. Write the manifest

Create `data/earth/NZL/manifest.json` with the hand-authored fields. Leave
`datasets` out — the scanner writes it.

```json
{
  "schema_version": 1,
  "body": "earth",
  "iso_a3": "NZL",
  "iso_a2": "NZ",
  "m49_region": "Australia and New Zealand",
  "name": { "en": "New Zealand", "es": "Nueva Zelanda" },
  "crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 },
  "source": {
    "name": "geoBoundaries",
    "url": "https://www.geoboundaries.org/",
    "license": "CC-BY-4.0",
    "retrieved": "2026-08-10"
  },
  "status": "review"
}
```

!!! tip "New Zealand crosses the antimeridian"

    The Chatham Islands sit east of 180°. Check that your geometry is cut at
    the antimeridian rather than using longitudes beyond 180, and note it in
    `notes`. See [CRS](../reference/crs.md#the-antimeridian).

## 5. Generate the manifest and preview

```powershell
.\.venv\Scripts\python.exe scripts\build_manifest.py data\earth\NZL
node scripts\make_previews.mjs data/earth/NZL
```

The first fills in `datasets` with feature counts, bbox, checksums and property
lists. The second writes simplified preview files — see
[Simplification & previews](previews.md) for the size budget.

## 6. Check it renders

```powershell
.\.venv\Scripts\python.exe -m mkdocs serve
```

Your country appears under **Catalog** automatically. Confirm the feature count
is plausible, the bounding box is in the right hemisphere, and the preview map
looks like the country.

## 7. Open the PR

Work through the [Review checklist](checklist.md) first.

Your PR should contain the data file(s), the manifest, and the preview file(s).
It should **not** contain generated documentation pages — those do not exist on
disk.

## Adding a level to an existing country

Same process, minus the manifest creation: drop the new file into the existing
directory and re-run `build_manifest.py`. It rewrites the `datasets` array and
leaves the curated fields alone.

## Correcting existing geometry

Say what changed and why in the PR description, and cite the source for the
correction. Boundary changes are the highest-scrutiny change in this
repository. If the correction reflects a sovereignty claim rather than a
mapping error, read
[Disputed boundaries](../about/disputed-boundaries.md) first.

--8<-- "abbreviations.md"
