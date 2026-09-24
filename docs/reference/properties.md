# Property dictionary

Every property key that appears anywhere in the corpus, what it means, and
where it is present. The tables below were checked against the data; each
dataset's own sorted list is in its [`manifest.json`](manifest.md) under
`datasets[].properties`.

## Standard properties

Defined by this project and present on **every** feature in every file. See
[Property schema](schema.md).

| Key | Type | Meaning |
|---|---|---|
| `shapeName` | string | Local-language name, with diacritics |
| `shapeISO` | string | Official code — ISO 3166-2 where one exists, otherwise the national code. Not yet a safe join key everywhere; see [Known issues](#known-issues-fixed-in-v100) |
| `shapeGroup` | string | ISO 3166-1 alpha-3 of the country, or body code |
| `shapeType` | string | `ADM0`–`ADM4` (or `QUAD`, once planetary data exists) |

## Hierarchy properties

Present on some features, not all. Exactly where:

| Key | Type | Meaning | Present on |
|---|---|---|---|
| `adm1ISO` | string | `shapeISO` of the ADM1 the feature belongs to — the code the split file is named after | Every split part (`{LEVEL}/{code}.geojson`), and every feature of Chile's combined `CHL_ADM3.geojson`. Combined files of other split levels do not carry it |
| `parentISO` | string | `shapeISO` of the **immediate** parent unit | Chile only, today: ADM2 (its region, e.g. `CL-MA`) and ADM3 (its province, e.g. `014`) |

!!! note "`parentISO` and `adm1ISO` are not the same thing"

    On a Chilean commune, `parentISO` is its *province* — the immediate parent
    in the official hierarchy — while `adm1ISO` is its *region*, which is what
    the file is keyed by. Both are useful and both are recorded.

!!! info "Planned for v1.0.0"

    The v1.0.0 data contract adds a Feature-level `id`
    (`{ISO3}:{LEVEL}:{code}`), and `parentID` and `adm1ISO` on **every**
    sub-national feature, so nesting works the same way in every country
    rather than only in Chile. See the [Roadmap](../about/roadmap.md).

## Source properties — geoBoundaries

Every feature taken from geoBoundaries — ADM1 and below, 15,726 features today
— carries one extra field:

| Key | Type | Meaning |
|---|---|---|
| `src_shape_id` | string | geoBoundaries' own opaque identifier for the unit, e.g. `66186276B69138566591314`. Stable within a geoBoundaries release; not a territorial code |

geoBoundaries' other four fields (`shapeName`, `shapeISO`, `shapeGroup`,
`shapeType`) already match the standard vocabulary, which is why this project
adopted it. Its `shapeID` is renamed to `src_shape_id` on the way in; no file
carries a property called `shapeID`.

## Source properties — Chile

Preserved from IDE Chile's DPA 2023 under the `src_` prefix.

| Key | Type | Present on | Meaning |
|---|---|---|---|
| `src_cut_reg` | string | ADM1, ADM2, ADM3 | CUT region code, two characters |
| `src_cut_prov` | string | ADM2, ADM3 | CUT province code, three characters |
| `src_cut_com` | string | ADM3 | CUT commune code, five characters, zero-padded |
| `src_region` | string | ADM2, ADM3 | Region name, without the "Región de" prefix |
| `src_provincia` | string | ADM3 | Province name |
| `src_superficie_km2` | number | ADM1 | Official area in **square kilometres**. The only non-string property in the corpus |

CUT (*Código Único Territorial*) is the national territorial coding scheme used
by INE and SUBDERE. Codes nest: commune `01402` (Camiña) sits in province `014`
(Tamarugal), which sits in region `01` (Tarapacá).

## Properties that get dropped

Export artifacts from the source GIS software. They carry no information that
cannot be recomputed, and they mislead.

| Key | Why it goes |
|---|---|
| `objectid` | An Esri internal row number. Not stable across exports |
| `st_area_sh` | Precomputed area in square metres, from an unstated projection |
| `st_length_` | Precomputed perimeter, same problem |
| `shape_leng` | Duplicate of `st_length_`, truncated to the dBase 10-character field limit |

## Known issues (fixed in v1.0.0)

!!! warning "Read this before joining on `shapeISO`"

    - On **22 municipal datasets** `shapeISO` holds the opaque geoBoundaries
      id (e.g. `52423323B35289781006587`) instead of a territorial code: the
      pipeline fell back to the upstream `shapeID` wherever geoBoundaries
      shipped an empty `shapeISO`. Affected: ARG ADM2, BOL ADM3, BRA ADM2,
      COL ADM2, CRI ADM2, DOM ADM2, ECU ADM2, GLP ADM4, GTM ADM2, GUF ADM3,
      GUY ADM2, HND ADM2, HTI ADM3, MEX ADM2, MTQ ADM4, PAN ADM2, PRI ADM2,
      PRY ADM2, SLV ADM2, SUR ADM2, USA ADM2 and VIR ADM3.
    - `shapeISO` is **not unique** in BLZ ADM2 (31 units carry only six
      distinct codes — their district's), MEX ADM1 (`MX-MEX` twice) and
      ECU ADM1 (`EC-H` twice).
    - **No feature has a GeoJSON Feature-level `id`** yet.

    Do not treat `shapeISO` as a guaranteed unique join key today. v1.0.0 adds
    `id` = `{ISO3}:{LEVEL}:{code}`, `parentID` and `adm1ISO` on every feature,
    and stops filling `shapeISO` with opaque ids.

## Known traps

!!! danger "Territorial codes must be strings"

    A JSON number cannot hold a leading zero, so any source storing Chile's
    `01402` as an integer silently yields `1402`, and joins against official
    statistics match nothing. `shapeISO` and every `src_cut_*` field are
    strings.

!!! warning "`shapeISO` is not yet a safe identity everywhere"

    Where it is opaque or duplicated (see above), use `src_shape_id` for
    identity on geoBoundaries data and `shapeName` for display.

!!! warning "The GeoJSON `id` member is not used yet"

    No file under `data/` sets the Feature-level `id` today. Identity lives in
    properties until v1.0.0 introduces a stable `id` on every feature.

## Regenerating this page

Property lists are recorded per dataset in each
[`manifest.json`](manifest.md). This page is maintained by hand; generating it
from the manifests is on the [Roadmap](../about/roadmap.md).

--8<-- "abbreviations.md"
