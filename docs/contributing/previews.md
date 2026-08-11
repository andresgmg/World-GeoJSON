# Simplification & previews

Every dataset ships a simplified companion file used for the map on its catalog
page.

## Why previews exist

Full-resolution boundary data cannot be displayed in a browser. Chile's
communes file is 70 MB; loading it means 70 MB over the network, several
hundred megabytes of JavaScript heap after `JSON.parse`, and tens of seconds of
blocked main thread. On a phone that is a crashed tab, not a slow map.

Separately, **jsDelivr refuses files over 20 MB**, so the CDN path does not
exist for large files at all.

And a 420-pixel-tall map cannot render 11-centimetre precision anyway. The
detail is not being lost — it was never visible.

## Generating

```powershell
node scripts\make_previews.mjs data/earth/CHL
```

Which runs, per dataset:

```bash
npx mapshaper data/earth/CHL/CHL_ADM3.geojson \
  -simplify percentage=2% keep-shapes \
  -filter-fields shapeName,shapeISO,shapeType \
  -o precision=0.0001 format=geojson \
     data/earth/CHL/preview/CHL_ADM3.preview.geojson
```

Three reductions compound:

| Step | Effect |
|---|---|
| `-simplify percentage=2%` | Visvalingam simplification, keeping 2% of vertices |
| `keep-shapes` | Prevents small polygons collapsing to nothing |
| `-filter-fields` | Keeps only what the tooltip needs |
| `precision=0.0001` | ~11 m, ample for a small map |

Typical result: 70 MB → 300–800 KB.

## Size budget

| Threshold | Meaning |
|---|---|
| under 800 KB | Target |
| 800 KB – 2 MB | Acceptable for unusually complex geometry |
| over 2 MB | **CI fails.** Simplify harder |

If a preview will not come under budget at 2%, drop to 1% or 0.5%. Complex
coastlines — Chile, Norway, Indonesia, Greece — need more aggressive settings
than compact countries.

## Check the result

Simplification is lossy and its failure modes are visual, so look at it.

- **Islands disappearing.** `keep-shapes` prevents whole polygons vanishing,
  but a multipolygon can still lose small members. Compare feature counts
  before and after: they must match exactly.
- **Slivers and self-intersections.** Aggressive simplification can make
  adjacent boundaries cross, leaving visible gaps or overlaps between units.
- **Disconnected coastlines.** Look for units that no longer touch their
  neighbours.

```bash
npx mapshaper data/earth/CHL/preview/CHL_ADM3.preview.geojson -info
```

Feature count must equal the source. If it does not, the simplification dropped
geometry and the settings are too aggressive.

## Previews are committed

They are small, deterministic build artifacts, and committing them means the
documentation site needs no build step over the data. Regenerate them whenever
the source file changes — CI checks that they exist and are within budget, and
[`manifest.json`](../reference/manifest.md) records their size.

## Static thumbnails

mapshaper can also emit SVG:

```bash
npx mapshaper input.geojson -o format=svg width=800 output.svg
```

Around 20 KB, no JavaScript, renders in the GitHub README as well as on the
docs site. Useful as a fallback where an interactive map is overkill.

--8<-- "abbreviations.md"
