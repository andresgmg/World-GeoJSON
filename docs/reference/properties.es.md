# Diccionario de propiedades

Todas las claves de propiedad que aparecen en el corpus, qué significan y dónde
están presentes. Las tablas se han contrastado con los datos; la lista ordenada
de cada dataset está en su [`manifest.json`](manifest.md), en
`datasets[].properties`.

## Propiedades estándar

Definidas por este proyecto y presentes en **cada** feature de cada archivo.
Ver [Esquema de propiedades](schema.md).

| Clave | Tipo | Significado |
|---|---|---|
| `shapeName` | cadena | Nombre en el idioma local, con tildes |
| `shapeISO` | cadena | Código oficial — ISO 3166-2 si existe, si no el código nacional. Todavía no es una clave de join segura en todas partes; ver [Problemas conocidos](#problemas-conocidos-corregidos-en-v100) |
| `shapeGroup` | cadena | ISO 3166-1 alpha-3 del país, o código de cuerpo |
| `shapeType` | cadena | `ADM0`–`ADM4` (o `QUAD`, cuando existan datos planetarios) |

## Propiedades de jerarquía

Presentes en algunas features, no en todas. Exactamente dónde:

| Clave | Tipo | Significado | Presente en |
|---|---|---|---|
| `adm1ISO` | cadena | `shapeISO` del ADM1 al que pertenece la feature — el código que da nombre al archivo partido | Cada parte partida (`{LEVEL}/{código}.geojson`) y cada feature del `CHL_ADM3.geojson` combinado de Chile. Los archivos combinados de otros niveles partidos no lo llevan |
| `parentISO` | cadena | `shapeISO` de la unidad padre **inmediata** | Solo Chile, hoy: ADM2 (su región, p. ej. `CL-MA`) y ADM3 (su provincia, p. ej. `014`) |

!!! note "`parentISO` y `adm1ISO` no son lo mismo"

    En una comuna chilena, `parentISO` es su *provincia* — el padre inmediato
    en la jerarquía oficial — mientras que `adm1ISO` es su *región*, que es por
    lo que está indexado el archivo. Ambos son útiles y ambos se registran.

!!! info "Previsto para v1.0.0"

    El contrato de datos de v1.0.0 añade un `id` a nivel de Feature
    (`{ISO3}:{LEVEL}:{código}`), y `parentID` y `adm1ISO` en **todas** las
    features subnacionales, para que el anidamiento funcione igual en todos
    los países y no solo en Chile. Ver la [Hoja de ruta](../about/roadmap.md).

## Propiedades de origen — geoBoundaries

Cada feature tomada de geoBoundaries — ADM1 y niveles inferiores, 15.726
features hoy — lleva un campo extra:

| Clave | Tipo | Significado |
|---|---|---|
| `src_shape_id` | cadena | Identificador opaco propio de geoBoundaries para la unidad, p. ej. `66186276B69138566591314`. Estable dentro de una release de geoBoundaries; no es un código territorial |

Los otros cuatro campos de geoBoundaries (`shapeName`, `shapeISO`,
`shapeGroup`, `shapeType`) ya coinciden con el vocabulario estándar, que es
justamente por lo que este proyecto lo adoptó. Su `shapeID` se renombra a
`src_shape_id` al entrar; ningún archivo lleva una propiedad llamada `shapeID`.

## Propiedades de origen — Chile

Preservadas de la DPA 2023 de IDE Chile con el prefijo `src_`.

| Clave | Tipo | Presente en | Significado |
|---|---|---|---|
| `src_cut_reg` | cadena | ADM1, ADM2, ADM3 | Código CUT de región, dos caracteres |
| `src_cut_prov` | cadena | ADM2, ADM3 | Código CUT de provincia, tres caracteres |
| `src_cut_com` | cadena | ADM3 | Código CUT de comuna, cinco caracteres, con ceros a la izquierda |
| `src_region` | cadena | ADM2, ADM3 | Nombre de la región, sin el prefijo "Región de" |
| `src_provincia` | cadena | ADM3 | Nombre de la provincia |
| `src_superficie_km2` | número | ADM1 | Superficie oficial en **kilómetros cuadrados**. La única propiedad no textual del corpus |

CUT (*Código Único Territorial*) es el esquema nacional de codificación
territorial que usan el INE y SUBDERE. Los códigos anidan: la comuna `01402`
(Camiña) está en la provincia `014` (Tamarugal), que está en la región `01`
(Tarapacá).

## Propiedades que se descartan

Artefactos de exportación del software GIS de origen. No aportan información que
no se pueda recalcular, e inducen a error.

| Clave | Por qué se va |
|---|---|
| `objectid` | Número de fila interno de Esri. No es estable entre exportaciones |
| `st_area_sh` | Área precalculada en metros cuadrados, desde una proyección no declarada |
| `st_length_` | Perímetro precalculado, mismo problema |
| `shape_leng` | Duplicado de `st_length_`, truncado al límite de 10 caracteres de dBase |

## Problemas conocidos (corregidos en v1.0.0)

!!! warning "Lee esto antes de hacer joins por `shapeISO`"

    - En **22 datasets municipales** `shapeISO` contiene el id opaco de
      geoBoundaries (p. ej. `52423323B35289781006587`) en vez de un código
      territorial: el pipeline recurrió al `shapeID` de origen allí donde
      geoBoundaries entregó un `shapeISO` vacío. Afectados: ARG ADM2, BOL ADM3,
      BRA ADM2, COL ADM2, CRI ADM2, DOM ADM2, ECU ADM2, GLP ADM4, GTM ADM2,
      GUF ADM3, GUY ADM2, HND ADM2, HTI ADM3, MEX ADM2, MTQ ADM4, PAN ADM2,
      PRI ADM2, PRY ADM2, SLV ADM2, SUR ADM2, USA ADM2 y VIR ADM3.
    - `shapeISO` **no es único** en BLZ ADM2 (31 unidades llevan solo seis
      códigos distintos — el de su distrito), MEX ADM1 (`MX-MEX` dos veces) y
      ECU ADM1 (`EC-H` dos veces).
    - **Ninguna feature tiene todavía un `id` de nivel Feature** de GeoJSON.

    No trates `shapeISO` como una clave de join única garantizada hoy. v1.0.0
    añade `id` = `{ISO3}:{LEVEL}:{código}`, `parentID` y `adm1ISO` en todas las
    features, y deja de rellenar `shapeISO` con ids opacos.

## Trampas conocidas

!!! danger "Los códigos territoriales deben ser cadenas"

    Un número JSON no puede guardar un cero a la izquierda, así que cualquier
    fuente que almacene el `01402` de Chile como entero produce `1402` sin
    avisar, y los joins contra estadísticas oficiales no encuentran nada.
    `shapeISO` y todos los campos `src_cut_*` son cadenas.

!!! warning "`shapeISO` todavía no es una identidad segura en todas partes"

    Donde sea opaco o esté duplicado (ver arriba), usa `src_shape_id` como
    identidad en los datos de geoBoundaries y `shapeName` para mostrar.

!!! warning "El miembro `id` de GeoJSON todavía no se usa"

    Ningún archivo bajo `data/` fija hoy el `id` a nivel de Feature. La
    identidad vive en las propiedades hasta que v1.0.0 introduzca un `id`
    estable en cada feature.

## Regenerar esta página

Las listas de propiedades se registran por dataset en cada
[`manifest.json`](manifest.md). Esta página se mantiene a mano; generarla desde
los manifiestos está en la [Hoja de ruta](../about/roadmap.md).

--8<-- "abbreviations.md"
