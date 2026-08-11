# Property schema

Every feature carries a small set of standard properties, plus whatever the
upstream source provided.

## Required properties

| Property | Type | Meaning |
|---|---|---|
| `shapeName` | string | The unit's name, in the local language, with correct diacritics |
| `shapeISO` | string | Official code for the unit — ISO 3166-2 where one exists, otherwise the national code |
| `shapeGroup` | string | ISO 3166-1 alpha-3 of the containing country, or the body code |
| `shapeType` | string | `ADM0`, `ADM1`, `ADM2`, `ADM3` or `QUAD` |

These names match [geoBoundaries](https://www.geoboundaries.org/), deliberately.
Adopting an existing vocabulary means consumers who already handle
geoBoundaries data can read these files with no changes, and it removes an
entire category of bikeshedding from review.

## Optional properties

| Property | Type | Meaning |
|---|---|---|
| `shapeID` | string | Globally unique, stable identifier: `{shapeGroup}-{shapeType}-{shapeISO}` |
| `parentISO` | string | `shapeISO` of the parent unit, for nesting |
| `shapeNameEn` | string | English exonym, where it differs meaningfully |

## Source properties are preserved, not deleted

Upstream attributes are kept under a `src_` prefix:

```json
{
  "shapeName": "Camiña",
  "shapeISO": "01402",
  "shapeGroup": "CHL",
  "shapeType": "ADM3",
  "parentISO": "CL-TA",
  "src_cod_comuna": 1402,
  "src_codregion": 1,
  "src_provincia": "Iquique",
  "src_dis_elec": 2,
  "src_cir_sena": 2
}
```

The reasoning: information you discard is gone, and someone always needs the
field you decided was irrelevant. `dis_elec` and `cir_sena` are Chile's
electoral district and senatorial constituency — meaningless to most users,
essential to anyone doing electoral analysis. Namespacing keeps them without
letting them collide with the standard vocabulary.

## What gets dropped

Export artifacts from the source GIS software are the exception. These carry no
information that cannot be recomputed, and they are actively misleading:

| Property | Why it goes |
|---|---|
| `objectid` | An Esri internal row number. Not stable across exports, not meaningful. |
| `st_area_sh` | Precomputed area in **square metres**, from an unstated projection |
| `st_length_` | Precomputed perimeter, same problem |
| `shape_leng` | Duplicate of `st_length_`, truncated to the dBase 10-character field limit |
| `area_km` | Precomputed area in **square kilometres** |

!!! warning "The units are inconsistent today"

    `regiones.geojson` has `area_km` in km². `comunas.geojson` has
    `st_area_sh` in m². Neither file says so. Anyone comparing the two without
    reading the values carefully gets an answer off by a factor of a million.

    Compute area yourself from the geometry, in a projection appropriate to
    your area of interest — see
    [Recipes](../get-started/recipes.md#compute-area-correctly).

## Migration table for Chile

| Today | Becomes |
|---|---|
| `Region` | `shapeName` on ADM1; `parentISO` lookup on ADM3 |
| `Comuna` | `shapeName` on ADM3 |
| `Provincia` | `src_provincia` |
| `codregion` | `src_codregion`, and drives `shapeISO` on ADM1 |
| `cod_comuna` | `shapeISO`, **as a zero-padded string** |
| `objectid`, `st_area_sh`, `st_length_`, `shape_leng`, `area_km` | removed |

### The leading-zero problem

`cod_comuna` is currently stored as a JSON **number**. Camiña is `1402`. The
official INE/SUBDERE code is `01402` — a five-character string. Every commune in
regions 1 through 9 loses its leading zero this way, and any join against
official statistics silently matches nothing.

`shapeISO` is therefore **always a string**, never a number, even when it looks
numeric. This is not a stylistic preference: JSON numbers cannot represent a
leading zero at all.

## Feature-level `id`

The top-level GeoJSON `id` member is currently present on only **5 of 343**
commune features, with non-sequential values (`0`, `1`, `3`, `142`, `155`) that
do not correspond to position. Consumers keying off `feature.id` get
`undefined` 98.5% of the time. `regiones.geojson` has none at all, so the two
files are also inconsistent with each other.

The rule going forward: either every feature in a file has a stable, meaningful
`id`, or none does. Use `shapeID` in properties for identity; do not rely on
the GeoJSON `id` member.

## Names and encoding

- Files are UTF-8. `shapeName` **must** carry correct diacritics: `Región de
  Ñuble`, `Camiña`, `La Araucanía`.
- Use a plain ASCII apostrophe (`'`), not a typographic one. `Región del
  Libertador Bernardo O'Higgins` already does this; matching it matters for
  string comparison.
- Do not abbreviate. The existing `Región de Aysén del Gral.Ibañez del Campo`
  is wrong three ways — abbreviated "Gral.", missing space after the period,
  and missing the accent in "Ibáñez". Normalising it is part of the migration.

--8<-- "abbreviations.md"
