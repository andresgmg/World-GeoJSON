# Approved sources & licensing

**Read this before doing any other work on a data contribution.**

A boundary file with an incompatible licence cannot be merged, however good the
geometry is. And once it is in git history it is genuinely difficult to remove
— rewriting history breaks every existing clone and fork. So the check happens
at the door.

## The compatibility question

This repository distributes data publicly, for free, for any use including
commercial. A source is usable here only if its licence permits exactly that.

Two failure modes matter:

- **Redistribution restrictions** — the licence forbids passing the data on, or
  forbids commercial use. Unusable, full stop.
- **Share-alike (copyleft) obligations** — the licence permits redistribution
  but requires derivatives to carry the same licence. Usable only if the whole
  project accepts that licence, which changes the terms for every existing
  consumer.

## Green — use freely

| Source | Licence | Notes |
|---|---|---|
| [Natural Earth](https://www.naturalearthdata.com/) | Public domain | Small-scale (1:10m–1:110m). Ideal for ADM0 and world overviews. No attribution required, though it is polite. |
| [geoBoundaries](https://www.geoboundaries.org/) | CC BY 4.0 | The best open global source for ADM1–ADM3. **Attribution required** — record it in the manifest. This project's property vocabulary matches theirs deliberately. |
| National SDIs with open licences | Varies | e.g. Chile's BCN / IDE Chile. Check the specific terms; "government data" does not automatically mean "open". |
| [OpenStreetMap-derived under a separate licence](https://osmdata.openstreetmap.de/) | Varies | Some derived products are released under non-ODbL terms. Verify per product. |

## Amber — usable only with care

| Source | Licence | The problem |
|---|---|---|
| [OpenStreetMap](https://www.openstreetmap.org/) | ODbL 1.0 | **Share-alike.** A derived database must also be ODbL. Boundaries extracted from OSM cannot be relicensed, and mixing them into this repository would arguably pull the entire data tree under ODbL — changing the terms for everyone already using it. Not accepted without an explicit project-level decision to dual-licence. |
| Wikidata / Wikimedia | CC0 for data, varies for geometry | The structured data is CC0, but geometry imported into it may carry the upstream licence. Trace the actual provenance. |

## Red — do not use

| Source | Licence | The problem |
|---|---|---|
| [GADM](https://gadm.org/license.html) | Custom, non-commercial | **The most common mistake.** GADM's terms prohibit redistribution and commercial use without prior permission. It is the most convenient global boundary source and the first place a well-meaning contributor looks — which is exactly why it needs naming explicitly. Incompatible with this repository in every respect. |
| Esri / ArcGIS Online basemap layers | Proprietary | Licensed for use within Esri products. Not redistributable. |
| Google Maps geometry | Proprietary | Extraction is prohibited by the terms of service. |
| Commercial providers (HERE, TomTom, …) | Proprietary | Per-seat or per-request licences. Never redistributable. |
| Any dataset with no stated licence | — | Absence of a licence means **all rights reserved**, not public domain. |

!!! danger "GADM is the trap"

    If you take one thing from this page: GADM is comprehensive, well
    maintained, free to download, and **not usable here**. Downloading it
    yourself for personal analysis is fine. Contributing it to a public
    MIT/CC-BY repository is a licence violation.

    A PR whose geometry matches GADM's characteristic vertex patterns will be
    questioned even if the source field says otherwise.

## Recording the source

Every dataset's `manifest.json` must carry a complete `source` block:

```json
"source": {
  "name": "geoBoundaries",
  "url": "https://www.geoboundaries.org/countryDownloads.html",
  "license": "CC-BY-4.0",
  "retrieved": "2026-08-10"
}
```

- `license` **must** be an [SPDX identifier](https://spdx.org/licenses/) where
  one exists. CI validates it against the approved list.
- `retrieved` matters: boundaries change, and knowing the vintage is how a
  consumer decides whether two datasets can be safely combined.

## If you are unsure

Open an issue and ask before doing the work. A licence question answered in ten
minutes is much cheaper than a contribution that cannot be merged — or worse,
one that is merged and later has to be removed.

--8<-- "abbreviations.md"
