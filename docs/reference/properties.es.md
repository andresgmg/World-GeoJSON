# Diccionario de propiedades

Todas las claves de propiedad que aparecen en el corpus, qué significan y si
son estándar.

## Propiedades estándar

Definidas por este proyecto y presentes en cada feature. Ver
[Esquema de propiedades](schema.md).

| Clave | Tipo | Significado |
|---|---|---|
| `shapeName` | cadena | Nombre en el idioma local, con tildes |
| `shapeISO` | cadena | Código oficial de la unidad |
| `shapeGroup` | cadena | ISO 3166-1 alpha-3 del país, o código de cuerpo |
| `shapeType` | cadena | `ADM0`–`ADM3` o `QUAD` |
| `shapeID` | cadena | `{shapeGroup}-{shapeType}-{shapeISO}` |
| `parentISO` | cadena | `shapeISO` de la unidad padre |
| `shapeNameEn` | cadena | Exónimo en inglés, si difiere significativamente |

## Propiedades de origen — Chile

Preservadas de BCN / IDE Chile con el prefijo `src_`.

| Clave | Tipo | Significado |
|---|---|---|
| `src_cod_comuna` | entero | Código de comuna INE/SUBDERE. **Pierde el cero inicial** — ver abajo |
| `src_codregion` | entero | Código de región, 1–16 |
| `src_provincia` | cadena | Nombre de provincia. No existe archivo de límites para este nivel |
| `src_dis_elec` | entero | Distrito electoral |
| `src_cir_sena` | entero | Circunscripción senatorial |

La presencia de `dis_elec` y `cir_sena` es la señal más clara de que la fuente
original es el conjunto de shapefiles de la Biblioteca del Congreso Nacional y
no un archivo de límites del INE — las divisiones electorales no son algo que
una agencia de estadística distribuya junto a los límites administrativos.

## Propiedades heredadas (pre-migración)

Presentes en los archivos actuales de la raíz. Se van a eliminar o renombrar;
ver la [tabla de migración](schema.md#tabla-de-migracion-para-chile).

| Clave | Destino | Por qué |
|---|---|---|
| `Region` | → `shapeName` / `parentISO` | TitleCase inconsistente; clave sin tilde, valor con tilde |
| `Comuna` | → `shapeName` | |
| `Provincia` | → `src_provincia` | |
| `codregion` | → `src_codregion` | |
| `cod_comuna` | → `shapeISO` como cadena con cero a la izquierda | |
| `objectid` | **eliminada** | Número de fila interno de Esri, no estable |
| `st_area_sh` | **eliminada** | Área precalculada en m², proyección no declarada |
| `st_length_` | **eliminada** | Perímetro precalculado, mismo problema |
| `shape_leng` | **eliminada** | Duplicado de `st_length_`, truncado al límite de 10 caracteres de dBase |
| `area_km` | **eliminada** | Área precalculada en km² — unidades distintas a `st_area_sh` |

## Trampas conocidas

!!! danger "`cod_comuna` pierde el cero inicial"

    Guardado como número JSON, así que Camiña es `1402`. El código oficial es
    la cadena `01402`. Afecta a todas las comunas de las regiones 1 a 9, y los
    joins contra estadísticas oficiales no encuentran nada sin avisar.

    Los números JSON no pueden representar un cero a la izquierda en absoluto,
    y por eso `shapeISO` es siempre una cadena.

!!! warning "Las unidades de área difieren entre archivos"

    `regiones.geojson` lleva `area_km` en **kilómetros cuadrados**.
    `comunas.geojson` lleva `st_area_sh` en **metros cuadrados**. Ninguno lo
    documenta. Compáralos ingenuamente y tu resultado se desvía por 10⁶.

!!! warning "`Region` va sin tilde como clave y con tilde como valor"

    La clave es `"Region"`; el valor es `"Región de Tarapacá"`. El código que
    pase los nombres de clave por un normalizador no encontrará el campo.

!!! warning "El miembro `id` de GeoJSON no es fiable"

    Presente en 5 de 343 features de comunas, ausente en las 16 regiones. Los
    valores no son correlativos y no se corresponden con la posición. Usa
    `shapeID` en las propiedades.

## Regenerar esta página

Las listas de propiedades se registran por dataset en cada
[`manifest.json`](manifest.md). Esta página se mantiene hoy a mano; generarla
desde los manifiestos está en la [Hoja de ruta](../about/roadmap.md).

--8<-- "abbreviations.md"
