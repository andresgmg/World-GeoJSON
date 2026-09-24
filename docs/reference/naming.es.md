# Nombres de archivos y carpetas

## La ruta canónica

```
data/{body}/{CODE}/{CODE}_{LEVEL}.geojson
```

| Segmento | Regla | Ejemplo |
|---|---|---|
| `body` | Nombre del cuerpo en minúsculas | `earth`, `moon`, `mars` |
| `CODE` | ISO 3166-1 alpha-3 en mayúsculas, o código específico del cuerpo | `CHL`, `NZL`, `MARS` |
| `LEVEL` | `ADM0`–`ADM4`, o `QUAD` para cuadrángulos planetarios | `ADM2` |

Ejemplo — esto es lo que contiene realmente `data/earth/CHL/`:

```
data/
└─ earth/
   └─ CHL/
      ├─ manifest.json
      ├─ CHL_ADM0.geojson          # contorno del país (Natural Earth)
      ├─ CHL_ADM1.geojson          # 16 regiones
      ├─ CHL_ADM2.geojson          # 56 provincias
      ├─ CHL_ADM3.geojson          # 345 comunas, país completo
      ├─ ADM3/                     # …y partidas por región
      │  ├─ CL-AI.geojson
      │  ├─ CL-AN.geojson
      │  ├─ CL-AP.geojson
      │  └─ … (16 archivos)
      └─ preview/
         ├─ CHL_ADM0.preview.geojson
         ├─ CHL_ADM1.preview.geojson
         ├─ CHL_ADM2.preview.geojson
         └─ CHL_ADM3.preview.geojson
```

**Los huecos en la secuencia de niveles son esperables y están permitidos** —
nombra cada archivo por el nivel que realmente representa, en vez de renumerar
para cerrar el hueco. Guadalupe y Martinica publican `GLP_ADM4.geojson` y
`MTQ_ADM4.geojson` sin nada entre ADM0 y ADM4, porque ese es el nivel en el que
geoBoundaries publica sus comunas.

## El nivel municipal va partido por ADM1, cuando existe un ADM1

El nivel más profundo que publica este proyecto es el **tier municipal**.
Siempre que el país también tenga un ADM1 en este repositorio, ese tier va
partido en un archivo por cada padre ADM1:

```
data/{body}/{CODE}/{LEVEL}/{código ADM1}.geojson
```

Brasil tiene 5.570 municipios y México 2.457; un único archivo por país sería
de decenas de megabytes e inutilizable en un navegador. Partir por la primera
división mantiene todos los archivos pequeños, permite descargar solo el estado
que interesa, y deja todo dentro del presupuesto de tamaño por archivo.

Hoy existen niveles partidos para ARG, BLZ, BOL, BRA, CHL, DOM, ECU, MEX, PRY y
USA.

**Catorce territorios tienen tier municipal pero ningún ADM1 por el que
partirlo**, así que publican solo el archivo de país completo: COL, CRI, GLP,
GTM, GUF, GUY, HND, HTI, MTQ, PAN, PRI, SLV, SUR y VIR. (La mayoría son países
cuyo ADM1 en geoBoundaries es copyleft; ver la
[Hoja de ruta](../about/roadmap.md).)

### Códigos de parte

El código de parte es el **ISO 3166-2** de la unidad ADM1 tal como lo entrega
la fuente (`CL-RM`, `US-CA`). El `parts[].code` del manifiesto registra la
correspondencia para que nadie tenga que adivinarla. Dos cosas a saber:

- **Las erratas de origen se pasan tal cual, no se corrigen.** geoBoundaries
  codifica Dakota del Sur como `SU-SD` en vez de `US-SD`, así que sus 66
  condados viven en `USA/ADM2/SU-SD.geojson`. El campo `notes` del manifiesto
  de USA lo indica; el archivo se renombra en v1.0.0 junto con las demás
  correcciones de `shapeISO`.
- **Las unidades cuyo padre no se pudo determinar** van a
  `{LEVEL}/unassigned.geojson` en vez de descartarse, y el manifiesto registra
  el recuento en `unassigned`. Hoy: ARG ADM2 (8 — las comunas de la ciudad de
  Buenos Aires, que el ADM1 de origen omite), BRA ADM2 (3) y USA ADM2 (1).

El pipeline recurre a un slug del nombre del ADM1 si el código de origen viene
vacío; ninguna parte lo necesita actualmente.

### El archivo de país completo es condicional

El archivo combinado (`CHL_ADM3.geojson`) se publica **solo si queda por debajo
del presupuesto de 18 MiB por archivo**, que lo mantiene bajo el límite de
20 MB por archivo que documenta jsDelivr. Por encima de eso solo existen los
archivos partidos, y la página de catálogo del dataset lo indica
explícitamente.

Brasil es el ejemplo real: su ADM2 combinado pesaría 33 MB, así que
`data/earth/BRA/` tiene una carpeta `ADM2/` con 28 partes y ningún
`BRA_ADM2.geojson`. Las comunas de Chile caben (7 MB), así que existen ambas
formas.

Así que conviene consultar la página de catálogo o el manifiesto en vez de dar
por hecho que existe un combinado.

### `parentISO` es el padre inmediato, no la clave del archivo

El `parentISO` de una comuna nombra su *provincia* — el padre inmediato en la
jerarquía oficial — aunque el archivo en el que vive esté indexado por
*región*. Son cosas distintas y ambas son útiles, así que se registran las dos:
`parentISO` para la jerarquía y `adm1ISO` para el archivo al que pertenece.

Hoy solo Chile lleva `parentISO`; todas las partes partidas llevan `adm1ISO`.
El contrato de v1.0.0 añade `parentID` y `adm1ISO` a cada feature subnacional
— ver el [Diccionario de propiedades](properties.md).

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

    La raíz del repositorio incluye todavía tanto `comunas.geojson` como
    `comunas.json`, idénticos byte a byte. Git los almacena como un único blob,
    así que la duplicación no cuesta nada en tamaño de repositorio — pero
    duplica el working tree y hace que el catálogo sea ambiguo sobre cuál ruta
    es la canónica. Bajo `data/` hay exactamente un archivo por dataset.

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
