# Reference

These pages define how data in this repository is organised. They are the
contract: a contribution that follows them can be merged; one that does not
cannot, no matter how good the underlying geometry is.

They exist because the project is scaling from one country to potentially two
hundred. Two files with ad-hoc property names are merely untidy; four hundred
files with ad-hoc property names are unusable.

## At a glance

| Question | Answer | Detail |
|---|---|---|
| Where does a file go? | `data/{body}/{ISO3}/{ISO3}_{LEVEL}.geojson` | [Naming](naming.md) |
| What is ADM1? | First-level divisions, whatever they are called locally | [Admin levels](admin-levels.md) |
| What properties must a feature have? | `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` | [Schema](schema.md) |
| What coordinate system? | OGC:CRS84 (≡ EPSG:4326), longitude first | [CRS](crs.md) |
| May a file declare its own CRS? | **No.** RFC 7946 removed that member | [CRS](crs.md#the-crs-member-is-forbidden) |
| How do the Moon and Mars work? | IAU 2015 body-fixed frames, no ISO codes | [Planetary](planetary.md) |
| Where does catalog metadata come from? | `manifest.json` beside the data | [Manifest](manifest.md) |

## Conformance language

These pages use **must**, **should** and **may** in the
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) sense. "Must" is enforced in
review and, where practical, in CI.

## Current state versus target state

Honesty matters more than tidiness here: **the existing Chile data does not yet
follow these conventions.** It predates them.

| Convention | Chile today | Target |
|---|---|---|
| Location | `comunas.geojson` at repo root | `data/earth/CHL/CHL_ADM3.geojson` |
| Name property | `Comuna` | `shapeName` |
| Code property | `cod_comuna` (integer, `1402`) | `shapeISO` (string, `01402`) |
| Esri artifacts | `objectid`, `st_area_sh`, `st_length_` | removed |
| `bbox` member | absent | present |
| Coordinate precision | ~14 decimals | 6 decimals |

Each page marks the gap between the two. Migration is a deliberate breaking
change with a deprecation window — see
[Versioning & stability](../about/versioning.md).

--8<-- "abbreviations.md"
