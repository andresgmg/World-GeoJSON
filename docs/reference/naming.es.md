# Nombres de archivos y carpetas

## La ruta canónica

```
data/{body}/{CODE}/{CODE}_{LEVEL}.geojson
```

| Segmento | Regla | Ejemplo |
|---|---|---|
| `body` | Nombre del cuerpo en minúsculas | `earth`, `moon`, `mars` |
| `CODE` | ISO 3166-1 alpha-3 en mayúsculas, o código específico del cuerpo | `CHL`, `NZL`, `MARS` |
| `LEVEL` | `ADM0`–`ADM3`, o `QUAD` para cuadrángulos planetarios | `ADM2` |

Ejemplo:

```
data/
└─ earth/
   └─ CHL/
      ├─ manifest.json
      ├─ CHL_ADM0.geojson
      ├─ CHL_ADM1.geojson          # regiones
      ├─ CHL_ADM3.geojson          # comunas
      └─ preview/
         ├─ CHL_ADM1.preview.geojson
         └─ CHL_ADM3.preview.geojson
```

Chile no tiene `CHL_ADM2.geojson` porque no existe un archivo abierto de
límites para sus provincias. **Los huecos en la secuencia de niveles son
esperables y están permitidos** — nombra cada archivo por el nivel que
realmente representa, en vez de renumerar para cerrar el hueco.

## Reglas

- Los archivos **deben** usar la extensión `.geojson`. No `.json`.
- Cada directorio de país **debe** contener un `manifest.json`
  ([formato](manifest.md)).
- Los previews simplificados **deben** vivir en `preview/` y llamarse
  `{stem}.preview.geojson`.
- Los nombres de directorios y archivos **no deben** contener espacios, tildes
  ni caracteres no ASCII. Las tildes van en los *valores* de las propiedades,
  nunca en las rutas.
- Un nivel administrativo por archivo. No agrupes niveles en un mismo
  `FeatureCollection`.

!!! note "¿Por qué no también `.json`?"

    El repositorio incluye hoy tanto `comunas.geojson` como `comunas.json`,
    idénticos byte a byte. Git los almacena como un único blob, así que la
    duplicación no cuesta nada en tamaño de repositorio — pero duplica el
    working tree y hace que el catálogo sea ambiguo sobre cuál ruta es la
    canónica. De aquí en adelante hay exactamente un archivo por dataset.

## Por qué ISO 3166-1 alpha-3

Alpha-3 (`CHL`) en vez de alpha-2 (`CL`):

- **Sin colisiones con códigos de subdivisión.** Los códigos alpha-2 de país se
  solapan con abreviaturas de estados de EE.UU. y otros esquemas
  subnacionales, lo que se vuelve un problema real en un repositorio que
  también guarda subdivisiones.
- **Es lo que usan los datasets de referencia.** geoBoundaries y GADM se
  indexan por alpha-3, así que cruzar datos con ellos no requiere tabla de
  traducción.
- **Más distinguible visualmente** en un listado de doscientos directorios.

El código alpha-2 se sigue registrando en `manifest.json` como `iso_a2`, porque
muchos consumidores lo quieren.

## Territorios y dependencias

Algunos territorios no soberanos tienen su propio código alpha-3. Úsalo, y
trátalos como entradas de primer nivel:

| Territorio | Código | No va bajo |
|---|---|---|
| Puerto Rico | `PRI` | `USA` |
| Groenlandia | `GRL` | `DNK` |
| Hong Kong | `HKG` | `CHN` |

Los territorios **sin** código alpha-3 propio se archivan como features ADM1 o
ADM2 del país que los administra, exactamente como los modela la fuente. No
inventes códigos. Si crees que un territorio necesita entrada propia y no tiene
código ISO, abre un issue en vez de elegir un código por tu cuenta — inventar
identificadores es como los registros se vuelven inutilizables.

!!! warning "Aquí es donde afloran las disputas de soberanía"

    Decidir si un lugar es un país, un territorio o una subdivisión es con
    frecuencia el fondo de una disputa política, no una cuestión de archivado.
    Este proyecto no juzga. Sigue a la fuente, regístrala en el manifiesto y
    lee [Fronteras disputadas](../about/disputed-boundaries.md) antes de abrir
    un PR sobre terreno en conflicto.

## Rutas planetarias

La Luna y Marte no tienen equivalente de ISO 3166 — no existe tal registro.
Usan el nombre del propio cuerpo como código, y sus features se nombran desde
el IAU Gazetteer of Planetary Nomenclature:

```
data/moon/MOON/MOON_QUAD.geojson
data/mars/MARS/MARS_QUAD.geojson
```

Los códigos de cuerpo se eligen de forma que nunca puedan colisionar con un
alpha-3 ISO real o futuro. Ver [Cuerpos planetarios](planetary.md).

--8<-- "abbreviations.md"
