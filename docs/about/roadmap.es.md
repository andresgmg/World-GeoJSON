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

## Siguiente — América

Los 57 territorios UN M49, en un PR para todo el continente.

- [ ] ADM0 de cada territorio desde Natural Earth
- [ ] ADM1 y tier municipal desde geoBoundaries, solo licencias permisivas
- [ ] `CHL_ADM0` — el contorno nacional
- [ ] Verificar los conteos sospechosos: Jamaica ADM2 (827 frente a 14
      parroquias), Santa Lucía ADM2 (547 frente a 10 distritos), Bahamas
      ADM1/ADM2 (32/34)
- [ ] Plantillas de issue y PR para envío de países
- [ ] Traducir al español las páginas generadas del catálogo

### Huecos de cobertura conocidos

Excluir las fuentes copyleft deja trece países de América sin un ADM1 que este
proyecto pueda redistribuir: Colombia, Costa Rica, Cuba, Guatemala, Guyana,
Honduras, Haití, Nicaragua, Panamá, Surinam, Trinidad y Tobago, Uruguay y San
Vicente y las Granadinas. Sus entradas en geoBoundaries son ODbL.

Cerrar un hueco significa encontrar un SDI nacional o una publicación de HDX con
términos permisivos — no relajar la regla. Ver
[Fuentes aprobadas](../contributing/sources.md).

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
