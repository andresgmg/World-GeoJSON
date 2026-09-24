# Get started

Using this project is three steps.

1. **Find your dataset** in the [Catalog](../catalog/index.md). Each page lists
   the administrative levels available for that country, how many features each
   has, and its bounding box.
2. **Copy a URL.** Every dataset page gives a CDN URL, a raw GitHub URL and a
   `curl` command; the parts of a split level link to the CDN only.
   [Download & CDN](download.md) explains which to use when — the answer is
   not always the CDN.
3. **Load it.** [Quick start](quickstart.md) has working snippets for Leaflet,
   MapLibre, Python and QGIS.

## Before you start: file sizes

Administrative boundary data is large, and this project stores it uncompressed
so it stays diff-able and directly consumable. Every file under `data/` is
simplified to a 100 m ground tolerance, which keeps the largest — Canada's
ADM1 — at 14.9 MB and everything under 20 MB. Chile's 345 communes are 7 MB.

That has consequences worth knowing up front:

- **Do not load a full-resolution file into a browser.** Fifteen megabytes
  over the network becomes a multiple of that in JavaScript heap after
  `JSON.parse`, with the main thread blocked while it parses. On mobile it is
  a crashed tab, not a slow map. Use the simplified previews instead: every
  dataset has one at `data/earth/{ISO3}/preview/{ISO3}_{LEVEL}.preview.geojson`
  — at most 2 MB, four-decimal coordinates, only `shapeName`, `shapeISO` and
  `shapeType` — and they are fine to load in a browser. Or simplify to your
  own tolerance — see [Recipes](recipes.md#simplify-for-the-web).
- **Do not clone the whole repository** just to get one country. Use a sparse
  checkout; [Download & CDN](download.md#git) shows how.
- **The CDN is not guaranteed.** jsDelivr caps files at 20 MB — every file in
  `data/` is under that — but it also documents a 150 MB limit per repository,
  which this one currently exceeds, so it may refuse to serve it. Raw GitHub
  URLs always work.

!!! note "The legacy root files are the exception"

    `comunas.geojson` in the repository root is an older 72 MB dataset kept
    only so existing links keep working. Its replacement is
    `data/earth/CHL/CHL_ADM3.geojson`.

## Which admin level do you want?

| You want | Level | In Chile |
|---|---|---|
| First-level divisions | ADM1 | 16 *regiones* |
| Second-level divisions | ADM2 | 56 *provincias* |
| The municipal tier | ADM3 | 345 *comunas* |

Level numbers are structural, not semantic: a country's ADM1 is whatever its
first-level division happens to be called. See
[Administrative levels](../reference/admin-levels.md).

--8<-- "abbreviations.md"
