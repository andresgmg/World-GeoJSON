# Fuentes aprobadas y licencias

**Lee esto antes de hacer cualquier otro trabajo en una contribución de datos.**

Un archivo de límites con una licencia incompatible no se puede mergear, por
buena que sea la geometría. Y una vez que está en la historia de git es
genuinamente difícil de quitar — reescribir la historia rompe todos los clones
y forks existentes. Así que la verificación se hace en la puerta.

## La cuestión de la compatibilidad

Este repositorio distribuye datos públicamente, gratis, para cualquier uso
incluido el comercial. Una fuente solo es utilizable aquí si su licencia
permite exactamente eso.

Hay dos modos de fallo:

- **Restricciones de redistribución** — la licencia prohíbe transmitir los
  datos, o prohíbe el uso comercial. Inutilizable, sin más.
- **Obligaciones de share-alike (copyleft)** — la licencia permite
  redistribuir pero exige que los derivados lleven la misma licencia.
  Utilizable solo si todo el proyecto acepta esa licencia, lo que cambia los
  términos para cada consumidor existente.

## Verde — usar libremente

| Fuente | Licencia | Notas |
|---|---|---|
| [Natural Earth](https://www.naturalearthdata.com/) | Dominio público | Escala pequeña (1:10m–1:110m). Ideal para ADM0 y vistas mundiales. No exige atribución, aunque es de buena educación. |
| [geoBoundaries](https://www.geoboundaries.org/) | CC BY 4.0 | La mejor fuente global abierta para ADM1–ADM3. **Exige atribución** — regístrala en el manifiesto. El vocabulario de propiedades de este proyecto coincide con el suyo a propósito. |
| SDIs nacionales con licencias abiertas | Varía | P.ej. BCN / IDE Chile. Revisa los términos concretos; "datos de gobierno" no significa automáticamente "abiertos". |
| [Derivados de OSM bajo otra licencia](https://osmdata.openstreetmap.de/) | Varía | Algunos productos derivados se publican bajo términos distintos de ODbL. Verifica producto por producto. |

## Ámbar — usar solo con cuidado

| Fuente | Licencia | El problema |
|---|---|---|
| [OpenStreetMap](https://www.openstreetmap.org/) | ODbL 1.0 | **Share-alike.** Una base de datos derivada también debe ser ODbL. Los límites extraídos de OSM no se pueden relicenciar, y mezclarlos en este repositorio arrastraría discutiblemente todo el árbol de datos a ODbL — cambiando los términos para todo el que ya lo esté usando. No se acepta sin una decisión explícita del proyecto de licenciar de forma dual. |
| Wikidata / Wikimedia | CC0 para datos, varía para geometría | Los datos estructurados son CC0, pero la geometría importada puede arrastrar la licencia original. Rastrea la procedencia real. |

## Rojo — no usar

| Fuente | Licencia | El problema |
|---|---|---|
| [GADM](https://gadm.org/license.html) | Propia, no comercial | **El error más común.** Los términos de GADM prohíben la redistribución y el uso comercial sin permiso previo. Es la fuente global de límites más cómoda y el primer sitio donde mira un contribuidor bienintencionado — que es exactamente por qué hay que nombrarla explícitamente. Incompatible con este repositorio en todos los aspectos. |
| Capas base de Esri / ArcGIS Online | Propietaria | Licenciadas para uso dentro de productos Esri. No redistribuibles. |
| Geometría de Google Maps | Propietaria | La extracción está prohibida por los términos del servicio. |
| Proveedores comerciales (HERE, TomTom, …) | Propietaria | Licencias por puesto o por petición. Nunca redistribuibles. |
| Cualquier dataset sin licencia declarada | — | La ausencia de licencia significa **todos los derechos reservados**, no dominio público. |

!!! danger "GADM es la trampa"

    Si te llevas una sola cosa de esta página: GADM es completo, está bien
    mantenido, es gratis de descargar y **no es utilizable aquí**. Descargarlo
    para tu propio análisis personal está bien. Aportarlo a un repositorio
    público MIT/CC-BY es una violación de licencia.

    Un PR cuya geometría coincida con los patrones de vértices
    característicos de GADM será cuestionado aunque el campo de fuente diga
    otra cosa.

## Registrar la fuente

Cada `manifest.json` debe llevar un bloque `source` completo:

```json
"source": {
  "name": "geoBoundaries",
  "url": "https://www.geoboundaries.org/countryDownloads.html",
  "license": "CC-BY-4.0",
  "retrieved": "2026-08-10"
}
```

- `license` **debe** ser un [identificador SPDX](https://spdx.org/licenses/)
  cuando exista. El CI lo valida contra la lista aprobada.
- `retrieved` importa: los límites cambian, y conocer la añada es como un
  consumidor decide si dos datasets se pueden combinar con seguridad.

## Si tienes dudas

Abre un issue y pregunta antes de hacer el trabajo. Una duda de licencia
resuelta en diez minutos sale mucho más barata que una contribución que no se
puede mergear — o peor, una que se mergea y luego hay que retirar.

--8<-- "abbreviations.md"
