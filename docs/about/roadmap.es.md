# Hoja de ruta

Honesta sobre qué está hecho, qué viene después y qué es aspiracional.

## Ahora — cimientos

Poner convenciones y tooling en su sitio antes de que crezcan los datos.

- [x] Sitio de documentación con MkDocs + Material
- [x] Convenciones escritas: nombres, niveles administrativos, esquema de
      propiedades, CRS, planetario
- [x] Política de licencias y lista de fuentes aprobadas
- [x] Política de fronteras disputadas
- [x] Generador de catálogo conectado a los manifiestos
- [x] CI que construye y despliega el sitio
- [x] Pipeline de ingesta: descarga, normaliza, simplifica, parte, manifiesto y preview
- [x] Chile desde la DPA 2023 de IDE Chile — ADM1, ADM2 y ADM3
- [x] Generación de previews y mapas interactivos
- [x] Workflow de validación de datos con lista blanca de licencias

## Hecho — América

**55 territorios, 95 datasets, 16.195 features.** Contornos de país desde
Natural Earth; primer nivel y tier municipal desde geoBoundaries, solo con
licencias permisivas; Chile desde IDE Chile.

Dos de los 57 territorios UN M49 no publican nada: **Bonaire, San Eustaquio y
Saba** y la **Isla Bouvet** no están en Natural Earth bajo sus códigos ISO y no
tienen datos de subdivisiones con licencia permisiva.

### Huecos de cobertura

**Quince países no tienen aquí divisiones de primer nivel** porque su ADM1 en
geoBoundaries es copyleft — ODbL en Colombia, Costa Rica, Cuba, Guatemala,
Guyana, Honduras, Haití, Nicaragua, Panamá, Surinam, Trinidad y Tobago, Uruguay
y San Vicente y las Granadinas; CC-BY-SA en Granada y Groenlandia. Varios sí
tienen un tier municipal con licencia permisiva, así que aparecen en el catálogo
con ADM2 y sin ADM1 por encima.

Cerrar un hueco significa encontrar un SDI nacional o una publicación de HDX con
términos permisivos — no relajar la regla. Ver
[Fuentes aprobadas](../contributing/sources.md).

Pendiente en este continente:

- [ ] Los distritos de Perú — geoBoundaries se detiene en sus 196 provincias
- [ ] Verificar los conteos sospechosos antes de confiar en ellos: Jamaica ADM2
      (827 frente a 14 parroquias) y Santa Lucía ADM2 (547 frente a 10
      distritos) parecen mal asignados y se dejaron fuera; los ADM1/ADM2 de
      Bahamas (32/34) son casi idénticos
- [ ] Guadalupe, Martinica, Guayana Francesa e Islas Vírgenes de EE.UU. tienen
      tier municipal pero no ADM1 aguas arriba, así que no se pueden partir
- [ ] Traducir al español las páginas generadas del catálogo

## Siguiente — de repositorio de datos a plataforma

América demostró el pipeline. Las próximas releases convierten el repositorio en
algo de lo que un programa pueda depender: primero un contrato estable, luego el
tooling, luego bibliotecas que lo hablen. En orden:

**Fase 0 — higiene de ingeniería** (hecha)

- [x] Lint, comprobación de tipos y tests — `ruff`, `mypy`, `pytest` —
      ejecutados por un workflow de CI en cada pull request
- [x] Corrección de bugs del pipeline, listados en el
      [Registro de cambios](changelog.md)
- [x] Todas las páginas de documentación alineadas con lo que contienen los
      datos

**Fase 1 — contrato de datos v1** (hecha; `v1.0.0` se etiqueta desde el merge)

- [x] `data/index.json`: un único archivo que enumera cada territorio, nivel y
      archivo con `bytes`, `sha256`, `bbox` y licencia — ver
      [Índice global y esquemas](../reference/index-json.md)
- [x] JSON Schemas en `schemas/` para el manifiesto, el índice, una feature,
      sus propiedades y el registro de países, aplicados en el CI
- [x] Un `id` de Feature estable en cada feature: `{ISO3}:{LEVEL}:{clave}`
- [x] `parentID`, `parentISO` y `adm1ISO` en cada feature subnacional, no solo
      en las de Chile
- [x] `shapeISO` deja de rellenarse con ids opacos de geoBoundaries, y se
      resuelven los códigos duplicados (`US-SD`, `MX-CMX`, `EC-X`, Belice
      vaciado)
- [x] Un paso de finalización (hoy `wgj finalize`) que escribe todo
      lo anterior y el formato canónico de archivo, comprobado en el CI
- [x] Releases de datos etiquetadas: un workflow de release que publica una
      GitHub Release con zips por país, `index.json` y `SHA256SUMS` en cada
      etiqueta (etiqueta pendiente del merge)

**Fase 2 — el pipeline como paquete** (hecha)

- [x] Los scripts pasaron a ser un paquete Python instalable, `wgj` bajo
      `pipeline/`, con una CLI — `wgj fetch`, `build`, `finalize`, `previews`,
      `manifest`, `index`, `validate` y `all` — documentada en
      [Pipeline de datos](../contributing/pipeline.md)
- [x] Tests que corren sobre `fixtures/data/` — tres territorios pequeños y su
      índice — así que el CI no necesita un checkout de los datos
- [x] Previews generados desde Python (mapshaper sigue corriendo vía Node)

