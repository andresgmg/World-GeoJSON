# Property dictionary

Every property key that appears anywhere in the corpus, what it means, and
whether it is standard.

## Standard properties

Defined by this project and present on every feature. See
[Property schema](schema.md).

| Key | Type | Meaning |
|---|---|---|
| `shapeName` | string | Local-language name, with diacritics |
| `shapeISO` | string | Official code — ISO 3166-2 where one exists, otherwise the national code |
| `shapeGroup` | string | ISO 3166-1 alpha-3 of the country, or body code |
| `shapeType` | string | `ADM0`–`ADM3` or `QUAD` |
| `parentISO` | string | `shapeISO` of the **immediate** parent unit |
| `adm1ISO` | string | ISO 3166-2 of the ADM1 the feature belongs to. Present on split municipal levels, where it names the file the feature lives in |
| `shapeID` | string | `{shapeGroup}-{shapeType}-{shapeISO}` |
| `shapeNameEn` | string | English exonym, where meaningfully different |

!!! note "`parentISO` and `adm1ISO` are not the same thing"

    On a Chilean commune, `parentISO` is its *province* — the immediate parent
    in the official hierarchy — while `adm1ISO` is its *region*, which is what
    the file is keyed by. Both are useful and both are recorded.

## Source properties — Chile

Preserved from IDE Chile's DPA 2023 under the `src_` prefix.

| Key | Type | Meaning |
|---|---|---|
| `src_cut_com` | string | CUT commune code, five characters, zero-padded |
| `src_cut_prov` | string | CUT province code, three characters |
| `src_cut_reg` | string | CUT region code, two characters |
| `src_provincia` | string | Province name |
| `src_region` | string | Region name |
| `src_superficie_km2` | number | Official area in **square kilometres** |

CUT (*Código Único Territorial*) is the national territorial coding scheme used
by INE and SUBDERE. Codes nest: commune `01402` sits in province `011`, which
sits in region `01`.

## Source properties — geoBoundaries

Countries taken from geoBoundaries carry its five native fields. Four of them
already match the standard vocabulary, which is why this project adopted it.

| Key | Note |
|---|---|
| `shapeName`, `shapeGroup`, `shapeType` | Used directly |
| `shapeISO` | **Frequently empty.** geoBoundaries documents it as "where available", and in practice many countries ship `""` |
| `shapeID` | An opaque internal identifier, not a territorial code |

## Properties that get dropped

Export artifacts from the source GIS software. They carry no information that
cannot be recomputed, and they mislead.

| Key | Why it goes |
|---|---|
| `objectid` | An Esri internal row number. Not stable across exports |
| `st_area_sh` | Precomputed area in square metres, from an unstated projection |
| `st_length_` | Precomputed perimeter, same problem |
| `shape_leng` | Duplicate of `st_length_`, truncated to the dBase 10-character field limit |

## Known traps

!!! danger "Territorial codes must be strings"

    A JSON number cannot hold a leading zero, so any source storing Chile's
    `01402` as an integer silently yields `1402`, and joins against official
    statistics match nothing. `shapeISO` and every `src_cut_*` field are
    strings.

!!! warning "`shapeISO` may be empty on geoBoundaries data"

    Do not assume it is populated. Use `shapeName` for display and `shapeID`
    for identity when the ISO code is missing.

!!! warning "The GeoJSON `id` member is not used"

    Identity lives in properties. Files in this repository do not rely on the
    top-level `id` member, and consumers should not either.

## Regenerating this page

Property lists are recorded per dataset in each
[`manifest.json`](manifest.md). This page is maintained by hand; generating it
from the manifests is on the [Roadmap](../about/roadmap.md).

--8<-- "abbreviations.md"
