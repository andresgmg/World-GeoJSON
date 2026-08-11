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
- [ ] Reestructurar Chile a `data/earth/CHL/` con manifiestos
- [ ] Aplicar el esquema estándar de propiedades a Chile
- [ ] Minificar y recortar la precisión de los archivos existentes
- [ ] Generación de previews y mapas interactivos
- [ ] Workflow de validación de datos

## Siguiente — Chile completo, luego Latinoamérica

- [ ] `CHL_ADM0` — el contorno nacional
- [ ] Las tres comunas que faltan: Antártica, Isla de Pascua, Juan Fernández
- [ ] `CHL_ADM2` — provincias, si se encuentra una fuente con licencia abierta
- [ ] Argentina, Perú, Bolivia, Uruguay, Paraguay
- [ ] Plantillas de issue y PR para envío de países
- [ ] Traducir al español las páginas generadas del catálogo

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
| 343 de 346 comunas | `comunas.geojson` | Siguiente |
| Sin archivo de límites ADM2 (provincias) | Chile | Siguiente, si hay fuente |
| Coordenadas con ~14 decimales | Ambos archivos | Ahora |
| Con indentación, ~40% de sobrecoste de tamaño | Ambos archivos | Ahora |
| Sin miembro `bbox` | Ambos archivos | Ahora |
| `cod_comuna` como entero, pierde el cero inicial | `comunas.geojson` | Ahora |
| `id` de GeoJSON en 5 de 343 features | `comunas.geojson` | Ahora |
| Archivos `.json` duplicados | Raíz del repo | Ahora |
| Unidades de área inconsistentes entre archivos | Ambos archivos | Ahora |
| `Región de Aysén del Gral.Ibañez del Campo` malformado | `regiones.geojson` | Ahora |

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
