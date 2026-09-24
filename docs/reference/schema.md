# Property schema

Every feature carries a small set of standard properties, plus whatever the
upstream source provided.

## Required properties

| Property | Type | Meaning |
|---|---|---|
| `shapeName` | string | The unit's name, in the local language, with correct diacritics |
| `shapeISO` | string | Official code for the unit — ISO 3166-2 where one exists, otherwise the national code |
| `shapeGroup` | string | ISO 3166-1 alpha-3 of the containing country, or the body code |
| `shapeType` | string | `ADM0`, `ADM1`, `ADM2`, `ADM3`, `ADM4` or `QUAD` |

These names match [geoBoundaries](https://www.geoboundaries.org/), deliberately.
Adopting an existing vocabulary means consumers who already handle
geoBoundaries data can read these files with no changes, and it removes an
entire category of bikeshedding from review.

All four are present on every feature of every file under `data/`; CI checks
for them.

## Optional properties

| Property | Type | Meaning | Present today |
|---|---|---|---|
| `adm1ISO` | string | `shapeISO` of the ADM1 the feature belongs to | Every split part; Chile's combined ADM3 |
| `parentISO` | string | `shapeISO` of the immediate parent unit, for nesting | Chile ADM2 and ADM3 only |
| `src_shape_id` | string | geoBoundaries' opaque upstream identifier | Every geoBoundaries feature (ADM1 and below) |
| `src_*` | string or number | Other upstream attributes, namespaced | Chile: CUT codes, region and province names, official area |

The full list, with exactly which files carry what, is in the
[Property dictionary](properties.md).

!!! warning "Known issues (fixed in v1.0.0)"

    On 22 municipal datasets `shapeISO` holds geoBoundaries' opaque id rather
    than a territorial code, it is duplicated in BLZ ADM2, MEX ADM1 and ECU
    ADM1, and no feature has a Feature-level `id` yet. Do not rely on
    `shapeISO` as a unique key across the whole corpus until v1.0.0, which
    adds `id` = `{ISO3}:{LEVEL}:{code}`, `parentID` and `adm1ISO` on every
    feature. Details in the
    [Property dictionary](properties.md#known-issues-fixed-in-v100).

## Source properties are preserved, not deleted

Upstream attributes are kept under a `src_` prefix. This is Camiña, from
`data/earth/CHL/ADM3/CL-TA.geojson`, exactly as stored:

```json
{
  "shapeName": "Camiña",
  "shapeISO": "01402",
  "shapeGroup": "CHL",
  "shapeType": "ADM3",
  "parentISO": "014",
  "adm1ISO": "CL-TA",
  "src_cut_com": "01402",
  "src_cut_prov": "014",
  "src_cut_reg": "01",
  "src_provincia": "Tamarugal",
  "src_region": "Tarapacá"
}
```

The reasoning: information you discard is gone, and someone always needs the
field you decided was irrelevant. The CUT codes and the region and province
names let you aggregate communes to provinces or regions with a string match
rather than a spatial join. Namespacing keeps them without letting them collide
with the standard vocabulary — and a geoBoundaries `shapeID` becomes
`src_shape_id` for the same reason.

## What gets dropped

Export artifacts from the source GIS software are the exception. These carry no
information that cannot be recomputed, and they are actively misleading:

| Property | Why it goes |
|---|---|
| `objectid` | An Esri internal row number. Not stable across exports, not meaningful. |
| `st_area_sh` | Precomputed area in **square metres**, from an unstated projection |
| `st_length_` | Precomputed perimeter, same problem |
| `shape_leng` | Duplicate of `st_length_`, truncated to the dBase 10-character field limit |
| `area_km` | Precomputed area in **square kilometres** (legacy root files) |

!!! warning "Precomputed areas cannot be compared across sources"

    Different producers use different units and different projections for the
    same-sounding field, and rarely document either. Chile's DPA ships
    `SUPERFICIE` in km²; Esri exports ship `st_area_sh` in m². Compare them
    naively and the answer is off by a factor of a million.

    Where such a field is preserved it keeps a unit-bearing name
    (`src_superficie_km2`, on Chile's regions). For anything you rely on,
    compute area yourself from the geometry in a projection suited to your
    area of interest — see
    [Recipes](../get-started/recipes.md#compute-area-correctly).

## Worked example: Chile

Chile is built from IDE Chile's *División Política Administrativa* 2023, whose
attributes map cleanly onto the standard set:

| Source field | Becomes |
|---|---|
| `REGION` | `shapeName` on ADM1; `src_region` on ADM2 and ADM3 |
| `PROVINCIA` | `shapeName` on ADM2; `src_provincia` on ADM3 |
| `COMUNA` | `shapeName` on ADM3 |
| `CUT_REG` | `shapeISO` on ADM1 via the ISO 3166-2 lookup (`01` → `CL-TA`); `src_cut_reg` on ADM1, ADM2 and ADM3 |
| `CUT_PROV` | `shapeISO` on ADM2, `parentISO` on ADM3; `src_cut_prov` on both |
| `CUT_COM` | `shapeISO` on ADM3; `src_cut_com` |
| `SUPERFICIE` | `src_superficie_km2` on ADM1 |

Region names come through **without** the "Región de" prefix: `Ñuble`,
`Tarapacá`, `Libertador General Bernardo O'Higgins`. A region therefore looks
like:

```json
{
  "shapeName": "Coquimbo",
  "shapeISO": "CL-CO",
  "shapeGroup": "CHL",
  "shapeType": "ADM1",
  "src_cut_reg": "04",
  "src_superficie_km2": 40587.8
}
```

and a commune like the Camiña example above.

### `shapeISO` is always a string

The official INE/SUBDERE code for Camiña is `01402` — five characters, leading
zero included. Every commune in regions 1 through 9 has one.

A JSON **number** cannot represent a leading zero at all, so a source that
stores these as integers silently turns `01402` into `1402`, and any join
against official statistics then matches nothing. The DPA shapefile already
stores CUT codes as strings, which is one of the reasons it was chosen over
alternatives.

`shapeISO` is therefore always a string, never a number, even when it looks
numeric.

!!! note "Codes here are national, not ISO 3166-2"

    Chile has ISO 3166-2 codes for its regions (`CL-TA`) but not for provinces
    or communes, so those levels carry the national CUT code instead: the
    three-digit province code on ADM2 (`014`), the five-digit commune code on
    ADM3 (`01402`). That is the documented fallback: ISO 3166-2 where it
    exists, the national code otherwise.

## Feature-level `id`

No file under `data/` sets the top-level GeoJSON `id` member today.

The legacy root `comunas.geojson` is the cautionary tale: it carries `id` on
only **5 of 343** commune features, with non-sequential values (`0`, `1`, `3`,
`142`, `155`) that do not correspond to position, so a consumer keying off
`feature.id` gets `undefined` 98.5% of the time — and `regiones.geojson` has
none at all.

The rule: either every feature in a file has a stable, meaningful `id`, or
none does. v1.0.0 gives every feature `id` = `{ISO3}:{LEVEL}:{code}`. Until
then, identity lives in properties: `shapeISO` where it is a real code, and
`src_shape_id` on geoBoundaries data where it is not.

## Names and encoding

- Files are UTF-8. `shapeName` **must** carry correct diacritics: `Ñuble`,
  `Camiña`, `La Araucanía`.
- Use a plain ASCII apostrophe (`'`), not a typographic one. `Libertador
  General Bernardo O'Higgins` does this; matching it matters for string
  comparison.
- Do not abbreviate. The legacy root `regiones.geojson` has `Región de Aysén
  del Gral.Ibañez del Campo` — wrong three ways: abbreviated "Gral.", no space
  after the period, and no accent in "Ibáñez". The current data carries
  `Aysén del General Carlos Ibáñez del Campo`, as the DPA publishes it.

--8<-- "abbreviations.md"
