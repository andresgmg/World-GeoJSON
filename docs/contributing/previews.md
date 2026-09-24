# Simplification & previews

Every dataset ships a simplified companion file used for the map on its catalog
page.

## Why previews exist

Full-resolution boundary data cannot be displayed in a browser. Files under
`data/` are already simplified to a 100 m tolerance and still run to 5–15 MB —
Chile's communes are 7 MB, Canada's provinces 14.9 MB. Loading one means that
much over the network, a multiple of it in JavaScript heap after `JSON.parse`,
and a blocked main thread while it parses. On a phone that is a crashed tab,
not a slow map.

Separately, **jsDelivr refuses files over 20 MB** and may refuse a repository
over 150 MB, so the CDN path is not something a catalog map can depend on.

And a 420-pixel-tall map cannot render 11-centimetre precision anyway. The
detail is not being lost — it was never visible.

## Generating

```bash
node scripts/make_previews.mjs data/earth/CHL
npm run previews                              # every country
```

Run it **before** `build_manifest.py`: the manifest records a preview's path
and size only if the file already exists.

For each level the script runs mapshaper, starting at 5% of vertices:

```bash
npx mapshaper data/earth/CHL/CHL_ADM3.geojson \
  -simplify percentage=5% keep-shapes \
  -filter-fields shapeName,shapeISO,shapeType \
  -o precision=0.0001 bbox format=geojson \
     data/earth/CHL/preview/CHL_ADM3.preview.geojson
```

and then, while the result is over 800 KB, halves the percentage — 2.5%,
1.25%, 0.625% — down to a floor of 0.2%. A split level is built from its
combined file, or from the parts merged together when there is none (Brazil
ADM2), so the preview covers the whole country.

| Step | Effect |
|---|---|
| `-simplify percentage=5%` | Visvalingam simplification, keeping 5% of vertices |
| `keep-shapes` | Prevents small polygons collapsing to nothing |
| `-filter-fields` | Keeps only what the tooltip needs |
| `precision=0.0001` | ~11 m, ample for a small map |

Typical result: 7 MB → 425 KB for Chile's 345 communes; 4.8 MB → 226 KB for
its 16 regions.

## Size budget

| Threshold | Meaning |
|---|---|
| under 800 KB | Target — the script stops halving here |
| 800 KB – 2 MB | Acceptable for unusually complex geometry that is still over target at 0.2% |
| over 2 MB | **Rejected.** `make_previews.mjs` refuses to write it, and `validate_data.py` fails CI |

A preview still over 2 MB at 0.2% means the source geometry is unusually
dense; the fix is upstream, in the source file's simplification tolerance,
not in the preview.

## Check the result

Simplification is lossy and its failure modes are visual, so look at it.

- **Islands disappearing.** `keep-shapes` prevents whole polygons vanishing,
  but a multipolygon can still lose small members. The script compares the
  feature count against the source and refuses to write a preview that
  dropped any — but a multipolygon member is not a feature, so look.
- **Slivers and self-intersections.** Aggressive simplification can make
  adjacent boundaries cross, leaving visible gaps or overlaps between units.
- **Disconnected coastlines.** Look for units that no longer touch their
  neighbours.

```bash
npx mapshaper data/earth/CHL/preview/CHL_ADM3.preview.geojson -info
```

## Previews are committed

They are small build artifacts, and committing them means the documentation
site needs no build step over the data. They are deterministic as long as the
inputs are processed in a fixed order, which the script does — levels and
split parts sorted by name — so regenerating from unchanged sources yields
unchanged bytes.

Regenerate them whenever the source file changes. `validate_data.py` treats a
dataset with no preview recorded as a warning (the catalog map is empty), and
a recorded preview that is missing or over 2 MB as an error;
[`manifest.json`](../reference/manifest.md) records the path and size.

## Static thumbnails

mapshaper can also emit SVG:

```bash
npx mapshaper input.geojson -o format=svg width=800 output.svg
```

Around 20 KB, no JavaScript, renders in the GitHub README as well as on the
docs site. Useful as a fallback where an interactive map is overkill.

--8<-- "abbreviations.md"
