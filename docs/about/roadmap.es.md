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
- [ ] Plantillas de issue y PR para envío de países
- [ ] Traducir al español las páginas generadas del catálogo

## Siguiente — los demás continentes

Un PR cada uno, reutilizando el pipeline: Europa, África, Asia y Oceanía.

## Más adelante — cobertura global

- [ ] ADM0 de todos los países (Natural Earth es el punto de partida obvio)
- [ ] ADM1 de todos los países (geoBoundaries)
- [ ] ADM2 donde existan fuentes con licencia abierta
- [ ] TopoJSON junto a GeoJSON
- [ ] Releases de datos etiquetadas, y documentación versionada

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
| 13 países sin ADM1 con licencia permisiva | América | Pendiente de fuente permisiva |
| Asignación del tier municipal sin verificar en ~15 territorios | `scripts/countries.json` | Marcados `verify` y publicados como `review` |
| Los distritos de Perú no están disponibles — geoBoundaries se detiene en provincias | Perú | Pendiente de fuente |
| Archivos heredados aún en la raíz | `comunas.geojson` y compañía | Obsoletos, se retiran en la próxima mayor |

## No previsto

- **Una API alojada o servicio de teselas.** Esto es un repositorio de datos.
  Cloudflare, jsDelivr y tu propio CDN sirven mejor.
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
