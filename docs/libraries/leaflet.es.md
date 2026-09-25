# Adaptador Leaflet

`geoworld-leaflet` en [npm](https://www.npmjs.com/package/geoworld-leaflet):
helpers que ponen un nivel del [cliente JavaScript](javascript.md) en un mapa
[Leaflet](https://leafletjs.com/). Cero dependencias en runtime: Leaflet se
recibe por parámetro, nunca se importa, así que el mismo paquete funciona con
`window.L` de una etiqueta `<script>`, con un bundler y, cuando llegue, con
Leaflet 2. El código vive en
[`packages/js/geoworld-leaflet`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/js/geoworld-leaflet).

```bash
npm install geoworld geoworld-leaflet leaflet
```

## Una llamada por nivel

```ts
import { createClient } from "geoworld";
import { withLeaflet } from "geoworld-leaflet";

const world = createClient({ version: "1.0.0" });
const gw = withLeaflet(L);                        // window.L, o import * as L from "leaflet"

const regions = await gw.addBoundaries(map, world, "CHL", "ADM1", {
  fit: true,                                      // fitBounds con el bbox del índice
  onEachFeature: (feature, layer) => layer.bindTooltip(feature.properties.shapeName),
});
regions.remove();                                 // es un L.GeoJSON normal
```

`withLeaflet(L)` devuelve tres funciones:

| Función | Devuelve |
|---|---|
| `bounds(bbox)` | `new L.LatLngBounds` a partir de un bbox del índice (`client.bbox(iso3, level)`) |
| `boundaries(client, iso3, level, options?)` | una capa `L.GeoJSON`, aún fuera del mapa |
| `addBoundaries(map, client, iso3, level, options?)` | la misma capa añadida al mapa, encuadrada si hay `fit` |

Las opciones son las `GeoJSONOptions` de Leaflet (`style`, `onEachFeature`,
`filter`, …) más:

| Opción | Por defecto | Significado |
|---|---|---|
| `part` | — | Una parte de un nivel dividido (`"US-CA"`, `"unassigned"`) |
| `preview` | `false` | El preview simplificado en vez del archivo completo |
| `fit` | `false` | `true` o `FitBoundsOptions` para encuadrar con el bbox del índice |

Sin `style`, la capa usa el del sitio de documentación:
`{ weight: 1, color: "#00695c", fillColor: "#00695c", fillOpacity: 0.12 }`.
Un nivel publicado solo en partes (los municipios de Brasil) se concatena
salvo que se indique `part`.

## Subcapas por id estable

```ts
import { layerById } from "geoworld-leaflet";

const santiago = layerById(regions, "CHL:ADM1:CL-RM");
santiago?.setStyle({ fillOpacity: 0.5 });
santiago?.openTooltip();
```

`layerById` recorre `layer.getLayers()` buscando la subcapa cuya feature
lleva ese id; devuelve `undefined` si no hay ninguna.

## Bounds sin Leaflet

`toLatLngBounds(bbox)` convierte un bbox del índice en el literal
`[[sur, oeste], [norte, este]]` que acepta `map.fitBounds`, así que el mapa
puede encuadrarse antes de descargar ningún GeoJSON:

```ts
import { toLatLngBounds } from "geoworld-leaflet";
map.fitBounds(toLatLngBounds(await world.bbox("CHL", "ADM3")), { padding: [8, 8] });
```

`collection(client, iso3, level, { part?, preview? })` trae un nivel igual
que el adaptador, para usarlo con tus propias opciones de `L.GeoJSON`.

## Ejemplo

[`examples/leaflet.html`](https://github.com/andresgmg/World-GeoJSON/blob/main/examples/leaflet.html)
es una página completa con Leaflet desde una etiqueta script, selector de
territorio y nivel, tooltips y estilo al pasar el ratón. `just examples` la
sirve.

--8<-- "abbreviations.md"
