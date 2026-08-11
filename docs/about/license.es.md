# Licencias y atribución

## Dos licencias, no una

El repositorio incluye hoy un único archivo `LICENSE` MIT. Eso es insuficiente,
porque **los datos no son código** y ambos necesitan términos distintos.

| Qué | Licencia |
|---|---|
| Scripts, configuración, documentación | **MIT** |
| Datos aportados por este proyecto | **CC BY 4.0** |
| Datos procedentes de una fuente externa | **La licencia de la fuente**, registrada por dataset |

MIT es una licencia de software. Habla de "el Software" y de exenciones de
garantía; no dice nada coherente sobre una base de datos. Las licencias
Creative Commons están diseñadas para contenido, y CC BY 4.0 cubre
explícitamente los derechos *sui generis* de base de datos, que existen en la
UE y son relevantes para datos de límites.

## La licencia de origen siempre manda

Este proyecto no puede conceder derechos que no tiene. Un dataset obtenido bajo
CC BY 4.0 sigue siendo CC BY 4.0 diga lo que diga esta página, y su requisito
de atribución te alcanza a ti.

La página de catálogo de cada dataset nombra su fuente y su licencia. Cada
`manifest.json` las registra:

```json
"source": {
  "name": "geoBoundaries",
  "url": "https://www.geoboundaries.org/",
  "license": "CC-BY-4.0",
  "retrieved": "2026-08-10"
}
```

**Consulta la página del dataset antes de redistribuir.** No hay una respuesta
única para todo el repositorio, y nunca la habrá.

## Nada de copyleft

Todos los datasets aquí están bajo una licencia **permisiva** — CC BY, CC0,
dominio público o equivalente. Las fuentes share-alike quedan excluidas, y el CI
aplica la [lista blanca](../contributing/sources.md#la-lista-blanca).

El motivo es ODbL en concreto. Define una *Base de Datos Derivada*, y mezclar un
solo dataset ODbL en esta colección colocaría discutiblemente la colección
entera bajo ODbL — cambiando los términos para todos los consumidores
existentes sin que se enteren. No es un intercambio que este proyecto vaya a
hacer, aunque cueste cobertura real: un tercio de las entradas de América de
geoBoundaries quedan descartadas por esta vía.

Los huecos se registran en la [Hoja de ruta](roadmap.md). Se cierran encontrando
una fuente permisiva, no relajando la regla.

## Condiciones que acompañan a una concesión

Algunas licencias abiertas llegan con obligaciones más allá de la atribución, y
esas se registran en `source.license_note` del manifiesto.

Chile es el ejemplo actual. La DPA 2023 de IDE Chile se publica como CC BY, pero
la cartografía subyacente circula bajo la **Resolución N°50 de 2019 de DIFROL**,
y las normas chilenas piden que los productos derivados se revisen igualmente.
Es lo habitual en la cartografía oficial chilena — existe por la reclamación
antártica y por las fronteras terrestres — y aquí se reproduce en vez de
omitirse en silencio.

## Atribución

Para los datasets que la exijan, atribuye tanto a la fuente original como a
este proyecto:

> Límites de [nombre de la fuente], vía World GeoJSON
> (<https://github.com/andresgmg/World-GeoJSON>), bajo licencia [licencia].

Para los datos actuales de Chile:

> Límites de la Biblioteca del Congreso Nacional de Chile (BCN) / IDE Chile,
> vía World GeoJSON.

## Cita

```bibtex
@misc{worldgeojson,
  author       = {Marquez, Andres},
  title        = {World GeoJSON: open administrative boundaries},
  year         = {2026},
  howpublished = {\url{https://github.com/andresgmg/World-GeoJSON}}
}
```

Cita también el dataset *de origen* cuando tu trabajo dependa de la geometría y
no del empaquetado.

## Aportar datos

Al contribuir, confirmas que:

1. Tienes derecho a aportar los datos.
2. La licencia de origen permite la redistribución, incluido el uso comercial.
3. El bloque `source` del manifiesto es exacto y completo.

Ver [Fuentes aprobadas y licencias](../contributing/sources.md) para saber qué
es aceptable — y en concreto por qué **GADM no lo es**.

## Sin garantía

Estos límites se ofrecen tal cual. No son aptos para fines legales, de
navegación ni catastrales. Se sabe que el número de features es incompleto en
algunos casos — Chile incluye 343 de 346 comunas — y la exactitud de la
geometría es la que aportara la fuente original.

## Fronteras disputadas

Los límites siguen a la fuente declarada. Su inclusión no es una afirmación
sobre soberanía. Ver [Fronteras disputadas](disputed-boundaries.md).

--8<-- "abbreviations.md"
