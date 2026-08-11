# Versioning & stability

## What counts as the public API

For a data repository, the API is not a function signature. It is:

1. **File paths.** People hard-code URLs.
2. **Property names and types.** People write code against `feature.properties.shapeName`.
3. **Feature identity.** `shapeISO` values are used as join keys.

Changing any of these breaks consumers silently — no compiler error, no
exception, just a map that renders empty or a join that matches nothing.

Geometry is different. Boundary refinements, added vertices and corrected
coastlines are expected within a version.

## Semantic versioning

| Change | Bump |
|---|---|
| Renaming or moving a file | **Major** |
| Renaming a property, or changing its type | **Major** |
| Changing `shapeISO` values | **Major** |
| Removing a dataset | **Major** |
| Adding a country or a level | Minor |
| Adding an optional property | Minor |
| Refining geometry | Patch |
| Correcting a name or a typo | Patch |

Releases are git tags. **Pin a tag in production**:

```
https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0/<path>
```

`@main` follows the default branch, so an upstream boundary correction reaches
your application unannounced.

## The upcoming breaking change

Restructuring Chile's data into `data/earth/CHL/` with the standard property
schema is a major change. Both the paths and the property names move:

| Today | Becomes |
|---|---|
| `/main/regiones.geojson` | `/main/data/earth/CHL/CHL_ADM1.geojson` |
| `/main/comunas.geojson` | `/main/data/earth/CHL/CHL_ADM3.geojson` |
| `properties.Region` | `properties.shapeName` |
| `properties.cod_comuna` (number) | `properties.shapeISO` (string) |

### Deprecation window

The four root-level files — `regiones.geojson`, `regiones.json`,
`comunas.geojson`, `comunas.json` — **stay in place, unchanged, for one full
major version.**

This is not tidiness. Somebody out there has
`raw.githubusercontent.com/…/main/comunas.geojson` in production. Moving it
returns a 404 with no explanation, and there is no redirect mechanism for raw
data URLs — `mkdocs-redirects` handles documentation pages only. The only
humane migration path is to leave the old files where they are and announce the
move.

They will be removed in a tagged release, not silently on `main`.

## Why not Git LFS

The obvious reaction to a 70 MB file, and a trap.

- **Bandwidth quota.** GitHub's free tier allows 1 GB/month of LFS bandwidth. A
  popular public data repository exhausts that in days, after which
  **downloads fail for everyone** until someone buys data packs.
- **It breaks CDNs.** jsDelivr and most mirrors serve the LFS pointer file — a
  132-byte text stub — rather than the data.
- **It complicates partial clones.** `--filter=blob:none` and sparse checkout
  interact awkwardly with LFS.
- **It is not needed.** The repository's packed size is about 8.5 MB; the
  pretty-printed JSON compresses roughly 9:1. Git is handling this fine.

The real fix for file size is minification and coordinate precision, which
together remove more than half the bytes with no loss of usable information.

## Deprecating a dataset

A dataset whose source becomes unusable — licence change, withdrawal — is
marked `"status": "deprecated"` in its manifest and flagged on its catalog page
with a replacement pointer where one exists. It is removed in the next major
release.

Data is not deleted from git history. Rewriting history breaks every existing
clone and fork, and for a public data repository that cost far exceeds the
benefit.

--8<-- "abbreviations.md"
