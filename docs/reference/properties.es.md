# Diccionario de propiedades

Todas las claves de propiedad que aparecen en el corpus, qué significan y si son
estándar.

## Propiedades estándar

Definidas por este proyecto y presentes en cada feature. Ver
[Esquema de propiedades](schema.md).

| Clave | Tipo | Significado |
|---|---|---|
| `shapeName` | cadena | Nombre en el idioma local, con tildes |
| `shapeISO` | cadena | Código oficial — ISO 3166-2 si existe, si no el código nacional |
| `shapeGroup` | cadena | ISO 3166-1 alpha-3 del país, o código de cuerpo |
| `shapeType` | cadena | `ADM0`–`ADM3` o `QUAD` |
| `parentISO` | cadena | `shapeISO` de la unidad padre **inmediata** |
| `adm1ISO` | cadena | ISO 3166-2 del ADM1 al que pertenece la feature. Presente en los niveles municipales partidos, donde indica el archivo en el que vive |
| `shapeID` | cadena | `{shapeGroup}-{shapeType}-{shapeISO}` |
| `shapeNameEn` | cadena | Exónimo en inglés, si difiere significativamente |

!!! note "`parentISO` y `adm1ISO` no son lo mismo"

    En una comuna chilena, `parentISO` es su *provincia* — el padre inmediato
    en la jerarquía oficial — mientras que `adm1ISO` es su *región*, que es por
    lo que está indexado el archivo. Ambos son útiles y ambos se registran.

## Propiedades de origen — Chile

Preservadas de la DPA 2023 de IDE Chile con el prefijo `src_`.

| Clave | Tipo | Significado |
|---|---|---|
| `src_cut_com` | cadena | Código CUT de comuna, cinco caracteres, con ceros a la izquierda |
| `src_cut_prov` | cadena | Código CUT de provincia, tres caracteres |
| `src_cut_reg` | cadena | Código CUT de región, dos caracteres |
| `src_provincia` | cadena | Nombre de la provincia |
| `src_region` | cadena | Nombre de la región |
| `src_superficie_km2` | número | Superficie oficial en **kilómetros cuadrados** |

CUT (*Código Único Territorial*) es el esquema nacional de codificación
territorial que usan el INE y SUBDERE. Los códigos anidan: la comuna `01402`
está en la provincia `011`, que está en la región `01`.

## Propiedades de origen — geoBoundaries

Los países tomados de geoBoundaries llevan sus cinco campos nativos. Cuatro ya
coinciden con el vocabulario estándar, que es justamente por lo que este
proyecto lo adoptó.

| Clave | Nota |
|---|---|
| `shapeName`, `shapeGroup`, `shapeType` | Se usan directamente |
| `shapeISO` | **Frecuentemente vacío.** geoBoundaries lo documenta como "cuando esté disponible", y en la práctica muchos países entregan `""` |
| `shapeID` | Un identificador interno opaco, no un código territorial |

## Propiedades que se descartan

Artefactos de exportación del software GIS de origen. No aportan información que
no se pueda recalcular, e inducen a error.

| Clave | Por qué se va |
|---|---|
| `objectid` | Número de fila interno de Esri. No es estable entre exportaciones |
| `st_area_sh` | Área precalculada en metros cuadrados, desde una proyección no declarada |
| `st_length_` | Perímetro precalculado, mismo problema |
| `shape_leng` | Duplicado de `st_length_`, truncado al límite de 10 caracteres de dBase |

## Trampas conocidas

!!! danger "Los códigos territoriales deben ser cadenas"

    Un número JSON no puede guardar un cero a la izquierda, así que cualquier
    fuente que almacene el `01402` de Chile como entero produce `1402` sin
    avisar, y los joins contra estadísticas oficiales no encuentran nada.
    `shapeISO` y todos los campos `src_cut_*` son cadenas.

!!! warning "`shapeISO` puede venir vacío en datos de geoBoundaries"

    No des por hecho que está poblado. Usa `shapeName` para mostrar y `shapeID`
    para identidad cuando falte el código ISO.

!!! warning "El miembro `id` de GeoJSON no se usa"

    La identidad vive en las propiedades. Los archivos de este repositorio no
    dependen del miembro `id` de nivel superior, y quien los consuma tampoco
    debería.

## Regenerar esta página

Las listas de propiedades se registran por dataset en cada
[`manifest.json`](manifest.md). Esta página se mantiene a mano; generarla desde
los manifiestos está en la [Hoja de ruta](../about/roadmap.md).

--8<-- "abbreviations.md"
