# Get started

Using this project is three steps.

1. **Find your dataset** in the [Catalog](../catalog/index.md). Each page lists
   the administrative levels available for that country, how many features each
   has, and its bounding box.
2. **Copy a URL.** Every dataset page gives a CDN URL, a raw GitHub URL and a
   `curl` command. [Download & CDN](download.md) explains which to use when —
   the answer is not always the CDN.
3. **Load it.** [Quick start](quickstart.md) has working snippets for Leaflet,
   MapLibre, Python and QGIS.

## Before you start: file sizes

Administrative boundary data is large, and this project stores it uncompressed
so it stays diff-able and directly consumable. Concretely, Chile's communes
file is **70 MB**.

That has consequences worth knowing up front:

- **Do not load a full-resolution file into a browser.** 70 MB over the network
  becomes several hundred megabytes of JavaScript heap after `JSON.parse`, plus
  tens of seconds of blocked main thread. On mobile it is a crashed tab, not a
  slow map. Use the simplified preview files, or simplify to your own tolerance
  — see [Recipes](recipes.md#simplify-for-the-web).
- **Do not clone the whole repository** just to get one country. Use a sparse
  checkout; [Download & CDN](download.md#git) shows how.
- **The CDN has a 20 MB ceiling.** Files above it must come from raw GitHub.

## Which admin level do you want?

| You want | Level | In Chile |
|---|---|---|
| The outline of the country | ADM0 | Chile |
| First-level divisions | ADM1 | 16 *regiones* |
| Second-level divisions | ADM2 | *provincias* — no open boundary file exists |
| Third-level divisions | ADM3 | 343 *comunas* |

Level numbers are structural, not semantic: a country's ADM1 is whatever its
first-level division happens to be called. See
[Administrative levels](../reference/admin-levels.md).

--8<-- "abbreviations.md"
