# Créditos

## Fuentes de datos

Todo lo que hay bajo `data/` procede de una de tres fuentes. Cuál, y bajo qué
licencia, se registra por dataset en los campos `license` y `src_provider` del
manifiesto — ver [Licencias y atribución](license.md).

- **[Natural Earth](https://www.naturalearthdata.com/)** — los contornos de
  país Admin 0 a escala 10m usados para **todos los ADM0** del repositorio.
  Dominio público, mantenidos por voluntarios con apoyo de NACIS.
- **[geoBoundaries](https://www.geoboundaries.org/)** (geoLab, William & Mary)
  — el primer nivel y el tier municipal de todos los países salvo Chile. La
  release `gbOpen` de geoBoundaries no es una licencia única: cada archivo
  lleva la licencia de su proveedor original (un instituto nacional de
  estadística, una agencia de la ONU, Wikimedia, …), y este proyecto toma solo
  el subconjunto permisivo — CC BY 2.5, CC BY 3.0 IGO, CC BY 4.0, Etalab 2.0,
  OGL Canada 2.0 y dominio público hoy. El proveedor original se acredita en
  el `src_provider` de cada dataset. El vocabulario de propiedades de este
  proyecto (`shapeName`, `shapeISO`, `shapeGroup`, `shapeType`) coincide con
  el suyo deliberadamente, para que los datos se puedan mover entre ambos sin
  traducción.
- **[IDE Chile / SUBDERE](https://www.geoportal.cl/)** — la *División
  Política Administrativa* 2023, bajo CC BY 4.0, para las regiones, provincias
  y comunas de Chile.

### Archivos heredados

**[Biblioteca del Congreso Nacional de Chile (BCN)](https://www.bcn.cl/siit/mapas_vectoriales)**
— los límites regionales y comunales con los que empezó este proyecto en 2023,
incluidos los atributos de distrito electoral y circunscripción senatorial que
vienen con ellos. Sobreviven solo como los obsoletos `regiones.geojson` y
`comunas.geojson` en la raíz del repositorio; nada bajo `data/` deriva de
ellos.

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
  es lo que permite al escáner de manifiestos leer los archivos más grandes en
  memoria constante.
- **[USGS Astrogeology](https://astrogeology.usgs.gov/)** — mapas base
  planetarios.

## Contribuyentes

Mantenido por Andres Marquez ([@andresgmg](https://github.com/andresgmg)).

Ver la
[lista de contribuyentes](https://github.com/andresgmg/World-GeoJSON/graphs/contributors)
en GitHub. Si has contribuido y no apareces correctamente, abre un issue.

--8<-- "abbreviations.md"
