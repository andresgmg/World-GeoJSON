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

## Hecho — Europa

**51 territorios, 97 datasets, 59.265 features.** El mismo pipeline y las
mismas fuentes que en América: contornos desde Natural Earth, primer nivel y
tier municipal desde geoBoundaries, solo con licencias permisivas.
geoBoundaries se lee ahora desde un commit fijado de su repositorio en vez de
su API, así que una reconstrucción descarga exactamente los mismos archivos.

Tres licencias que solo exigen atribución entraron en la lista blanca, para
datos nacionales que geoBoundaries redistribuye: la Open Government Licence
v3.0 del Reino Unido, la Data licence Germany – attribution – 2.0 de Alemania
y la Open Data Commons Attribution 1.0 (las comunas de Francia). Las 35.010
comunas francesas añaden además un quinto nivel, ADM5, al contrato.

Diecisiete países tienen primer nivel y tier municipal: Bélgica, Bulgaria,
Bosnia y Herzegovina, Bielorrusia, Alemania, Dinamarca, España, Francia, el
Reino Unido, Grecia, Irlanda, Italia, Macedonia del Norte, los Países Bajos,
Noruega, Rumanía y Suecia. Kosovo se publica como `XKX`, un código de usuario,
con la disputa explicada en su manifiesto — ver
[Fronteras disputadas](disputed-boundaries.md). **Svalbard y Jan Mayen** no
publica nada: Natural Earth dibuja ambos dentro del contorno de Noruega.

### Huecos de cobertura

**Diecinueve países no tienen aquí divisiones de primer nivel.** Su ADM1 en
geoBoundaries es ODbL (Estonia, Finlandia, Croacia, Islandia, Liechtenstein,
Lituania, Luxemburgo, Mónaco, Montenegro, Polonia, Portugal, Rusia, San
Marino, Serbia, Eslovaquia, Ucrania), CC-BY-SA (Austria, Kosovo) o está bajo
la licencia propia de swisstopo, que no está en la lista blanca (Suiza).
Islandia, Luxemburgo, Portugal y Ucrania tienen un tier municipal con licencia
permisiva, publicado sin ADM1 por encima. Åland, las Islas Feroe, Guernsey,
Gibraltar, la Isla de Man, Jersey y la Ciudad del Vaticano no tienen nada por
debajo del contorno en origen.

**Diecisiete países no tienen aquí tier municipal** porque es copyleft o
tiene una licencia fuera de la lista blanca: Austria, Suiza, Chequia,
Estonia, Finlandia, Croacia, Hungría, Lituania, Polonia, Rusia, Serbia,
Eslovaquia, Eslovenia y Kosovo, más Liechtenstein, Montenegro y San Marino,
cuyos municipios son su primer nivel. Chequia, Hungría y Eslovenia sí publican
su primer nivel. Los 61 municipios de Albania y las comunas de Moldavia no
están en geoBoundaries.

Pendiente en este continente:

- [ ] Niveles intermedios. El pipeline construye ADM1 y un tier municipal por
      país, así que los niveles intermedios con licencia permisiva aún no
      están: los 96 départements y 320 arrondissements de Francia, las 20
      regiones y 107 provincias de Italia, las 38 regiones administrativas de
      Alemania, los 77 distritos de Chequia, los 43 arrondissements de
      Bélgica y los segundos niveles de Grecia (14 unidades) y de Bosnia y
      Herzegovina (12)
- [ ] Los municipios de Alemania (Gemeinden) — no están en geoBoundaries; el
      tier publicado son los 401 distritos
- [ ] Vigencias más recientes donde ha habido reformas: las fusiones de
      Bélgica de 2019, las reformas de Noruega de 2020 y 2024, los raiones de
      Ucrania de 2020, las fusiones de Islandia (74 unidades frente a 64), los
      municipios de Albania de 2015
- [ ] Previews del catálogo para los tres niveles demasiado densos para 2 MB
      incluso con la simplificación más gruesa: España ADM3, Francia ADM5 e
      Italia ADM4

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

Un PR cada uno, reutilizando el pipeline: África, Asia y Oceanía.

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
| 19 países sin ADM1 con licencia permisiva | Europa | Pendiente de fuente permisiva |
| `shapeISO` es `""` en 58.492 features — todos los datasets municipales europeos salvo el de Portugal | 20 datasets municipales de geoBoundaries | Por diseño, como arriba; usa `id` |
| 863 ids basados en el nombre llevan sufijo numérico. Algunos son homónimos reales (Lagoa y Calheta en Portugal, San Teodoro en Italia); otros son un mismo municipio dibujado como varias features en origen | FRA 791, ROU 48, UKR 10, NOR 6, PRT 5, BGR 1, GRC 1, ITA 1 | Estables por versión de datos; pueden renumerarse con un refresco de la fuente — fija una versión |
| 129 comunas no solapan con ninguna de las 13 regiones metropolitanas | FRA ADM5 (los cinco departamentos de ultramar) | Conservadas en `ADM5/unassigned.geojson` |
| Sin archivo combinado: el nivel se publica solo como partes por región | FRA ADM5 | Por diseño — un único archivo superaría el presupuesto de 18 MiB. Usa las partes (`iter_parts`) |
| Sin preview en el catálogo: más de 2 MB incluso con la simplificación más gruesa | ESP ADM3, FRA ADM5, ITA ADM4 | Los archivos de datos están completos; solo falta el mapa del catálogo |
| Asignación del tier municipal sin verificar en 11 territorios | BEL, DEU, ESP, FRA, GBR, IRL, ISL, NOR, PRT, ROU, UKR | Marcados `verify` y publicados como `review` |
| Budapest está dibujada dentro del condado de Pest: los metadatos cuentan 20 unidades y el archivo trae 19 | HUN ADM1 | En origen; pendiente de corrección o de otra fuente |
| La provincia de Sofía tiene 23 unidades frente a 22 municipios: dos se llaman Zlatitsa | BGR ADM2 (`BGR:ADM2:BG-23.zlatitsa-2`) | En origen; pendiente de corrección |
| El primer nivel son las cinco macrorregiones NUTS 1, no las 20 regiones | ITA ADM1 | Niveles tal como vienen en origen; regiones y provincias están pendientes arriba |
| Crimea: dentro del contorno de Rusia en Natural Earth, dentro de los raiones de Ucrania en geoBoundaries | RUS ADM0, UKR ADM0 y ADM2 | Documentado en [Fronteras disputadas](disputed-boundaries.md) |
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
