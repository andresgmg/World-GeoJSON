# Créditos

## Fuentes de datos

**[Biblioteca del Congreso Nacional de Chile (BCN) / IDE Chile](https://www.bcn.cl/siit/mapas_vectoriales)**
— los límites regionales y comunales con los que empezó este proyecto,
incluidos los atributos de distrito electoral y circunscripción senatorial que
vienen con ellos.

## Fuentes recomendadas

Aún no utilizadas, pero sobre las que este proyecto espera construir. Ambas son
modelos de cómo deberían publicarse los datos geográficos abiertos:

- **[geoBoundaries](https://www.geoboundaries.org/)** (geoLab, William & Mary)
  — límites ADM0–ADM3 abiertos para todos los países, bajo CC BY 4.0. El
  vocabulario de propiedades de este proyecto (`shapeName`, `shapeISO`,
  `shapeGroup`, `shapeType`) coincide con el suyo deliberadamente, para que los
  datos se puedan mover entre ambos sin traducción.
- **[Natural Earth](https://www.naturalearthdata.com/)** — datos vectoriales de
  escala pequeña en dominio público, mantenidos por voluntarios con apoyo de
  NACIS.

## Estándares

- **[RFC 7946](https://www.rfc-editor.org/rfc/rfc7946)** — el formato GeoJSON,
  IETF.
- **ISO 3166** — códigos de país y de subdivisión.
- **[UN M49](https://unstats.un.org/unsd/methodology/m49/)** — las agrupaciones
  regionales con las que se organiza el catálogo.
- **Grupo de trabajo IAU/IAG sobre coordenadas cartográficas y elementos de
  rotación** — el informe de 2015 que define los marcos de referencia
  planetarios usados para la Luna y Marte.
- **[IAU Gazetteer of Planetary Nomenclature](https://planetarynames.wr.usgs.gov/)**
  (USGS Astrogeology) — el registro autoritativo de nombres aprobados para
  accidentes superficiales.

## Herramientas

- **[MkDocs](https://www.mkdocs.org/)** y
  **[Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)** —
  este sitio.
- **[mapshaper](https://github.com/mbloch/mapshaper)** (Matthew Bloch) — el
  caballo de batalla de la simplificación y la conversión. Su simplificación
  con preservación de topología es lo que hace posibles previews utilizables.
- **[GDAL/OGR](https://gdal.org/)** — conversión de formatos y reproyección.
- **[Leaflet](https://leafletjs.com/)** — los mapas de preview.
- **[ijson](https://github.com/ICRAR/ijson)** — parseo JSON en streaming, que
  es lo que permite escanear un archivo de 70 MB en memoria constante.
- **[USGS Astrogeology](https://astrogeology.usgs.gov/)** — mapas base
  planetarios.

## Contribuyentes

Mantenido por Andres Marquez ([@andresgmg](https://github.com/andresgmg)).

Ver la
[lista de contribuyentes](https://github.com/andresgmg/World-GeoJSON/graphs/contributors)
en GitHub. Si has contribuido y no apareces correctamente, abre un issue.

--8<-- "abbreviations.md"
