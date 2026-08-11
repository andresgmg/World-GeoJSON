# About

## What this is

A public repository of open GeoJSON administrative boundaries, and the
conventions that keep it coherent as it grows.

## History

The project started in 2023 as `chile-geojson`: two files, Chile's 16 regions
and 343 communes, converted from the Biblioteca del Congreso Nacional's
shapefile set. Its entire documentation was a two-line README.

That was fine for two files. It does not survive contact with two hundred
countries. The repository was renamed **World-GeoJSON** to reflect the wider
goal, and the current work is putting the conventions, tooling and
documentation in place *before* the data grows — so that everything added
afterwards arrives in a consistent shape, rather than being retrofitted later.

The eventual scope includes the Moon and Mars. That is not a joke: planetary
boundary and nomenclature data exists, it is openly licensed, and nobody
publishes it in a convenient GeoJSON form. It does require its own conventions,
because [almost nothing about Earth's assumptions carries
over](../reference/planetary.md).

## Current state

| | |
|---|---|
| Countries | 1 (Chile) |
| Datasets | 3 (ADM1, ADM2, ADM3) |
| Features | 417 |
| Bodies | 1 of 3 planned |
| Data licence | CC BY 4.0, single source |

The Americas are next, then one continent per release. See
[Roadmap](roadmap.md).

The four legacy files in the repository root predate the conventions and are
deprecated; see
[Versioning & stability](versioning.md#the-legacy-root-files).

## Maintainer

Andres Marquez ([@andresgmg](https://github.com/andresgmg)).

Contributions are welcome — see [Contributing](../contributing/index.md).

## Licensing in one line

Code is MIT. Data is licensed per source, and some sources require attribution.
[Licensing & attribution](license.md) has the detail, and it matters more than
most projects' licence pages.

--8<-- "abbreviations.md"
