# Versioning & stability

## What counts as the public API

For a data repository, the API is not a function signature. It is:

1. **File paths.** People hard-code URLs.
2. **Property names and types.** People write code against `feature.properties.shapeName`.
3. **Feature identity.** `shapeISO` values — and, from v1.0.0, the Feature
   `id` — are used as join keys.

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

Releases are git tags. **No tag exists yet**: `v1.0.0` is the first one
planned, once the data contract on the [Roadmap](roadmap.md) is in place. Until
then the only reference is `main`, reached through raw URLs:

```
https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/<path>
```

Once `v1.0.0` is tagged, **pin the tag in production** — the same raw URL with
the tag in place of `main`, or jsDelivr's `@tag` form:

```
https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v1.0.0/<path>
https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0/<path>
```

`main` follows the default branch, so an upstream boundary correction reaches
your application unannounced.

!!! note "jsDelivr may refuse this repository"

    jsDelivr documents limits of 150 MB per repository and 20 MB per file for
    its GitHub endpoint, and this repository is over 150 MB. Raw URLs, or a git
    sparse checkout of the country directories you need, are the reliable
    path today.

From v1.0.0 on, each release also publishes **per-country zip assets** on the
GitHub Release — one archive per territory with its files and manifest — for
consumers who want a download rather than a clone or a CDN.

## The legacy root files

Chile now lives at `data/earth/CHL/` under the standard property schema, built
from IDE Chile's DPA 2023. The old files remain at the repository root and are
deprecated:

| Deprecated | Replacement |
|---|---|
| `/main/regiones.geojson`, `/main/regiones.json` | `/main/data/earth/CHL/CHL_ADM1.geojson` |
| `/main/comunas.geojson`, `/main/comunas.json` | `/main/data/earth/CHL/CHL_ADM3.geojson` |
| `properties.Region` / `properties.Comuna` | `properties.shapeName` |
| `properties.cod_comuna` (number) | `properties.shapeISO` (string, zero-padded) |

The replacements are not byte-equivalent. They come from a different source
(IDE Chile DPA 2023 rather than BCN's older vector set), carry a different
property schema, contain 345 communes rather than 343, and are simplified to a
documented 100 m tolerance. Treat this as a migration, not a move.

### Deprecation window

All four root-level files — `regiones.geojson`, `regiones.json`,
`comunas.geojson`, `comunas.json` — **stay in place, unchanged, through the
whole 1.x series, and are removed in v2.0.0.**

This is not tidiness. Somebody out there has
`raw.githubusercontent.com/…/main/comunas.geojson` in production. Moving it
returns a 404 with no explanation, and there is no redirect mechanism for raw
data URLs — `mkdocs-redirects` handles documentation pages only. The only
humane migration path is to leave the old files where they are and announce the
move.

They will be removed in a tagged release, not silently on `main`.

## Why not Git LFS

The obvious reaction to a 72 MB file, and a trap.

- **Bandwidth quota.** GitHub's free tier allows 1 GB/month of LFS bandwidth. A
  popular public data repository exhausts that in days, after which
  **downloads fail for everyone** until someone buys data packs.
- **It breaks CDNs.** jsDelivr and most mirrors serve the LFS pointer file — a
  132-byte text stub — rather than the data.
- **It complicates partial clones.** `--filter=blob:none` and sparse checkout
  interact awkwardly with LFS.
- **It is not needed.** The repository's packed size is about 56 MiB for a
  working tree of about 309 MB, 164 MB of it under `data/`. JSON compresses
  well and Git is handling this fine.

The real fix for file size is minification and coordinate precision, and the
new files already apply it: one feature per line at six decimals makes
`CHL_ADM3.geojson` 7 MB where the legacy `comunas.geojson` is 72 MB.

## Library versioning

The client libraries planned in Phase 3 of the [Roadmap](roadmap.md) — Python
`world-geojson`, TypeScript `@world-geojson/core` — are versioned
**independently of the data**:

- A library's semver describes its own API. Its major bumps when a function
  signature breaks, not when a boundary moves.
- Each library declares which data `schema_version` (of the manifest and
  `index.json`) it supports, and pins a data tag by default, so a data release
  never reaches an application unannounced through a library update.
- A data minor (a new country, a new level) needs no library change. A data
  major that changes the schema needs a library release that declares support
  for it.

## Deprecating a dataset

A dataset whose source becomes unusable — licence change, withdrawal — is
marked `"status": "deprecated"` in its manifest and flagged on its catalog page
with a replacement pointer where one exists. It is removed in the next major
release.

Data is not deleted from git history. Rewriting history breaks every existing
clone and fork, and for a public data repository that cost far exceeds the
benefit.

--8<-- "abbreviations.md"
