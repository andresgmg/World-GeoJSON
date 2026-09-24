# Property schema

Every feature carries a small set of standard properties, plus whatever the
upstream source provided.

## Required properties

| Property | Type | Meaning |
|---|---|---|
| `shapeName` | string | The unit's name, in the local language, with correct diacritics |
| `shapeISO` | string | Official code for the unit — ISO 3166-2 where one exists, otherwise the national code; `""` when the upstream has none |
| `shapeGroup` | string | ISO 3166-1 alpha-3 of the containing country, or the body code |
| `shapeType` | string | `ADM0`, `ADM1`, `ADM2`, `ADM3`, `ADM4` or `QUAD` |

These names match [geoBoundaries](https://www.geoboundaries.org/), deliberately.
Adopting an existing vocabulary means consumers who already handle
geoBoundaries data can read these files with no changes, and it removes an
entire category of bikeshedding from review.

All four are present on every feature of every file under `data/`; CI
validates every feature against the JSON Schema that says so
([`feature-properties.schema.json`](#json-schemas)). `shapeISO` is `""` on
most municipal units — geoBoundaries has no code for them — and is never an
opaque upstream id; where it is non-empty it is unique within its level.

## Optional properties

| Property | Type | Meaning | Present on |
|---|---|---|---|
| `adm1ISO` | string | Key of the ADM1 the feature belongs to | Every feature below ADM1 when the country publishes an ADM1, combined files included; `"unassigned"` where no parent could be determined |
| `parentISO` | string | Key of the parent at the previous published level | Every feature that has a parent level in the catalog — ADM1 (the ISO3) and below |
| `parentID` | string | The parent's feature `id` | The same, except `"unassigned"` features |
| `src_shape_id` | string | geoBoundaries' opaque upstream identifier | Every geoBoundaries feature (ADM1 and below) |
| `src_*` | string or number | Other upstream attributes, namespaced | Chile: CUT codes, region and province names, official area |

No other property is allowed: the schema sets `additionalProperties: false`,
so a file with a stray key fails CI. The full presence rules, with counts, are
in the [Property dictionary](properties.md#hierarchy-properties).

!!! tip "Join on `id`, nest on `parentID`"

    Every feature has a Feature-level `id` (below) and every sub-national
    feature names its parent's id in `parentID`, in every country. `shapeISO`
    is the key for joining *official statistics* where a code exists; `id` is
    the key for everything else.

## Source properties are preserved, not deleted

Upstream attributes are kept under a `src_` prefix. This is Camiña, from
`data/earth/CHL/ADM3/CL-TA.geojson` — feature `id` `CHL:ADM3:01402` — with
its properties exactly as stored, in the order they are stored:

```json
{
  "shapeName": "Camiña",
  "shapeISO": "01402",
  "shapeGroup": "CHL",
  "shapeType": "ADM3",
  "adm1ISO": "CL-TA",
  "parentISO": "014",
  "parentID": "CHL:ADM2:014",
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
  "parentISO": "CHL",
  "parentID": "CHL:ADM0:CHL",
  "src_cut_reg": "04",
  "src_superficie_km2": 40587.8
}
```

— feature `id` `CHL:ADM1:CL-CO`, parent the country outline — and a commune
like the Camiña example above.

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

Every feature in every file under `data/` — previews included — sets the
top-level GeoJSON `id` member: `{ISO3}:{LEVEL}:{key}`, unique across the
repository.

```json
{"type":"Feature","id":"CHL:ADM3:01402","properties":{…},"geometry":{…}}
```

The key is the `shapeISO` when that is a real, unique code (`CHL:ADM3:01402`,
`USA:ADM1:US-SD`) and a name-based key otherwise (`USA:ADM2:US-SD.davison`,
`COL:ADM2:san-rafael`). The full five-step rule, the measured split between the
two, the numeric-suffix behaviour on name collisions and its stability caveat,
and the `pipeline/src/wgj/tables/id_overrides.json` registry are documented
once, in
[Property dictionary → The feature `id`](properties.md#the-feature-id).

The rule behind it: either every feature in a file has a stable, meaningful
`id`, or none does. The legacy root `comunas.geojson` is the cautionary tale —
it carries `id` on only **5 of 343** commune features, with values (`0`, `1`,
`3`, `142`, `155`) that correspond to nothing, so a consumer keying off
`feature.id` got `undefined` 98.5% of the time. That is why the contract makes
`id` mandatory: [`feature.schema.json`](#json-schemas) lists it under
`required`, and CI validates every feature against it.

## File layout

Every full-resolution file is written by `wgj finalize` in one
canonical form, so that the same data always produces the same bytes:

```
{"type":"FeatureCollection","bbox":[west,south,east,north],"features":[
{"type":"Feature","id":"CHL:ADM1:CL-CO","properties":{…},"geometry":{…}},
{"type":"Feature","id":"CHL:ADM1:CL-NB","properties":{…},"geometry":{…}},
…
]}
```

- the collection header and its `bbox` on the first line, then **one feature
  per line** — `grep`, `head` and streaming parsers work;
- compact separators, no pretty-printing;
- coordinates with at most **6 decimals** (4 in previews), no exponents, no
  trailing zeros;
- `bbox` recomputed from the coordinates, so it always matches the geometry;
- properties in the [fixed order](properties.md#property-order).

Running the finalize step twice is a no-op, and CI runs it with `--check` to
make sure every committed file is in this form. Previews use the same layout
and carry the same `id`, with only `shapeName`, `shapeISO` and `shapeType`.

## JSON Schemas

The contract on this page is machine-readable. Two schemas, JSON Schema
2020-12, in `schemas/` and served from this site:

| Schema | Validates | Published at |
|---|---|---|
| `feature.schema.json` | One Feature: `type`, a required `id` matching `^[A-Z]{3}:(ADM[0-4]\|QUAD):\S+$`, `properties` (by reference to the next schema), a `Polygon` or `MultiPolygon` geometry | <https://andresgmg.github.io/World-GeoJSON/schemas/feature.schema.json> |
| `feature-properties.schema.json` | The `properties` object: the four required keys, the three hierarchy keys, `src_*` by pattern, nothing else | <https://andresgmg.github.io/World-GeoJSON/schemas/feature-properties.schema.json> |

`wgj validate` applies them to every feature of every
full-resolution file in CI. The manifest, index and registry schemas are on
[Global index & schemas](index-json.md#schemas).

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
