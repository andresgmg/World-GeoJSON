# Coordinate reference systems

## The rule

All Earth data in this repository is **OGC:CRS84** — longitude and latitude in
decimal degrees on the WGS 84 datum. This is numerically identical to
EPSG:4326 with the axis order that GeoJSON mandates.

```json
"coordinates": [-70.6483, -33.4569]
```

**Longitude first.** EPSG:4326 formally defines latitude first; GeoJSON
overrides this. Reversing the pair is the single most common error in
hand-edited GeoJSON, and it fails quietly — the geometry renders, just in the
wrong hemisphere.

## The `crs` member is forbidden

RFC 7946 §4 states that all GeoJSON coordinates are in WGS 84, and the
specification **removed** the `crs` member that the 2008 draft allowed. A
conforming file cannot declare its coordinate system, because there is only one
permitted answer.

So: no file in this repository contains a `crs` member. The authoritative
declaration lives out of band, in the dataset's
[`manifest.json`](manifest.md):

```json
"crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 }
```

That field exists because it is genuinely load-bearing for planetary data,
where the coordinates are *not* WGS 84 and the file cannot say so. See
[Planetary bodies](planetary.md).

## Coordinate precision

Coordinates **must not** exceed **6 decimal places** — approximately 11 cm at
the equator.

The current Chile files store around **14** decimal places
(`-68.95020116247055`). That is nanometre precision on boundaries surveyed to,
at best, metre accuracy. It is not more accurate; it is the same accuracy with
eight digits of noise attached, and those digits occupy real bytes in a 70 MB
file.

| Decimals | Precision at equator |
|---|---|
| 3 | 110 m |
| 4 | 11 m |
| 5 | 1.1 m |
| 6 | 11 cm |

Six is generous for administrative boundaries. Previews use four.

## The `bbox` member

Every `FeatureCollection` **should** carry a top-level `bbox`:

```json
"bbox": [-109.4548, -56.5333, -66.4177, -17.4983]
```

Order is `[west, south, east, north]`. It lets a consumer decide whether to
download the file at all, and lets a map fit its view without parsing the whole
geometry.

Neither current Chile file has one. Adding them is part of the migration.

## Winding order

RFC 7946 §3.1.6 requires the right-hand rule: exterior rings counterclockwise,
interior rings (holes) clockwise. Many tools ignore this on read, but some —
notably several vector-tile pipelines and MongoDB's geospatial indexes — do
not, and will treat a wrongly-wound polygon as covering the entire planet minus
your shape.

`mapshaper` rewinds correctly on output. Verify rather than assume.

## The antimeridian

RFC 7946 §3.1.9: geometries crossing 180° longitude **should** be cut in two at
the antimeridian rather than using coordinates outside the −180…180 range.

This is not hypothetical for Chile:

- **Isla de Pascua** sits at about 109°W — well inside range, but far enough
  from the mainland that a naive bounding box spans a third of the planet.
- **The Chilean Antarctic Territory** extends to the South Pole. Polygons that
  include a pole are a known failure mode for renderers and for
  point-in-polygon tests, quite separately from the antimeridian question.

Any dataset including polar or antimeridian-crossing geometry **must** note it
in the manifest so consumers are not surprised.

## Reprojection

Do not compute areas or distances in degrees. A degree of longitude is 111 km
at the equator and 0 at the poles; area in "square degrees" is not a quantity.

Reproject to something appropriate for your area of interest first — for Chile,
EPSG:5361 (SIRGAS-Chile). See
[Recipes](../get-started/recipes.md#compute-area-correctly).

Data **must** be stored in CRS84 regardless. Reprojection is the consumer's
job; storing anything else would make the files non-conforming.

--8<-- "abbreviations.md"