Los `scripts/*.py` se quedaron como shims de compatibilidad durante una
release y se retiraron en la Fase 4, como estaba previsto.

**Fase 3 — bibliotecas cliente** (hecha; primera publicación pendiente)

- [x] Python `geoworld` (`packages/python/geoworld`, PyPI)
- [x] TypeScript `geoworld` (`packages/js/geoworld`, npm)
- [ ] Publicadas: etiquetas `python-v0.1.0` y `js-v0.1.0`, cuando estén
      configurados los publicadores en PyPI y npm

Ambas son clientes ligeros con la misma API: leen `index.json` de una versión
de datos fijada, descargan bajo demanda, cachean, verifican `sha256` y navegan
por `id`. Sin servidor de por medio — descargan archivos estáticos. Ver
[Bibliotecas cliente](../libraries/index.md).

**Fase 4 — adaptadores para frameworks e incorporación**

- [x] `geoworld-maplibre`, `geoworld-leaflet` y `geoworld-react` sobre
      `geoworld` — ver [Bibliotecas cliente](../libraries/index.md)
- [x] Ejemplos trabajados en `examples/` (Leaflet, MapLibre, React; sin build)
- [x] Formularios de issue (país nuevo, problema de datos, bug de biblioteca),
      plantilla de pull request y `CODEOWNERS`
- [x] Retirados los shims de compatibilidad `scripts/*.py` que quedaron de la
      Fase 2

## Siguiente — los demás continentes

Un PR cada uno, reutilizando el pipeline: Europa, África, Asia y Oceanía.

## Más adelante — cobertura global

- [ ] ADM0 de todos los países (Natural Earth es el punto de partida obvio)
- [ ] ADM1 de todos los países (geoBoundaries)
- [ ] ADM2 donde existan fuentes con licencia abierta
- [ ] TopoJSON junto a GeoJSON
- [ ] Documentación versionada (las releases de datos etiquetadas suben a la
      Fase 1)

ADM3 explícitamente no es un objetivo a escala global. Muy pocos países lo
publican abiertamente y los tamaños de archivo se vuelven inmanejables.

## Eventualmente — la Luna y Marte

Las convenciones [ya están escritas](../reference/planetary.md), a propósito:
la convención de latitud en particular no se puede inferir de los datos a
posteriori, así que equivocarse sale caro de descubrir y caro de arreglar.

- [ ] Cuadrángulos lunares, marco body-fixed IAU 2015
- [ ] Cuadrángulos marcianos
- [ ] Accidentes superficiales con nombre del IAU Gazetteer
- [ ] Mapas base WMS de USGS Astrogeology en los previews

## Problemas de datos conocidos

Registrados, no escondidos.

| Problema | Dónde | Estado |
|---|---|---|
| Falta la comuna Antártica (12202) — 345 de 346 | Chile ADM3 | No se corrige; el paquete DPA oficial excluye la reclamación antártica |
| 15 países sin ADM1 con licencia permisiva | América | Pendiente de fuente permisiva |
| La mayoría de las unidades municipales no tienen código oficial en origen, así que `shapeISO` es `""` en 15.364 features | 22 datasets municipales de geoBoundaries | Por diseño desde 1.0.0 — un código vacío es honesto, un id opaco no lo era. Usa `id`; lo cerraría una fuente nacional con códigos |
| 169 ids basados en el nombre llevan sufijo numérico (`COL:ADM2:albania-2`) porque la fuente tiene varias unidades con el mismo nombre y sin código | COL 84, HND 28, SLV 18, ARG 16, GTM 6, USA 6, MEX 4, BLZ 2, BRA 2, VIR 2, SUR 1 | Estables por versión de datos; pueden renumerarse con un refresco de la fuente — fija una versión |
| 12 unidades municipales no solapan con ningún padre ADM1 | ARG ADM2 (8, ciudad de Buenos Aires), BRA ADM2 (3), USA ADM2 (1) | Conservadas en partes `unassigned` con `adm1ISO: "unassigned"` y sin `parentID` |
| Asignación del tier municipal sin verificar en 19 territorios | `pipeline/src/wgj/tables/countries.json` | Marcados `verify` y publicados como `review` |
| Los distritos de Perú no están disponibles — geoBoundaries se detiene en provincias | Perú | Pendiente de fuente |
| Archivos heredados aún en la raíz | `comunas.geojson` y compañía | Obsoletos; se mantienen durante la serie 1.x y se retiran en v2.0.0 |

## No previsto

- **Una API alojada o servicio de teselas.** Esto es un repositorio de datos,
  y las bibliotecas de la Fase 3 son del lado del cliente: descargan archivos
  estáticos. Cloudflare, jsDelivr y tu propio CDN sirven mejor.
- **Geocodificación o datos de direcciones.** Otro problema, otras fuentes.
- **Límites históricos.** Interesante, y un proyecto en sí mismo.
- **Exactitud submétrica.** Son límites administrativos, no levantamientos
  catastrales.

## Contribuir a la hoja de ruta

[Abre un issue.](https://github.com/andresgmg/World-GeoJSON/issues) Los países
donde tengas conocimiento local de cuál es la fuente abierta autoritativa son
especialmente útiles — encontrar una fuente legalmente utilizable es de forma
consistente la parte más difícil.

--8<-- "abbreviations.md"
