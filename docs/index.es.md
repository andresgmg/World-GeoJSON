# World GeoJSON

Límites administrativos en GeoJSON, abiertos y versionados — hoy América,
creciendo hacia todos los países del mundo y, con el tiempo, hacia la Luna y
Marte.

Todos los datos son GeoJSON según [RFC 7946](https://www.rfc-editor.org/rfc/rfc7946)
en WGS 84. Sin API key, sin registro, sin un servicio con límite de peticiones
en medio: pides una URL y tienes los límites.

<div class="grid cards" markdown>

-   :material-rocket-launch: **[Empezar](get-started/index.md)**

    Encuentra un dataset, copia una URL y cárgalo en Leaflet, MapLibre, Python
    o QGIS.

-   :material-map-search: **[Catálogo](catalog/index.md)**

    Todos los datasets, con número de features, bounding box, lista de
    propiedades y enlaces de descarga.

-   :material-book-open-variant: **[Referencia](reference/index.md)**

    Las convenciones: estructura de carpetas, niveles administrativos, esquema
    de propiedades, política de CRS y en qué se diferencian los cuerpos
    planetarios.

-   :material-package-variant: **[Bibliotecas](libraries/index.md)**

    `geoworld` para Python y JavaScript: lee el índice de una release de datos
    fijada, descarga bajo demanda, verifica checksums, navega por `id`.

-   :material-source-pull: **[Contribuir](contributing/index.md)**

    Cómo añadir un país — incluyendo qué fuentes son legalmente seguras.

</div>

## Pruébalo

```js
const url =
  "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/earth/CHL/CHL_ADM1.geojson";

const regiones = await fetch(url).then((r) => r.json());
console.log(regiones.features.length); // 16
console.log(regiones.features.map((f) => f.properties.shapeName));
// ["Coquimbo", "Ñuble", "Los Lagos", …]
```

Todos los datasets están en `data/earth/{ISO3}/{ISO3}_{LEVEL}.geojson` y
llevan las mismas cuatro propiedades — `shapeName`, `shapeISO`, `shapeGroup`,
`shapeType` — así que el fragmento sirve para cualquier país del
[Catálogo](catalog/index.md).

## Qué es este proyecto

Un **catálogo de datos**, no un servicio. El repositorio guarda los archivos;
este sitio documenta qué contienen, de dónde vino cada uno y qué convenciones
debe seguir cualquier contribución nueva.

Esas convenciones importan más de lo que parece. El proyecto empezó como un
volcado de dos archivos de un solo país, sin esquema, sin declaración de
sistema de coordenadas y sin atribución de fuente. Escalar eso a cientos de
países sin reglas escritas produce un montón de archivos mutuamente
incompatibles. La sección [Referencia](reference/index.md) es el contrato que
lo evita.

## Qué no es

- **No es un geocodificador ni un servidor de teselas.** Son polígonos de
  límites. El renderizado, la búsqueda y el indexado espacial son trabajo de tu
  aplicación.
- **No es autoritativo sobre soberanía.** Los límites siguen a la fuente
  declarada en la página de cada dataset. Donde hay reclamaciones en conflicto,
  el proyecto documenta el desacuerdo en lugar de resolverlo — ver
  [Fronteras disputadas](about/disputed-boundaries.md).
- **No tiene una licencia uniforme.** El código es MIT. Los *datos* se
  licencian según su fuente, y algunas exigen atribución. Ver
  [Licencias y atribución](about/license.md).

## Estado actual

**América: 55 territorios, 95 datasets, 16.195 features.**

Contornos de país desde Natural Earth, divisiones de primer nivel y municipales
desde geoBoundaries, y Chile desde la *División Política Administrativa* 2023 de
IDE Chile. Todos los datasets tienen licencia permisiva — las fuentes copyleft
quedan excluidas, y por eso algunos países aún no tienen divisiones de primer
nivel.

Europa, África, Asia y Oceanía vienen después, un continente por release. La
[Hoja de ruta](about/roadmap.md) tiene la secuencia y los huecos conocidos.

--8<-- "abbreviations.md"
