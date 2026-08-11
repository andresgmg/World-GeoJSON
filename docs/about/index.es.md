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
| Territorios | 55 (América) |
| Datasets | 95 |
| Features | 16.195 |
| Cuerpos | 1 de 3 previstos |
| Licencia de datos | Solo permisivas, registrada por dataset |

Europa, África, Asia y Oceanía vienen después, un continente por release. Ver
[Hoja de ruta](roadmap.md).

Los cuatro archivos heredados en la raíz del repositorio son anteriores a las
convenciones y están obsoletos; ver
[Versionado y estabilidad](versioning.md#los-archivos-heredados-de-la-raiz).

## Mantenimiento

Andres Marquez ([@andresgmg](https://github.com/andresgmg)).

Las contribuciones son bienvenidas — ver
[Contribuir](../contributing/index.md).

## Licencias en una línea

El código es MIT. Los datos se licencian según su fuente, y algunas exigen
atribución. [Licencias y atribución](license.md) tiene el detalle, y aquí
importa más que en la mayoría de los proyectos.

--8<-- "abbreviations.md"
