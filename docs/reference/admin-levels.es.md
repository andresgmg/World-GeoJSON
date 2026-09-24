# Niveles administrativos

## Definiciones

| Nivel | Significado |
|---|---|
| **ADM0** | El contorno del país o cuerpo |
| **ADM1** | Divisiones de primer nivel |
| **ADM2** | Divisiones de segundo nivel |
| **ADM3** | Divisiones de tercer nivel |
| **ADM4** | Divisiones de cuarto nivel — se publican solo donde la fuente sitúa ahí el tier municipal (Guadalupe y Martinica hoy) |

Siguen la semántica de [geoBoundaries](https://www.geoboundaries.org/) y GADM,
para que los datasets de este proyecto puedan cruzarse con los suyos sin paso
de traducción.

## Los números son estructurales, no semánticos

Es la regla que más confusión causa, así que conviene decirla claro: **ADM1 no
significa "provincia".** Significa "el primer nivel de subdivisión que tenga
este país, se llame como se llame". El término local se registra aparte, como
`adm1_term` y `municipal_term` en `pipeline/src/wgj/tables/countries.json` — no
en los manifiestos.

| País | ADM1 | ADM2 | ADM3 |
|---|---|---|---|
| Chile | Región | Provincia | Comuna |
| Argentina | Provincia | Departamento | Municipio |
| Francia | Región | Departamento | Comuna |
| Estados Unidos | Estado | Condado | — |
| Japón | Prefectura | Municipio | — |

Chile ilustra bien por qué la numeración tiene que ser estructural. Las comunas
son el nivel con el que todo el mundo trabaja en la práctica — son la unidad
del censo, de las elecciones y del gobierno local — pero son **ADM3**, no ADM2,
porque entre ellas y las regiones hay un nivel de provincia. Numerarlas como
ADM2 por ser el nivel más prominente haría que los niveles de Chile no
concordaran con los de ningún otro país, y rompería cualquier consulta
multipaís que agrupe por nivel.

!!! info "Cuando los niveles de un país no encajan limpiamente"

    Pasa a menudo. Algunos países tienen jerarquías solapadas, ciudades con
    estatus especial que se saltan un nivel, o divisiones que cambiaron hace
    poco. Registra lo que modela la fuente, describe el desajuste en el campo
    `notes` del manifiesto, y no reorganices la jerarquía en silencio para que
    parezca ordenada.

## El tier municipal

Este proyecto publica tres cosas por país: el contorno (ADM0), las divisiones de
primer nivel (ADM1) y el **tier municipal** — el nivel de gobierno local en el
que la gente vive de verdad. Ahí se detiene.

El tier municipal es un objetivo *semántico*, no un número de nivel, y su número
varía:

| País | Tier municipal | Nivel |
|---|---|---|
| Chile | Comuna | **ADM3** |
| México | Municipio | ADM2 |
| Brasil | Município | ADM2 |
| Estados Unidos | Condado | ADM2 |
| Bolivia | Municipio | **ADM3** |
| Haití | Comuna | **ADM3** |
| Costa Rica | Cantón | ADM2 |
| Guadalupe, Martinica | Comuna | **ADM4** |

Como no se puede inferir de los datos, la correspondencia se cura a mano en
`pipeline/src/wgj/tables/countries.json` y es la única pieza de este pipeline
que siempre necesitará criterio humano.

Los niveles más profundos — los *corregimientos* de Panamá, los *distritos* de
Costa Rica — quedan fuera de alcance. Existen en pocos países, los tamaños de
archivo crecen mucho y casi nadie los necesita.

El nivel municipal va **partido en un archivo por padre ADM1 siempre que exista
un ADM1**. Catorce territorios tienen tier municipal pero ningún ADM1 aquí
(sobre todo porque su ADM1 en geoBoundaries es copyleft), así que publican un
único archivo de país completo; ver
[Nombres de archivos y carpetas](naming.md#el-nivel-municipal-va-partido-por-adm1-cuando-existe-un-adm1).

## Expectativas de cobertura

- **ADM0 y ADM1 son la prioridad.** Son los niveles que más consumidores
  necesitan y los que están disponibles con licencia abierta de forma más
  fiable.
- **El tier municipal donde exista una fuente con licencia abierta.**

Una entrada de país con solo ADM1 es bienvenida. La cobertura parcial es normal
y el catálogo muestra exactamente qué niveles existen para cada entrada.

!!! warning "Los números de nivel tampoco son consistentes entre fuentes"

    La numeración ADM de geoBoundaries se asigna por país y no siempre coincide
    con la jerarquía oficial — publica Guadalupe solo en ADM4, Puerto Rico sin
    ADM0 ni ADM1, y Martinica en ADM3 y ADM4 sin nada en medio. Nunca supongas
    que ADM2 significa lo mismo en dos países.

## El anidamiento debe ser consistente

Cuando se aportan varios niveles de un país:

- Cada feature ADM2 **debe** anidar dentro de exactamente una feature ADM1.
- La unión de las features ADM1 **debería** igualar el contorno ADM0, dentro de
  la tolerancia de la geometría de origen.
- Las features **deben** llevar una referencia a su padre, y la llevan, en
  todas partes: `parentID` — el `id` de la feature padre — y `parentISO` en
  cada feature que tiene un nivel padre en el catálogo, y `adm1ISO` en cada
  feature por debajo de un ADM1. En los datos de geoBoundaries el padre se
  deriva por unión espacial de mayor solapamiento, porque la fuente no entrega
  referencia al padre; las 12 unidades que no solapan con ningún padre se
  conservan con `adm1ISO: "unassigned"` y sin `parentID`. El CI comprueba que
  cada `parentID` resuelve — ver [Esquema de propiedades](schema.md).

No mezcles añadas. Los límites cambian: un archivo ADM1 de 2019 combinado con
uno ADM2 de 2024 no anidará, y el desajuste es difícil de detectar a simple
vista. Registra la añada en el manifiesto (`src_year`).

## Chile, nivel por nivel

Chile es el único país con la escalera completa, y conviene saber exactamente
qué hay:

| Nivel | Archivo | Contenido | Fuente |
|---|---|---|---|
| ADM0 | `CHL_ADM0.geojson` | Contorno del país | Natural Earth 10m |
| ADM1 | `CHL_ADM1.geojson` | 16 regiones | IDE Chile / SUBDERE DPA 2023 |
| ADM2 | `CHL_ADM2.geojson` | 56 provincias | IDE Chile / SUBDERE DPA 2023 |
| ADM3 | `CHL_ADM3.geojson` + `ADM3/` (16 partes) | 345 comunas | IDE Chile / SUBDERE DPA 2023 |

- **345 de 346 comunas.** Solo falta Antártica (`12202`): el paquete DPA
  excluye la reclamación antártica chilena, así que es una decisión de la
  fuente, no una pérdida de procesamiento. Isla de Pascua y Juan Fernández
  están presentes.
- El nivel provincial existe como geometría dibujable, no solo como propiedad
  de cada comuna — el `parentISO` de cada comuna apunta al `shapeISO` de su
  provincia, y su `parentID` al `id` de la provincia (`CHL:ADM2:014` para
  Camiña).

Los archivos heredados de la raíz (BCN, 343 comunas, sin provincias) son el
dataset más antiguo al que esto reemplaza; ver
[Versionado y estabilidad](../about/versioning.md).

--8<-- "abbreviations.md"
