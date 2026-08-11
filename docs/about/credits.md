# Credits

## Data sources

**[Biblioteca del Congreso Nacional de Chile (BCN) / IDE Chile](https://www.bcn.cl/siit/mapas_vectoriales)**
— the regional and communal boundaries this project started from, including the
electoral district and senatorial constituency attributes that come with them.

## Recommended sources

Not used yet, but the ones this project expects to build on. Both are models of
how open geographic data should be published:

- **[geoBoundaries](https://www.geoboundaries.org/)** (William & Mary geoLab)
  — open ADM0–ADM3 boundaries for every country under CC BY 4.0. This
  project's property vocabulary (`shapeName`, `shapeISO`, `shapeGroup`,
  `shapeType`) deliberately matches theirs, so data can move between the two
  without translation.
- **[Natural Earth](https://www.naturalearthdata.com/)** — public domain
  small-scale vector data, maintained by volunteers with support from NACIS.

## Standards

- **[RFC 7946](https://www.rfc-editor.org/rfc/rfc7946)** — the GeoJSON format,
  IETF.
- **ISO 3166** — country and subdivision codes.
- **[UN M49](https://unstats.un.org/unsd/methodology/m49/)** — the regional
  groupings used to organise the catalog.
- **IAU/IAG Working Group on Cartographic Coordinates and Rotational Elements**
  — the 2015 report defining the planetary reference frames used for the Moon
  and Mars.
- **[IAU Gazetteer of Planetary Nomenclature](https://planetarynames.wr.usgs.gov/)**
  (USGS Astrogeology) — the authoritative registry of approved surface feature
  names.

## Tools

- **[MkDocs](https://www.mkdocs.org/)** and
  **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)** —
  this site.
- **[mapshaper](https://github.com/mbloch/mapshaper)** (Matthew Bloch) — the
  simplification and conversion workhorse. Its topology-preserving
  simplification is what makes usable previews possible at all.
- **[GDAL/OGR](https://gdal.org/)** — format conversion and reprojection.
- **[Leaflet](https://leafletjs.com/)** — the preview maps.
- **[ijson](https://github.com/ICRAR/ijson)** — streaming JSON parsing, which
  is what lets a 70 MB file be scanned in constant memory.
- **[USGS Astrogeology](https://astrogeology.usgs.gov/)** — planetary
  basemaps.

## Contributors

Maintained by Andres Marquez ([@andresgmg](https://github.com/andresgmg)).

See the
[contributors list](https://github.com/andresgmg/World-GeoJSON/graphs/contributors)
on GitHub. If you have contributed and are not listed correctly, please open an
issue.

--8<-- "abbreviations.md"
