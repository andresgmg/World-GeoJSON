# Acerca de

## Qué es esto

Un repositorio público de límites administrativos abiertos en GeoJSON, y las
convenciones que lo mantienen coherente a medida que crece.

## Historia

El proyecto empezó en 2023 como `chile-geojson`: dos archivos, las 16 regiones
y las 343 comunas de Chile, convertidos desde el conjunto de shapefiles de la
Biblioteca del Congreso Nacional. Toda su documentación era un README de dos
líneas.

Eso servía para dos archivos. No sobrevive al contacto con doscientos países.
El repositorio se renombró a **World-GeoJSON** para reflejar el objetivo más
amplio, y el trabajo actual consiste en poner las convenciones, el tooling y la
documentación en su sitio *antes* de que crezcan los datos — para que todo lo
que se añada después llegue con una forma consistente, en vez de tener que
adaptarlo a posteriori.

El alcance eventual incluye la Luna y Marte. No es una broma: existen datos
planetarios de límites y nomenclatura, tienen licencia abierta y nadie los
publica en un formato GeoJSON cómodo. Eso sí, requieren sus propias
convenciones, porque
[casi ningún supuesto terrestre se traslada](../reference/planetary.md).

## Estado actual

| | |
|---|---|
| Países | 1 (Chile) |
| Datasets | 2 (ADM1, ADM3) |
| Cuerpos | 1 de 3 previstos |
| Documentación | Este sitio |
| Convenciones de datos | Escritas, aún no aplicadas a los archivos existentes |

La distancia entre las convenciones escritas y los datos publicados es
deliberada y está registrada. Ver [Hoja de ruta](roadmap.md), y
[Referencia](../reference/index.md#estado-actual-frente-a-estado-objetivo) para
las diferencias concretas.

## Mantenimiento

Andres Marquez ([@andresgmg](https://github.com/andresgmg)).

Las contribuciones son bienvenidas — ver
[Contribuir](../contributing/index.md).

## Licencias en una línea

El código es MIT. Los datos se licencian según su fuente, y algunas exigen
atribución. [Licencias y atribución](license.md) tiene el detalle, y aquí
importa más que en la mayoría de los proyectos.

--8<-- "abbreviations.md"
