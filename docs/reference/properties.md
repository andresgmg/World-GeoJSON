# Property dictionary

Every property key that appears anywhere in the corpus, what it means, and
where it is present. The tables below were checked against the data; each
dataset's own sorted list is in its [`manifest.json`](manifest.md) under
`datasets[].properties`, and the contract itself is enforced by a JSON Schema,
[`feature-properties.schema.json`](index-json.md#schemas), on every feature of
every full-resolution file in CI.

## Standard properties

Defined by this project and present on **every** feature in every file. See
[Property schema](schema.md).

| Key | Type | Meaning |
|---|---|---|
| `shapeName` | string | Local-language name, with diacritics |
| `shapeISO` | string | Official code — ISO 3166-2 where one exists, otherwise the national code; `""` when the upstream has none. Never an opaque id. Unique within a level wherever it is non-empty |
| `shapeGroup` | string | ISO 3166-1 alpha-3 of the country, or body code |
| `shapeType` | string | `ADM0`–`ADM4` (or `QUAD`, once planetary data exists) |

### `shapeISO` in detail

**Empty means "no code".** geoBoundaries ships no code for most municipal
units, and the pipeline no longer papers over that with the upstream's opaque
identifier: `shapeISO` is `""` on 15,364 features — 14,797 of ADM2, 501 of
ADM3 and all 66 ADM4. The upstream id is still there, as `src_shape_id`, and
the feature's identity is its [`id`](#the-feature-id).

**Documented upstream errors are corrected**, from
`pipeline/src/wgj/tables/shapeiso_fixes.json`. Every entry there is an ISO
3166-2 code the upstream got wrong for the unit named in `shapeName`:

| Where | Unit | Upstream | Corrected |
|---|---|---|---|
| USA ADM1 | South Dakota | `SU-SD` | `US-SD` |
| MEX ADM1 | Ciudad de México ("Distrito Federal" upstream) | `MX-MEX`, duplicating the State of Mexico | `MX-CMX` |
| ECU ADM1 | Cotopaxi | `EC-H`, duplicating Chimborazo | `EC-X` |
| BLZ ADM2 | all 31 units | their district's code, repeated | `""` |

The registry is not for inventing codes. A unit without an ISO 3166-2 code
keeps `""` and gets a name-based `id`.

**Unique within a level wherever it is non-empty.** The three corrections
above resolved the only duplicates, and the `id` rule below only ever uses a
code that is unique within its level — a duplicated code would be passed over
for a name-based key, not silently reused.

**Always a string**, even when it looks numeric (`"01402"`).

## Hierarchy properties

Present below ADM0 according to fixed rules — the same in every country, not
only in Chile:

| Key | Type | Meaning | Present on |
|---|---|---|---|
| `adm1ISO` | string | Key of the ADM1 unit the feature belongs to — the code its split part is named after | Every feature below ADM1 in a country that publishes an ADM1 (13,181 features), in the combined level files as well as in the parts. `"unassigned"` on the 12 features whose parent could not be determined (ARG 8, BRA 3, USA 1). Not on ADM1 itself |
| `parentISO` | string | Key of the parent at the **previous published level** | Every feature that has a parent level in the catalog: the ISO3 on ADM1 (`"CHL"`), the region on Chile's provinces (`"CL-MA"`), the province on Chile's communes (`"014"`), the state on US counties (`"US-SD"`) |
| `parentID` | string | The parent's feature `id`, ready to join | 16,063 features. Absent on ADM0, on `"unassigned"` features, and where no parent level is published — Guadeloupe's and Martinique's ADM4 and French Guiana's ADM3, whose territories have no ADM0 in the catalog |

Chile's commune Camiña carries all three at once: `adm1ISO` is its region
(`CL-TA`), `parentISO` its province (`014`) and `parentID` the province's id
(`CHL:ADM2:014`).

!!! note "`parentISO` and `adm1ISO` are not the same thing"

    On a Chilean commune, `parentISO` is its *province* — the immediate parent
    in the official hierarchy — while `adm1ISO` is its *region*, which is what
    the split file is keyed by. Where the previous published level *is* the
    ADM1 — US counties, Mexican municipios — the two coincide. Where a
    country has no ADM1, a municipal unit's `parentISO` is the ISO3 and there
    is no `adm1ISO` (`COL:ADM2:san-rafael` below).

## The feature `id`

Every feature carries a top-level GeoJSON `id` — a member of the Feature, not
a property — of the form `{ISO3}:{LEVEL}:{key}`, unique across the whole
repository. The key is chosen by one rule, implemented once in
`wgj finalize`:

1. **ADM0** → the ISO3: `ABW:ADM0:ABW`.
2. **`shapeISO`, when it is a real code and unique within the level**:
   `CHL:ADM3:01402`, `USA:ADM1:US-SD`, `CHL:ADM2:014`.
3. **Otherwise, below the first level when the country has an ADM1**:
   `{adm1ISO}.{slug(shapeName)}` — `USA:ADM2:US-SD.davison`,
   `BLZ:ADM2:BZ-SC.stann-creek-west`, `MEX:ADM2:MX-CMX.azcapotzalco`.
4. **Otherwise** `slug(shapeName)`: `COL:ADM2:san-rafael`, `PRI:ADM2:fajardo`,
   `GLP:ADM4:la-desirade`.
5. **Name collisions** get a deterministic numeric suffix, in order of the
   upstream id: `COL:ADM2:albania`, `COL:ADM2:albania-2`,
   `COL:ADM2:albania-3`.

Measured on the current data: 831 ids are keyed by a real code (every ADM0,
all 378 ADM1, Chile's 56 provinces and 345 communes), 12,780 by
`adm1.slug`, 2,584 by the slug alone, and 169 carry a numeric suffix (COL 84,
HND 28, SLV 18, ARG 16, GTM 6, USA 6, MEX 4, BLZ 2, BRA 2, VIR 2, SUR 1).

!!! warning "Suffixed ids are stable per data version — pin one"

    A suffix is assigned in upstream-id order, so `COL:ADM2:albania-2` stays
    `albania-2` for as long as the upstream vintage does. A refresh of the
    upstream can renumber them. Code-keyed ids do not have this problem. Pin
    a tagged data version in production and treat an upstream refresh as the
    breaking change it is — see
    [Versioning & stability](../about/versioning.md).

A key can be pinned by hand in `pipeline/src/wgj/tables/id_overrides.json` —
keyed by ISO3, level and the feature's `src_shape_id` (or `shapeISO` for
national sources), the value being the key part after `{ISO3}:{LEVEL}:`. It is
empty today: the `shapeISO` corrections resolved every known collision.
`wgj finalize` refuses to run while a collision remains and names the features,
so a new entry there is the way to resolve one.

Previews carry the same `id` as the full files, so a map drawn from a preview
joins to anything keyed on the full data.

## Property order

Properties are written in a fixed order: `shapeName`, `shapeISO`,
`shapeGroup`, `shapeType`, then `adm1ISO`, `parentISO` and `parentID` where
present, then the `src_*` fields. Files are canonical — one feature per line,
compact separators, coordinates at 6 decimals — and CI checks that re-running
the finalize step changes nothing. See
[Property schema → File layout](schema.md#file-layout).

## Worked examples

One feature per rule, exactly as stored (geometry omitted):

```json
{"type":"Feature","id":"CHL:ADM1:CL-CO","properties":{"shapeName":"Coquimbo","shapeISO":"CL-CO","shapeGroup":"CHL","shapeType":"ADM1","parentISO":"CHL","parentID":"CHL:ADM0:CHL","src_cut_reg":"04","src_superficie_km2":40587.8}}
{"type":"Feature","id":"CHL:ADM2:122","properties":{"shapeName":"Antártica Chilena","shapeISO":"122","shapeGroup":"CHL","shapeType":"ADM2","adm1ISO":"CL-MA","parentISO":"CL-MA","parentID":"CHL:ADM1:CL-MA","src_cut_prov":"122","src_cut_reg":"12","src_region":"Magallanes y de la Antártica Chilena"}}
{"type":"Feature","id":"CHL:ADM3:01402","properties":{"shapeName":"Camiña","shapeISO":"01402","shapeGroup":"CHL","shapeType":"ADM3","adm1ISO":"CL-TA","parentISO":"014","parentID":"CHL:ADM2:014","src_cut_com":"01402","src_cut_prov":"014","src_cut_reg":"01","src_provincia":"Tamarugal","src_region":"Tarapacá"}}
{"type":"Feature","id":"USA:ADM2:US-SD.davison","properties":{"shapeName":"Davison","shapeISO":"","shapeGroup":"USA","shapeType":"ADM2","adm1ISO":"US-SD","parentISO":"US-SD","parentID":"USA:ADM1:US-SD","src_shape_id":"52423323B35289781006587"}}
{"type":"Feature","id":"COL:ADM2:san-rafael","properties":{"shapeName":"San Rafael","shapeISO":"","shapeGroup":"COL","shapeType":"ADM2","parentISO":"COL","parentID":"COL:ADM0:COL","src_shape_id":"7082276B22021388124839"}}
{"type":"Feature","id":"GLP:ADM4:la-desirade","properties":{"shapeName":"La Désirade","shapeISO":"","shapeGroup":"GLP","shapeType":"ADM4","src_shape_id":"45945325B8612440900081"}}
```

Coquimbo is an ADM1: parent, no `adm1ISO`. Antártica Chilena and Camiña are
keyed by their CUT codes, and Camiña's parent is a province, not its region.
Davison has no code, so it is keyed by state and name. San Rafael's country has
no ADM1, so its parent is the ADM0. La Désirade has no parent level in the
catalog at all.

## Source properties — geoBoundaries

Every feature taken from geoBoundaries — ADM1 and below, 15,726 features today
— carries one extra field:

| Key | Type | Meaning |
|---|---|---|
| `src_shape_id` | string | geoBoundaries' own opaque identifier for the unit, e.g. `66186276B69138566591314`. Stable within a geoBoundaries release; not a territorial code. It is also the key under which `shapeiso_fixes.json` and `id_overrides.json` address a feature |

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

## History

!!! info "What v1.0.0 changed"

    On the unreleased 0.x `main`, 22 municipal datasets carried the opaque
    geoBoundaries id in `shapeISO`, the code was duplicated in BLZ ADM2, MEX
    ADM1 and ECU ADM1, `adm1ISO` existed only on split parts (plus Chile's
    combined ADM3), `parentISO` only in Chile, and no feature had an `id`.
    The finalize step introduced in v1.0.0 fixed all of it in one pass; the
    [Changelog](../about/changelog.md) has the list.

## Known traps

!!! danger "Territorial codes must be strings"

    A JSON number cannot hold a leading zero, so any source storing Chile's
    `01402` as an integer silently yields `1402`, and joins against official
    statistics match nothing. `shapeISO` and every `src_cut_*` field are
    strings.

!!! warning "`shapeISO` is empty where there is no code — join on `id`"

    Most municipal units have no ISO 3166-2 code and `shapeISO` is `""` on
    them. It is a correct join key for official statistics *where it is
    filled*; for identity use `id`, which every feature has and which is
    unique across the repository.

!!! note "Do not parse `id`"

    The key is readable on purpose, but `shapeISO`, `adm1ISO`, `parentISO` and
    `parentID` exist as separate fields precisely so you never have to take
    an `id` apart. Treat it as an opaque string when joining.

## Regenerating this page

Property lists are recorded per dataset in each
[`manifest.json`](manifest.md). This page is maintained by hand; generating it
from the manifests is on the [Roadmap](../about/roadmap.md).

--8<-- "abbreviations.md"
