# Esquema de propiedades

Cada feature lleva un pequeño conjunto de propiedades estándar, más lo que
haya aportado la fuente original.

## Propiedades obligatorias

| Propiedad | Tipo | Significado |
|---|---|---|
| `shapeName` | cadena | Nombre de la unidad, en el idioma local, con las tildes correctas |
| `shapeISO` | cadena | Código oficial de la unidad — ISO 3166-2 si existe, si no el código nacional |
| `shapeGroup` | cadena | ISO 3166-1 alpha-3 del país que la contiene, o código de cuerpo |
| `shapeType` | cadena | `ADM0`, `ADM1`, `ADM2`, `ADM3` o `QUAD` |

Estos nombres coinciden deliberadamente con
[geoBoundaries](https://www.geoboundaries.org/). Adoptar un vocabulario ya
existente significa que quien ya procesa datos de geoBoundaries puede leer
estos archivos sin cambios, y elimina toda una categoría de discusión estéril
en la revisión.

## Propiedades opcionales

| Propiedad | Tipo | Significado |
|---|---|---|
| `shapeID` | cadena | Identificador único y estable: `{shapeGroup}-{shapeType}-{shapeISO}` |
| `parentISO` | cadena | `shapeISO` de la unidad padre, para el anidamiento |
| `shapeNameEn` | cadena | Exónimo en inglés, cuando difiere de forma significativa |

## Las propiedades de origen se preservan, no se borran

Los atributos originales se conservan con el prefijo `src_`:

```json
{
  "shapeName": "Camiña",
  "shapeISO": "01402",
  "shapeGroup": "CHL",
  "shapeType": "ADM3",
  "parentISO": "CL-TA",
  "src_cod_comuna": 1402,
  "src_codregion": 1,
  "src_provincia": "Iquique",
  "src_dis_elec": 2,
  "src_cir_sena": 2
}
```

El razonamiento: la información que descartas se pierde, y siempre hay alguien
que necesita justo el campo que decidiste que era irrelevante. `dis_elec` y
`cir_sena` son el distrito electoral y la circunscripción senatorial de Chile —
irrelevantes para la mayoría, esenciales para quien haga análisis electoral. El
prefijo los conserva sin dejar que colisionen con el vocabulario estándar.

## Qué se descarta

Los artefactos de exportación del software GIS de origen son la excepción. No
aportan información que no se pueda recalcular, y además inducen a error:

| Propiedad | Por qué se va |
|---|---|
| `objectid` | Número de fila interno de Esri. No es estable entre exportaciones ni significativo. |
| `st_area_sh` | Área precalculada en **metros cuadrados**, desde una proyección no declarada |
| `st_length_` | Perímetro precalculado, mismo problema |
| `shape_leng` | Duplicado de `st_length_`, truncado al límite de 10 caracteres de dBase |
| `area_km` | Área precalculada en **kilómetros cuadrados** |

!!! warning "Las áreas precalculadas no se pueden comparar entre fuentes"

    Cada productor usa unidades y proyecciones distintas para un campo que
    suena igual, y rara vez documenta ninguna de las dos. La DPA de Chile trae
    `SUPERFICIE` en km²; las exportaciones Esri traen `st_area_sh` en m².
    Compáralos ingenuamente y el resultado se desvía por un factor de un
    millón.

    Cuando un campo así se preserva, se le da un nombre que lleva la unidad
    (`src_superficie_km2`). Para cualquier cosa de la que dependas, calcula el
    área tú mismo desde la geometría, en una proyección adecuada a tu zona de
    interés — ver
    [Recetas](../get-started/recipes.md#calcular-el-area-correctamente).

## Ejemplo trabajado: Chile

Chile se construye desde la *División Política Administrativa* 2023 de IDE
Chile, cuyos atributos encajan limpiamente en el conjunto estándar:

| Campo de origen | Pasa a ser |
|---|---|
| `REGION` | `shapeName` en ADM1 |
| `PROVINCIA` | `shapeName` en ADM2 |
| `COMUNA` | `shapeName` en ADM3 |
| `CUT_REG` | `shapeISO` en ADM1 vía el lookup ISO 3166-2; `src_cut_reg` en el resto |
| `CUT_PROV` | `shapeISO` en ADM2, `parentISO` en ADM3 |
| `CUT_COM` | `shapeISO` en ADM3 |
| `SUPERFICIE` | `src_superficie_km2` |

Una comuna queda así:

```json
{
  "shapeName": "Camiña",
  "shapeISO": "01402",
  "shapeGroup": "CHL",
  "shapeType": "ADM3",
  "parentISO": "011",
  "adm1ISO": "CL-TA",
  "src_cut_com": "01402",
  "src_cut_prov": "011",
  "src_cut_reg": "01",
  "src_provincia": "Tamarugal",
  "src_region": "Tarapacá"
}
```

### `shapeISO` es siempre una cadena

El código oficial INE/SUBDERE de Camiña es `01402` — cinco caracteres, cero
inicial incluido. Todas las comunas de las regiones 1 a 9 lo llevan.

Un **número** JSON no puede representar un cero a la izquierda en absoluto, así
que una fuente que los guarde como enteros convierte `01402` en `1402` sin
avisar, y cualquier join contra estadísticas oficiales deja de encontrar nada.
El shapefile de la DPA ya guarda los códigos CUT como cadenas, que es una de las
razones por las que se eligió frente a las alternativas.

Por eso `shapeISO` es siempre una cadena, nunca un número, aunque parezca
numérico.

!!! note "Aquí los códigos son nacionales, no ISO 3166-2"

    Chile tiene códigos ISO 3166-2 para sus regiones (`CL-TA`) pero no para
    provincias ni comunas, así que esos niveles llevan el código CUT nacional.
    Es el respaldo documentado: ISO 3166-2 donde exista, código nacional en
    caso contrario.

## El `id` a nivel de feature

El miembro `id` de nivel superior de GeoJSON está hoy presente en solo **5 de
343** features de comunas, con valores no correlativos (`0`, `1`, `3`, `142`,
`155`) que no se corresponden con la posición. Quien se apoye en `feature.id`
obtiene `undefined` el 98,5% de las veces. `regiones.geojson` no tiene ninguno,
así que los dos archivos también son inconsistentes entre sí.

La regla de aquí en adelante: o todas las features de un archivo tienen un `id`
estable y significativo, o ninguna lo tiene. Usa `shapeID` en las propiedades
para la identidad; no dependas del miembro `id` de GeoJSON.

## Nombres y codificación

- Los archivos son UTF-8. `shapeName` **debe** llevar las tildes correctas:
  `Región de Ñuble`, `Camiña`, `La Araucanía`.
- Usa un apóstrofo ASCII (`'`), no uno tipográfico. `Región del Libertador
  Bernardo O'Higgins` ya lo hace así; respetarlo importa para la comparación de
  cadenas.
- No abrevies. El actual `Región de Aysén del Gral.Ibañez del Campo` está mal
  de tres formas — "Gral." abreviado, falta el espacio tras el punto, y falta
  la tilde en "Ibáñez". Normalizarlo es parte de la migración.

--8<-- "abbreviations.md"
