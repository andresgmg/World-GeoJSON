# Registro de cambios

El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/). El
versionado sigue [Semantic Versioning](https://semver.org/lang/es/) adaptado a
datos según [Versionado y estabilidad](versioning.md).

## Sin publicar

### Añadido — pipeline de datos y Chile

- **Chile en `data/earth/CHL/`**, desde la *División Política Administrativa*
  2023 de IDE Chile bajo CC BY: 16 regiones, 56 provincias y 345 comunas. El
  nivel provincial no tenía fuente con licencia abierta hasta ahora.
- El nivel municipal va **partido por región** en 16 archivos para que ninguno
  sea inmanejable, más un archivo de país completo cuando cabe bajo el techo del
  CDN.
- Pipeline de ingesta: `fetch_sources.py`, `build_data.py`,
  `build_manifest.py`, `make_previews.mjs`, y un `scripts/countries.json` curado
  que registra qué nivel ADM es el tier municipal de cada país.
- Toda la geometría simplificada a una **tolerancia de 100 m sobre el terreno**,
  registrada por dataset en el manifiesto. Una distancia y no un porcentaje,
  para que todo el repositorio comparta una única resolución real.
- `validate-data.yml` — compara los manifiestos con una regeneración limpia,
  verifica que las partes sumen el total del nivel, aplica los presupuestos de
  tamaño y rechaza cualquier `source.license` fuera de la lista blanca
  permisiva.
- Mapas de preview interactivos, servidos desde el propio sitio para que
  funcionen con `mkdocs serve` y durante la revisión del PR, sin depender de la
  propagación del CDN.

### Cambiado

- **La fuente de Chile pasa de BCN a la DPA 2023 de IDE Chile.** geoBoundaries
  se evaluó y se descartó para Chile: su ADM2 es OpenStreetMap bajo ODbL y sus
  comunas son de 2020.
- **geoBoundaries deja de describirse como fuente CC BY 4.0.** `gbOpen` es un
  contenedor de licencias por archivo y el 33% de sus entradas de América son
  copyleft. `contributing/sources.md` estaba equivocada y se ha corregido.
- Natural Earth pasa a ser la fuente designada para los contornos de país.

### Obsoleto

- `regiones.geojson`, `comunas.geojson` y sus duplicados `.json` se mantienen en
  la raíz del repositorio, sin cambios, durante una versión mayor completa. No
  son equivalentes byte a byte a sus reemplazos — cambian fuente, esquema y
  resolución.

### Añadido — sitio de documentación

- Sitio de documentación construido con MkDocs y Material for MkDocs,
  desplegado en GitHub Pages.
- Convenciones escritas para estructura del repositorio, niveles
  administrativos, esquema de propiedades, sistemas de referencia de
  coordenadas y cuerpos planetarios.
- Lista de fuentes aprobadas y política de licencias, incluida la exclusión
  explícita de GADM y el problema de share-alike con OpenStreetMap.
- Política de fronteras disputadas.
- Código de conducta.
- Generador de catálogo (`scripts/gen_catalog.py`) que produce páginas de
  dataset desde los `manifest.json`.
- Workflow de CI que construye el sitio con `--strict` en los pull requests y
  despliega a GitHub Pages en `main`.

### Corregido

- `.gitattributes` ahora fija `*.geojson` a finales de línea LF. Antes,
  `* text=auto` provocaba conversión a CRLF al hacer checkout en Windows,
  dejando el archivo del working tree 1,8 MB más grande que el blob almacenado
  y produciendo checksums que no podían coincidir con el CI de Linux ni con
  `raw.githubusercontent.com`.

### Previsto — rompedor

Los archivos heredados de la raíz se retiran en la próxima versión mayor. Ver
[Versionado y estabilidad](versioning.md#los-archivos-heredados-de-la-raiz).

---

## [0.2.0] — 2023

### Añadido

- `comunas.geojson` — 343 comunas de Chile.
- `comunas.json` — duplicado byte a byte.

## [0.1.0] — 2023

### Añadido

- `regiones.geojson` — 16 regiones de Chile.
- `regiones.json` — duplicado byte a byte.
- Licencia MIT.

Fuente de ambos: Biblioteca del Congreso Nacional de Chile (BCN) / IDE Chile.

--8<-- "abbreviations.md"
