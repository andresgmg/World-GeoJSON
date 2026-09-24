# Registro de cambios

El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/). El
versionado sigue [Semantic Versioning](https://semver.org/lang/es/) adaptado a
datos según [Versionado y estabilidad](versioning.md).

## Sin publicar

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
