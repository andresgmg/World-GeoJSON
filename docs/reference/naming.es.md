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
      ├─ CHL_ADM1.geojson          # 16 regiones
      ├─ CHL_ADM2.geojson          # 56 provincias
      ├─ CHL_ADM3.geojson          # 345 comunas, país completo
      ├─ ADM3/                     # …y partidas por región
      │  ├─ CL-AP.geojson
      │  ├─ CL-RM.geojson
      │  └─ …
      └─ preview/
         ├─ CHL_ADM1.preview.geojson
         ├─ CHL_ADM2.preview.geojson
         └─ CHL_ADM3.preview.geojson
```

**Los huecos en la secuencia de niveles son esperables y están permitidos** —
nombra cada archivo por el nivel que realmente representa, en vez de renumerar
para cerrar el hueco.

## El nivel municipal va partido

El nivel más profundo que publica este proyecto es el **tier municipal**, y va
siempre partido en un archivo por cada padre ADM1:

```
data/{body}/{CODE}/{LEVEL}/{código del padre}.geojson
```

Brasil tiene 5.570 municipios y México 2.457; un único archivo por país sería
de decenas de megabytes e inutilizable en un navegador. Partir por la primera
división mantiene todos los archivos pequeños, permite descargar solo el estado
que interesa, y deja todo por debajo del techo de 20 MB del CDN.

El código del padre es el **ISO 3166-2** de la unidad ADM1 cuando se conoce
(`CL-RM`, `CL-AP`). Cuando no — geoBoundaries entrega con frecuencia un
`shapeISO` vacío — se recurre a un slug del nombre del ADM1, y `manifest.json`
registra la correspondencia para que nadie tenga que adivinarla.

### El archivo de país completo es condicional

El archivo combinado (`CHL_ADM3.geojson`) se publica **solo si queda por debajo
de 20 MB**, que es el mayor tamaño que sirve jsDelivr. Por encima de eso solo
existen los archivos partidos, y la página de catálogo del dataset lo indica
explícitamente.

Así que conviene consultar la página de catálogo o el manifiesto en vez de dar
por hecho que existe un combinado.

### `parentISO` es el padre inmediato, no la clave del archivo

El `parentISO` de una comuna nombra su *provincia* — el padre inmediato en la
jerarquía oficial — aunque el archivo en el que vive esté indexado por
*región*. Son cosas distintas y ambas son útiles, así que se registran las dos:
`parentISO` para la jerarquía y `adm1ISO` para el archivo al que pertenece.

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
