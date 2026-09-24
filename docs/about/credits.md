# Credits

## Data sources

Everything under `data/` comes from one of three sources. Which one, and under
which licence, is recorded per dataset in the manifest's `license` and
`src_provider` fields — see [Licensing & attribution](license.md).

- **[Natural Earth](https://www.naturalearthdata.com/)** — the 10m Admin 0
  country outlines used for **every ADM0** in the repository. Public domain,
  maintained by volunteers with support from NACIS.
- **[geoBoundaries](https://www.geoboundaries.org/)** (William & Mary geoLab)
  — the first-level and municipal tiers for every country except Chile.
  geoBoundaries' `gbOpen` release is not a single licence: each file carries
  the licence of its original provider (a national statistics office, a UN
  agency, Wikimedia, …), and this project takes only the permissive subset —
  CC BY 2.5, CC BY 3.0 IGO, CC BY 4.0, Etalab 2.0, OGL Canada 2.0 and public
  domain today. The original provider is credited in each dataset's
  `src_provider`. This project's property vocabulary (`shapeName`, `shapeISO`,
  `shapeGroup`, `shapeType`) deliberately matches theirs, so data can move
  between the two without translation.
- **[IDE Chile / SUBDERE](https://www.geoportal.cl/)** — the *División
  Política Administrativa* 2023, under CC BY 4.0, for Chile's regions,
  provinces and communes.

### Legacy files

**[Biblioteca del Congreso Nacional de Chile (BCN)](https://www.bcn.cl/siit/mapas_vectoriales)**
— the regional and communal boundaries this project started from in 2023,
including the electoral district and senatorial constituency attributes that
come with them. They survive only as the deprecated `regiones.geojson` and
`comunas.geojson` at the repository root; nothing under `data/` derives from
them.

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
  is what lets the manifest scanner read the largest files in constant memory.
- **[USGS Astrogeology](https://astrogeology.usgs.gov/)** — planetary
  basemaps.

## Contributors

Maintained by Andres Marquez ([@andresgmg](https://github.com/andresgmg)).

See the
[contributors list](https://github.com/andresgmg/World-GeoJSON/graphs/contributors)
on GitHub. If you have contributed and are not listed correctly, please open an
issue.

--8<-- "abbreviations.md"
