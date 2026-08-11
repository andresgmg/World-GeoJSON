# Registro de cambios

El formato sigue [Keep a Changelog](https://keepachangelog.com/es/1.1.0/). El
versionado sigue [Semantic Versioning](https://semver.org/lang/es/) adaptado a
datos según [Versionado y estabilidad](versioning.md).

## Sin publicar

### Añadido

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

La siguiente release reestructura el árbol de datos. Ver
[Versionado y estabilidad](versioning.md#el-cambio-rompedor-que-viene).

- `regiones.geojson` → `data/earth/CHL/CHL_ADM1.geojson`
- `comunas.geojson` → `data/earth/CHL/CHL_ADM3.geojson`
- Propiedades renombradas al esquema estándar
- `cod_comuna` pasa a `shapeISO`, una **cadena** con cero a la izquierda
- Artefactos Esri eliminados
- Archivos `.json` duplicados eliminados

Los cuatro archivos de la raíz se mantienen en su sitio, marcados como
obsoletos, durante una versión mayor completa. No desaparecerán en silencio.

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
