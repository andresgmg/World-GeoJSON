# Referencia

Estas páginas definen cómo se organizan los datos de este repositorio. Son el
contrato: una contribución que las siga puede mergearse; una que no, no —
por buena que sea la geometría.

Existen porque el proyecto está escalando de un país a potencialmente
doscientos. Dos archivos con nombres de propiedades improvisados son
simplemente desprolijos; cuatrocientos archivos con nombres improvisados son
inutilizables.

## De un vistazo

| Pregunta | Respuesta | Detalle |
|---|---|---|
| ¿Dónde va un archivo? | `data/{body}/{ISO3}/{ISO3}_{LEVEL}.geojson` | [Nombres](naming.md) |
| ¿Qué es ADM1? | Divisiones de primer nivel, como sea que se llamen localmente | [Niveles](admin-levels.md) |
| ¿Qué propiedades son obligatorias? | `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` | [Esquema](schema.md) |
| ¿Qué sistema de coordenadas? | OGC:CRS84 (≡ EPSG:4326), longitud primero | [CRS](crs.md) |
| ¿Puede un archivo declarar su CRS? | **No.** RFC 7946 eliminó ese miembro | [CRS](crs.md#el-miembro-crs-esta-prohibido) |
| ¿Cómo funcionan la Luna y Marte? | Marcos body-fixed IAU 2015, sin códigos ISO | [Planetario](planetary.md) |
| ¿De dónde salen los metadatos del catálogo? | `manifest.json` junto a los datos | [Manifiesto](manifest.md) |

## Lenguaje de conformidad

Estas páginas usan **debe**, **debería** y **puede** en el sentido de
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). "Debe" se aplica en la
revisión y, donde es práctico, en CI.

## Estado actual frente a estado objetivo

Aquí la honestidad importa más que la prolijidad: **los datos actuales de Chile
todavía no siguen estas convenciones.** Son anteriores a ellas.

| Convención | Chile hoy | Objetivo |
|---|---|---|
| Ubicación | `comunas.geojson` en la raíz | `data/earth/CHL/CHL_ADM3.geojson` |
| Propiedad de nombre | `Comuna` | `shapeName` |
| Propiedad de código | `cod_comuna` (entero, `1402`) | `shapeISO` (cadena, `01402`) |
| Artefactos Esri | `objectid`, `st_area_sh`, `st_length_` | eliminados |
| Miembro `bbox` | ausente | presente |
| Precisión de coordenadas | ~14 decimales | 6 decimales |

Cada página marca la distancia entre ambos. La migración es un cambio rompedor
deliberado con ventana de obsolescencia — ver
[Versionado y estabilidad](../about/versioning.md).

--8<-- "abbreviations.md"
