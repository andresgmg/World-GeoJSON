# Approved sources & licensing

**Read this before doing any other work on a data contribution.**

A boundary file with an incompatible licence cannot be merged, however good the
geometry is. And once it is in git history it is genuinely difficult to remove —
rewriting history breaks every existing clone and fork. So the check happens at
the door, and it is enforced in CI by `scripts/validate_data.py`.

## The compatibility question

This repository distributes data publicly, for free, for any use including
commercial. A source is usable here only if its licence permits exactly that.

Two failure modes matter:

- **Redistribution restrictions** — the licence forbids passing the data on, or
  forbids commercial use. Unusable, full stop.
- **Share-alike (copyleft) obligations** — the licence permits redistribution
  but requires derivatives to carry the same licence. ODbL in particular defines
  a *Derivative Database*, and mixing one into this collection would arguably
  pull the whole thing under ODbL, changing the terms for everyone already using
  it. **This project excludes copyleft data.**

## The allow-list

`source.license` must be one of these SPDX identifiers. CI rejects anything
else:

| SPDX id | Typical source |
|---|---|
| `public-domain` | Natural Earth |
| `CC0-1.0` | Some national open-data portals |
| `CC-BY-4.0` | geoBoundaries' own work, IDE Chile |
| `CC-BY-3.0`, `CC-BY-3.0-IGO` | OCHA / HDX country boundaries |
| `CC-BY-2.5` | Older national releases |
| `Etalab-2.0` | France and its overseas departments |
| `OGL-Canada-2.0` | Canada |

## Green — use freely

| Source | Licence | Notes |
|---|---|---|
| [Natural Earth](https://www.naturalearthdata.com/) | Public domain | **The right choice for ADM0.** One global 12.7 MB file covers every country at 1:10m, including territories that geoBoundaries omits entirely. *"No permission is needed to use Natural Earth."* |
| [IDE Chile / SUBDERE](https://www.geoportal.cl/) | CC BY | Official Chilean cartography. Used here for all three of Chile's tiers — see the DIFROL note below. |
| National SDIs with open licences | Varies | Check the specific terms; "government data" does not automatically mean "open". |
| [HDX / OCHA COD-AB](https://data.humdata.org/) | Often CC BY 3.0 IGO | The upstream that feeds geoBoundaries' better files. Going direct gets fresher data and a clearer per-country licence page. |

## Amber — verify the licence per file

| Source | Licence | The problem |
|---|---|---|
| [geoBoundaries](https://www.geoboundaries.org/) `gbOpen` | **Per file** | See below — this is not the simple CC BY 4.0 source it appears to be. |
| Wikidata / Wikimedia | CC0 for data, varies for geometry | The structured data is CC0, but geometry imported into it may carry the upstream licence. Trace the actual provenance. |

!!! warning "geoBoundaries is not uniformly CC BY 4.0"

    geoBoundaries' *own code and derivative works* are CC BY 4.0, and the
    project is excellent. But `gbOpen` is a **container of heterogeneous
    upstream licences**, and its citation file says so directly:

    > Users using individual boundary files from geoBoundaries should
    > additionally ensure that they are citing the sources provided in the
    > metadata for each file.

    Measured across the 129 Americas entries in `gbOpen`, **43 (33%) are
    copyleft** — 35 ODbL and 8 CC-BY-SA, almost all derived from
    OpenStreetMap. Those cannot be used here.

    Always read the `boundaryLicense` field from the API response for the
    specific country **and level** you are taking. Chile is a good example of
    why: its ADM1 and ADM3 are CC BY 3.0 IGO, but its ADM2 is ODbL.

    Use the `gbOpen` release only. `gbAuthoritative` is explicitly
    non-commercial, and `gbHumanitarian` has unverifiable per-file licensing.

## Red — do not use

| Source | Licence | The problem |
|---|---|---|
| [GADM](https://gadm.org/license.html) | Custom, non-commercial | **The most common mistake.** GADM's terms prohibit redistribution and commercial use without prior permission. It is the most convenient global boundary source and the first place a well-meaning contributor looks — which is exactly why it needs naming explicitly. |
| [OpenStreetMap](https://www.openstreetmap.org/) | ODbL 1.0 | Share-alike. This is what makes a third of geoBoundaries unusable here. Excellent data, incompatible terms. |
| Esri / ArcGIS Online basemap layers | Proprietary | Licensed for use within Esri products. Not redistributable. |
| Google Maps geometry | Proprietary | Extraction is prohibited by the terms of service. |
| Commercial providers (HERE, TomTom, …) | Proprietary | Never redistributable. |
| Any dataset with no stated licence | — | Absence of a licence means **all rights reserved**, not public domain. |

!!! danger "GADM is the trap"

    GADM is comprehensive, well maintained, free to download, and **not usable
    here**. Downloading it for your own analysis is fine. Contributing it to a
    public repository is a licence violation.

## Coverage gaps are acceptable; licence violations are not

Excluding copyleft leaves visible holes — 15 Americas countries have no ADM1
here because their geoBoundaries ADM1 is copyleft (13 ODbL, 2 CC-BY-SA) and
no permissive alternative has been found yet. That is the correct trade.

Gaps are recorded on the [Roadmap](../about/roadmap.md) as "awaiting a
permissive source", and the way to close one is to find a national SDI or HDX
release with acceptable terms, not to relax the rule.

## Recording the source

Every `manifest.json` must carry a complete `source` block:

```json
"source": {
  "name": "geoBoundaries",
  "url": "https://www.geoboundaries.org/countryDownloads.html",
  "license": "CC-BY-4.0",
  "retrieved": "2026-08-11"
}
```

- `license` **must** be an SPDX identifier from the allow-list above.
- `retrieved` matters: boundaries change, and knowing the vintage is how a
  consumer decides whether two datasets can safely be combined.
- The manifest's single-line `notes` field is where conditions that travel
  with a grant belong — for example, Chilean official cartography circulates
  under Resolución N°50 de 2019 of DIFROL, which asks that derived products
  be reviewed equally. (There is no separate `license_note` field.)

## If you are unsure

Open an issue and ask before doing the work. A licence question answered in ten
minutes is much cheaper than a contribution that cannot be merged — or worse,
one that is merged and later has to be removed.

--8<-- "abbreviations.md"
