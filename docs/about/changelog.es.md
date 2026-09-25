# Registro de cambios

El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/). El
versionado sigue [Semantic Versioning](https://semver.org/lang/es/) adaptado a
datos según [Versionado y estabilidad](versioning.md).

## Sin publicar

### Añadido — bibliotecas cliente

- **`geoworld` para Python** (`packages/python/geoworld`, PyPI): un cliente
  ligero sin dependencias. `GeoWorld("1.0.0")` lee `data/index.json` de una
  release de datos fijada, descarga archivos bajo demanda, los cachea en el
  directorio de caché de la plataforma y verifica cada `sha256` contra el
  índice; `get`, `get_part`, `iter_parts`, `preview`, `find`, `parent`,
  `children`, `search`, `url`, `bbox` y, con el extra `geopandas`,
  `to_geopandas`.
- **`geoworld` para JavaScript/TypeScript** (`packages/js/geoworld`, npm): la
  misma API, `async`, ESM y CommonJS, sin dependencias, sobre `fetch` y Web
  Crypto (Node ≥ 20, navegadores). `geoworld/node` añade una caché en disco
  con la misma disposición que la del cliente Python.
- `fixtures/expected/fixtures.json`: un golden que ambos clientes deben
  reproducir byte a byte, comprobado en CI, para que no puedan divergir.
- Workflows `publish-python.yml` (etiqueta `python-vX.Y.Z`, trusted
  publishing en PyPI) y `publish-js.yml` (etiqueta `js-vX.Y.Z`, npm con
  procedencia), y un job `js-client` en `ci.yml` (Node 20 y 22).
- Documentación: [Bibliotecas cliente](../libraries/index.md),
  [Python](../libraries/python.md), [JavaScript](../libraries/javascript.md).

### Añadido — paquete del pipeline

- **El comando `wgj`.** El pipeline es ahora un paquete Python instalable,
  `wgj` bajo `pipeline/` — `pip install -r requirements-dev.txt`, o
  `pip install -e ./pipeline[pipeline]` a secas — con un subcomando por paso:
  `wgj fetch`, `wgj build`, `wgj finalize`, `wgj previews`, `wgj manifest`,
  `wgj index` y `wgj validate`, cada uno con `--help`; `python -m wgj` es lo
  mismo. Documentado en [Pipeline de datos](../contributing/pipeline.md).
- `wgj all CHL`: build → previews → manifiesto → índice → validación para los
  países indicados, deteniéndose en el primer fallo.
- `fixtures/data/`: tres territorios pequeños — Aruba, Barbados y una
  República Dominicana reducida — con su `index.json`. La suite de tests
  corre sobre ellos (`pytest` desde la raíz del repositorio, sin necesidad de
  un checkout de los datos; `WGJ_DATA=<dir>` apunta el paquete a otro árbol),
  y las bibliotecas cliente los usarán más adelante.

### Cambiado

- `scripts/*.py` son ahora shims de compatibilidad de diez líneas que llaman
  al paquete. Se quedan durante una release y se retiran en la Fase 4 de la
  [Hoja de ruta](roadmap.md); a partir de ahora escribe `wgj`.
- `scripts/make_previews.mjs` se elimina: `wgj previews` (Python) genera los
  previews, ejecutando mapshaper vía Node como antes, y `npm run previews`
  ahora lo invoca.
- Los registros se mudan al paquete: `pipeline/src/wgj/tables/` contiene
  `countries.json`, `shapeiso_fixes.json`, `id_overrides.json` e
  `iso3166_2.json`, antes bajo `scripts/`.
- El hook de MkDocs para el catálogo es `pipeline/mkdocs_hook.py`, que
  reexporta `wgj.catalog`; construir la documentación no necesita nada más
  que `requirements-docs.txt`.
- **Todos los previews se regeneraron una vez con el port a Python.** Los
  bytes cambiaron; la geometría, las propiedades y los ids son idénticos, así
  que un mapa dibujado desde un preview sigue uniéndose a los datos completos.
  Los `preview_bytes` de los manifiestos y `data/index.json` lo reflejan. Un
  cambio de datos de nivel patch: nada cambió en ningún archivo a resolución
  completa.
- CI: el workflow de datos ejecuta `wgj validate --checksums`,
  `wgj finalize --check data/earth/*/`, `wgj index --check` y una
  regeneración con `wgj manifest data/earth/*/` que no debe dejar
  diferencias; el workflow de código ejecuta ruff, mypy y pytest sobre los
  fixtures, y después regenera los previews de ABW, BRB y DOM con
  `wgj previews` y falla ante cualquier diferencia.

### Eliminado

- El sitio de documentación ya no muestra sellos de "última actualización"
  ni genera tarjetas de previsualización social (Open Graph). Entre ambos
  costaban GitPython, Cairo, Pillow, un paso `apt` y un clon con historial
  completo en cada build; la cadena de docs baja de 46 a unos 30 paquetes y
  CI usa un clon superficial.

## [1.0.0] — 2026-09-24

La primera release etiquetada, cortada desde `main` en cuanto se mergee el
contrato de datos. Todo lo de esta sección va en ella: el contrato, la higiene
de ingeniería, América, el pipeline y el sitio de documentación.

### Añadido — contrato de datos v1

- **Un `id` de Feature estable en cada una de las 16.195 features**,
  `{ISO3}:{LEVEL}:{clave}`, único en todo el repositorio: el `shapeISO` real
  cuando existe (`CHL:ADM3:01402`, `USA:ADM1:US-SD`), y si no una clave
  basada en el nombre (`USA:ADM2:US-SD.davison`, `COL:ADM2:san-rafael`), con
  un sufijo numérico determinista ante colisiones de nombre. Las claves
  manuales se pueden fijar en `scripts/id_overrides.json` (vacío hoy).
- **Campos de jerarquía allí donde aplican**: `adm1ISO` en cada feature por
  debajo de ADM1 cuando el país lo tiene, archivos combinados incluidos
  (13.181 features); `parentISO` y `parentID` — el `id` del padre — en cada
  feature con un nivel padre publicado (16.063 features), en todos los países
  y no solo en Chile.
- **`data/index.json`**, el índice global: cada territorio y dataset en un
  único archivo de 340 KB (39 KB con gzip), manifiestos incrustados tal cual,
  sin marca de tiempo, así que es determinista byte a byte. Generado por
  `scripts/build_index.py`.
- **JSON Schemas** en `schemas/` (borrador 2020-12) para el manifiesto, el
  índice, una feature, sus propiedades y el registro de países, publicados en
  `https://andresgmg.github.io/World-GeoJSON/schemas/`. La lista blanca de
  licencias es ahora el enum `license` del esquema del manifiesto, y
  `fetch_sources.py` mapea el texto de licencia de origen a los mismos ids.
- **`scripts/finalize_geojson.py`**, el paso del pipeline que escribe los
  ids, la jerarquía, las correcciones de `shapeISO`, el bbox y el formato
  canónico de archivo (una feature por línea, compacto, 6 decimales; no
  cambia nada al reejecutarse). `build_data.py` lo ejecuta él mismo;
  `--check` verifica los datos commiteados en el CI.
- **Workflow de release**: subir una etiqueta `vX.Y.Z` publica una GitHub
  Release con `world-geojson-vX.Y.Z-{ISO3}.zip` por territorio,
  `world-geojson-vX.Y.Z-all.zip`, `index.json` y `SHA256SUMS`, con la sección
  correspondiente de este registro como notas.
- `CITATION.cff` en la raíz del repositorio.
- `build_data.py --resplit`, que vuelve a derivar los padres y las partes
  partidas desde los archivos commiteados tras una corrección de `shapeISO`,
  sin reconstruir desde la fuente.
- Mejoras de validación en `validate_data.py`: validación con JSON Schema de
  cada manifiesto, del índice, del registro y de cada feature de cada archivo
  a resolución completa; ids de feature únicos por archivo; cada `parentID`
  resuelve; el `bbox` del archivo es igual a las coordenadas; los recuentos
  de features del manifiesto coinciden con los archivos; `--checksums`
  recalcula el hash de cada archivo. El CI ejecuta además
  `finalize_geojson.py --check` y `build_index.py --check`.

### Cambiado — rompedor respecto al `main` 0.x sin publicar

No existía ninguna etiqueta, así que nada estaba fijado; aun así, el código
escrito contra `main` debe saber:

- `shapeISO` ya no lleva el id opaco de geoBoundaries donde la fuente no
  tiene código. Es `""` en 15.364 features de 22 datasets municipales
  (14.797 de ADM2, 501 de ADM3, las 66 de ADM4); `src_shape_id` conserva el
  id de origen.
- Tres códigos de origen corregidos desde `scripts/shapeiso_fixes.json` —
  Dakota del Sur `SU-SD` → `US-SD`, Ciudad de México `MX-MEX` → `MX-CMX`,
  Cotopaxi `EC-H` → `EC-X` — y los códigos ADM2 de Belice vaciados, ya que
  repetían el del distrito. `shapeISO` es ahora único dentro de cada nivel
  donde no está vacío.
- Las partes partidas siguen los códigos corregidos: `USA/ADM2/SU-SD.geojson`
  es ahora `US-SD.geojson` (66 condados); `MEX/ADM2/MX-CMX.geojson`
  (16 alcaldías) y `ECU/ADM2/EC-X.geojson` (7 cantones) son nuevos, y
  `MX-MEX.geojson` (ahora 125 municipios) y `EC-H.geojson` (ahora 10
  cantones) se redujeron en consecuencia.
- Cada archivo a resolución completa y cada preview se reescribió en el
  formato canónico, así que cambiaron los `bytes` y el `sha256` de cada
  archivo, y cada manifiesto. La geometría no cambia.

### Corregido — contrato de datos v1

- El `bbox` de 13 archivos era la extensión previa a la simplificación; ahora
  es igual a las coordenadas en cada archivo, y el CI lo comprueba.
- Los previews llevan ahora el `id` de feature, así que un mapa dibujado desde
  un preview se une a los datos completos.

### Añadido — higiene de ingeniería

- `pyproject.toml` con configuración de `ruff`, `mypy` y `pytest`, y una suite
  `tests/` para los scripts del pipeline.
- `justfile`, `.pre-commit-config.yaml` y `.editorconfig`.
- Workflow de CI `ci.yml` que ejecuta lint y tests en cada pull request;
  `validate-data` corre ahora también en los push a `main`.

### Corregido — pipeline y sitio

- El sitio de documentación perdió sus mapas de preview: el sparse checkout del
  workflow de docs excluía los archivos de `preview/` desde los que se sirven.
- `fetch_sources.py` descargaba el archivo de 297 MB de Chile para cualquier
  alcance, no solo cuando se pedía Chile, y lo extraía incluso con `--dry-run`.
- `build_data.py` salía con código 0 tras fallos.
- `validate_data.py --help` ejecutaba la validación completa en vez de mostrar
  la ayuda, y comprobaba las propiedades obligatorias solo en la primera feature
  de cada archivo; ahora comprueba todas.
- `gen_catalog.py` no detectaba un preview cambiado cuando el archivo nuevo
  tenía el mismo tamaño que el anterior.
- `make_previews.mjs` procesaba sus entradas en el orden del sistema de
  archivos, así que la salida no era reproducible entre plataformas.

### Documentación

- Todas las páginas de Referencia y Acerca de alineadas con los datos tal como
  se publican: el conjunto de propiedades realmente presente (`src_shape_id`,
  dónde existen `adm1ISO` y `parentISO`; `shapeID` y `shapeNameEn` nunca
  existieron), los campos reales del manifiesto, las reglas de partición y los
  territorios sin partir, los cuatro niveles de Chile, los problemas conocidos
  de `shapeISO` y la hoja de ruta hacia plataforma.

### Añadido — América

- **55 territorios, 95 datasets, 16.195 features.** Contornos de país desde
  Natural Earth 10m (dominio público); divisiones de primer nivel y municipales
  desde geoBoundaries `gbOpen`, solo con licencias permisivas; Chile desde IDE
  Chile.
- Los niveles municipales van partidos por su padre de primer nivel. El padre se
  deriva mediante unión espacial por mayor solapamiento, porque geoBoundaries no
  lleva referencia al padre y con frecuencia entrega un `shapeISO` vacío.
- Cada dataset registra su propia licencia, proveedor aguas arriba y añada. Una
  licencia a nivel de país sería una afirmación falsa: el contorno de Brasil es
  dominio público, sus estados CC BY 2.5 y sus municipios CC BY 3.0 IGO.
- mapshaper queda fijado en `package.json` e instalado localmente, en vez de
  resolverse por `npx` en cada llamada.

**Qué no entra, y por qué.** Quince países no tienen divisiones de primer nivel
porque su ADM1 en geoBoundaries es ODbL o CC-BY-SA. Bonaire/San Eustaquio y Saba
y la Isla Bouvet no publican nada. Los ADM2 de Jamaica y Santa Lucía se dejaron
fuera por parecer mal asignados — 827 unidades frente a 14 parroquias, 547
frente a 10 distritos. Ver la [Hoja de ruta](roadmap.md).

**Rarezas de las fuentes que conviene conocer.** El metadato `admUnitCount` de
geoBoundaries no concuerda con los archivos que sirve en varios casos (Surinam
declara 62 unidades ADM2 y entrega 58); los conteos aquí son lo que los archivos
contienen realmente. El ADM1 de Argentina omite la Ciudad Autónoma de Buenos
Aires, así que sus 8 comunas no solapan con ninguna provincia y se conservan en
una parte `unassigned` en lugar de descartarse. Ecuador y Perú entregan cada uno
un ADM1 cuyo `shapeISO` contiene un asterisco.

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
