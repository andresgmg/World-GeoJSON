# Planetary bodies

The Moon and Mars break almost every assumption the rest of this reference
makes. This page states exactly how, because getting it wrong produces data
that looks fine and is silently, systematically displaced.

## The core problem

[RFC 7946 §4](https://www.rfc-editor.org/rfc/rfc7946#section-4) says GeoJSON
coordinates are WGS 84 — a datum defined by an ellipsoid fitted to Earth — and
removed the `crs` member that would let a file say otherwise.

Mars is not Earth. Its coordinates are not WGS 84 and cannot be. But a
conforming GeoJSON file has no way to say so.

!!! danger "Planetary files here are RFC 7946-*shaped*, not RFC 7946-*conformant*"

    This is a deliberate, documented deviation from the standard, not an
    oversight.

    A Mars file in this repository is syntactically valid GeoJSON that any
    parser will read. Its coordinates are degrees. But they are degrees on
    Mars, and **the file itself cannot tell you that**. A consumer that assumes
    WGS 84 — which the specification entitles it to do — will place Olympus
    Mons somewhere in the Pacific.

    The authoritative CRS declaration therefore lives in
    [`manifest.json`](manifest.md), and reading it is **mandatory** before
    using planetary data. There is no in-band alternative.

## Coordinate reference systems

Planetary coordinates use body-fixed frames from the IAU/IAG Working Group on
Cartographic Coordinates and Rotational Elements, whose 2015 report is the
current reference. These are registered in PROJ under the `IAU_2015` authority.

| Body | Frame | Reference radius |
|---|---|---|
| Moon | `IAU_2015:30100` | 1 737 400 m (sphere) |
| Mars | `IAU_2015:49900` | 3 396 190 m equatorial |

In a manifest:

```json
"crs": {
  "authority": "IAU_2015",
  "code": "49900",
  "body": "mars",
  "proj": "+proj=longlat +R=3396190 +no_defs",
  "note": "Planetocentric latitude, east-positive longitude, -180..180"
}
```

The `proj` string is included so consumers can hand it directly to GDAL, PROJ,
`pyproj` or `rasterio` without looking anything up.

## The two errors everyone makes

### Planetocentric versus planetographic latitude

Two different definitions of "latitude" are in active use for Mars:

- **Planetocentric** — the angle at the body's centre. What this project uses.
- **Planetographic** — the angle of the surface normal to the equatorial plane.

On a perfect sphere they are identical. Mars is oblate enough that they diverge
by **up to about 0.3°**, which is roughly 18 km at the equator. That is large
enough to put a feature in the wrong crater and small enough that nothing looks
obviously broken.

**This project stores planetocentric latitude.** Datasets that arrive
planetographic must be converted before merging, and the manifest records which
convention applies.

### East-positive versus west-positive longitude

Historical Mars maps used west-positive longitude. Modern practice, and the IAU
recommendation for Mars, is **east-positive**. Lunar data is east-positive too.

Mixing the two mirrors your map about the prime meridian. Because many
planetary features are roughly symmetric in distribution, this often does not
look wrong at a glance.

**This project stores east-positive longitude in the −180…180 domain**, for
consistency with the Earth data and because most web mapping libraries assume
it. Sources using the 0…360 domain must be converted.

## There is no ISO 3166 for other worlds

No registry of "countries" exists for the Moon or Mars, and under the Outer
Space Treaty none is likely to. So the naming convention substitutes:

- **Body code** in place of a country code — `MOON`, `MARS`. These are chosen
  to be four characters so they can never collide with a three-character ISO
  3166-1 alpha-3, present or future.
- **`QUAD`** in place of an admin level, for the USGS quadrangle schemes that
  are the closest thing to a systematic subdivision of a planetary surface.
- **Feature names** from the
  [IAU Gazetteer of Planetary Nomenclature](https://planetarynames.wr.usgs.gov/),
  which is the authoritative registry of approved names for surface features.
  Do not invent names, and do not use informal mission nicknames.

```
data/moon/MOON/MOON_QUAD.geojson
data/mars/MARS/MARS_QUAD.geojson
```

`shapeGroup` carries the body code; `shapeType` is `QUAD`.

## Basemaps

There are no Web Mercator tile services for planetary bodies. USGS Astrogeology
publishes equirectangular WMS endpoints, so preview maps for these bodies use
`EPSG:4326`-style plate carrée rather than the Web Mercator that the Earth maps
use.

This is why `geojson-map.js` reads a `data-body` attribute: it selects both the
basemap and the map projection from it.

## Status

**Nothing planetary has been added yet.** This page is written first, on
purpose. The conventions above are the ones that are expensive to change once
files exist — particularly the latitude convention, which cannot be detected
from the data itself after the fact.

--8<-- "abbreviations.md"
