# Adaptador MapLibre

`geoworld-maplibre` en [npm](https://www.npmjs.com/package/geoworld-maplibre):
helpers que ponen un nivel del [cliente JavaScript](javascript.md) en un mapa
[MapLibre GL JS](https://maplibre.org/). Cero dependencias en runtime;
`maplibre-gl` (≥ 2) y `geoworld` son peers. El código vive en
[`packages/js/geoworld-maplibre`](https://github.com/andresgmg/World-GeoJSON/tree/main/packages/js/geoworld-maplibre).

```bash
npm install geoworld geoworld-maplibre maplibre-gl
```

## Una llamada por nivel

```ts
import { createClient } from "geoworld";
import { addBoundaries } from "geoworld-maplibre";

const world = createClient({ version: "1.0.0" });
const regions = await addBoundaries(map, world, "CHL", "ADM1", { fit: true });

regions.source;   // "geoworld-CHL-ADM1"
regions.layers;   // ["geoworld-CHL-ADM1-fill", "geoworld-CHL-ADM1-line"]
regions.bbox;     // del índice, sin descarga
regions.remove(); // las capas y luego el source
```

`addBoundaries` falla pronto si el territorio o el nivel no existen, encuadra
el mapa con el bbox del índice cuando se pide (antes de que lleguen los
datos), descarga el nivel a través del cliente (verificado, cacheado), espera
a que el estilo admita un source y añade un source GeoJSON más una capa de
relleno y otra de línea. Lanza si el id del source ya está en el mapa: llama
a `remove()` en el handle anterior en vez de confiar en un reemplazo
silencioso.

| Opción | Por defecto | Significado |
|---|---|---|
| `part` | — | Una parte de un nivel dividido (`"US-CA"`, `"unassigned"`) |
| `preview` | `false` | El preview simplificado en vez del archivo completo |
| `source` | `geoworld-{ISO3}-{NIVEL}[-{parte}][-preview]` | Id del source |
| `fill` | `{ "fill-color": "#00695c", "fill-opacity": 0.15 }` | Paint del relleno, o `false` para no crear esa capa |
| `line` | `{ "line-color": "#00695c", "line-width": 1 }` | Paint de la línea, o `false` para no crear esa capa |
| `before` | — | Inserta las capas debajo de este id de capa |
| `fit` | `false` | `true` o `FitBoundsOptions` para encuadrar con el bbox del índice |

Un nivel publicado solo en partes (los municipios de Brasil) se concatena
salvo que se indique `part`; los niveles grandes se ven mejor con
`preview: true`.

## Estado de feature por id estable

Cada feature de World GeoJSON tiene un `id` estable como `CHL:ADM1:CL-RM`.
MapLibre no puede usarlo directamente: `promoteId` lee una *propiedad*, y un
id de feature no numérico se pierde al entrar en el source. Por eso el
adaptador construye los datos del source como copias superficiales con
`properties.id` repitiendo el id de la feature y pone `promoteId: "id"`, de
modo que tanto `feature-state` como `e.features[0].id` ven el id de World
GeoJSON.

```ts
import { clearFeatureState, setFeatureState } from "geoworld-maplibre";

const regions = await addBoundaries(map, world, "CHL", "ADM1", {
  fill: {
    "fill-color": "#00695c",
    "fill-opacity": ["case", ["boolean", ["feature-state", "hover"], false], 0.45, 0.15],
  },
});

let hovered: string | null = null;
map.on("mousemove", regions.layers[0], (e) => {
  const id = String(e.features?.[0]?.id ?? "");
  if (!id || id === hovered) return;
  if (hovered) clearFeatureState(map, regions.source, hovered, "hover");
  hovered = id;
  setFeatureState(map, regions.source, id, { hover: true });
});
map.on("mouseleave", regions.layers[0], () => {
  if (hovered) clearFeatureState(map, regions.source, hovered, "hover");
  hovered = null;
});
```

## Tus propias capas

```ts
import { collection, fitToBounds, sourceSpec, withIdProperty } from "geoworld-maplibre";

map.addSource("provinces", await sourceSpec(world, "CHL", "ADM2"));   // { type: "geojson", data, promoteId: "id" }
map.addLayer({ id: "provinces-outline", type: "line", source: "provinces" });
fitToBounds(map, await world.bbox("CHL", "ADM2"), { padding: 20 });
```

`collection(client, iso3, level, { part?, preview? })` devuelve la
FeatureCollection que daría el cliente, concatenando partes cuando no hay
archivo combinado; `withIdProperty(fc)` es el paso de promoción por sí solo;
`toLngLatBounds(bbox)` convierte un bbox del índice en lo que toma
`fitBounds`; `whenStyleReady(map)` resuelve cuando `addSource` es seguro.

!!! note "Antimeridiano"
    Los bbox del índice son valores ingenuos `[oeste, sur, este, norte]`. Un
    dataset que cruza el antimeridiano (Rusia, Fiyi, Estados Unidos con
    Alaska) da `[-180, …, 180, …]` y `fit` muestra el mundo entero.

## Ejemplo

[`examples/maplibre.html`](https://github.com/andresgmg/World-GeoJSON/blob/main/examples/maplibre.html)
es una página completa: selector de territorio y nivel, la capa con `fit` y
resaltado al pasar el ratón mediante feature state. `just examples` la sirve.

--8<-- "abbreviations.md"
