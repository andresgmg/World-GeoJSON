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
| ¿Cómo identifico una feature? | Su `id`: `{ISO3}:{LEVEL}:{clave}`, estable dentro de una versión de datos | [Propiedades](properties.md) |
| ¿Cómo listo todo en una sola petición? | `data/index.json` | [Índice global y esquemas](index-json.md) |

## Lenguaje de conformidad

Estas páginas usan **debe**, **debería** y **puede** en el sentido de
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119). "Debe" se aplica en la
revisión y, donde es práctico, en CI.

## Los archivos heredados

Todo lo que hay bajo `data/` sigue estas convenciones. Los cuatro archivos que
siguen en la raíz del repositorio — `regiones.geojson`, `comunas.geojson` y sus
duplicados `.json` — no: son anteriores a las convenciones.

Se mantienen en su sitio, sin cambios, durante una versión mayor completa para
que los enlaces profundos existentes sigan funcionando, y están **obsoletos**.
Usa `data/earth/CHL/`.

Ver [Versionado y estabilidad](../about/versioning.md) para el calendario de
retirada.

--8<-- "abbreviations.md"
