# World GeoJSON

Open, versioned GeoJSON administrative boundaries — starting with Chile,
growing toward every country on Earth, and eventually to the Moon and Mars.

Every dataset here is plain [RFC 7946](https://www.rfc-editor.org/rfc/rfc7946)
GeoJSON in WGS 84. No API key, no sign-up, no rate-limited service in front of
it: fetch a URL and you have boundaries.

<div class="grid cards" markdown>

-   :material-rocket-launch: **[Get started](get-started/index.md)**

    Find a dataset, copy a URL, load it in Leaflet, MapLibre, Python or QGIS.

-   :material-map-search: **[Catalog](catalog/index.md)**

    Every dataset, with feature counts, bounding boxes, property lists and
    download links.

-   :material-book-open-variant: **[Reference](reference/index.md)**

    The conventions: folder layout, admin levels, property schema, CRS policy,
    and how planetary bodies differ.

-   :material-source-pull: **[Contributing](contributing/index.md)**

    How to add a country — including which upstream sources are legally safe
    to use.

</div>

## Try it

```js
const url =
  "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/regiones.geojson";

const regions = await fetch(url).then((r) => r.json());
console.log(regions.features.length); // 16
```

## What this project is

A **data catalog**, not a service. The repository holds the files; this site
documents what is in them, where each one came from, and the conventions any
new contribution must follow.

Those conventions matter more than they might sound. The project began as a
single-country dump of two files with no schema, no coordinate system
declaration and no source attribution. Scaling that to hundreds of countries
without written rules produces a pile of mutually incompatible files. The
[Reference](reference/index.md) section is the contract that prevents it.

## What this project is not

- **Not a geocoder or a tile server.** These are boundary polygons. Rendering,
  search and spatial indexing are your application's job.
- **Not authoritative on sovereignty.** Boundaries follow whichever upstream
  source is named on each dataset's page. Where claims conflict, the project
  documents the disagreement rather than resolving it — see
  [Disputed boundaries](about/disputed-boundaries.md).
- **Not uniformly licensed.** The code in this repository is MIT. The *data* is
  licensed per source, and some sources require attribution. See
  [Licensing & attribution](about/license.md).

## Current status

**The Americas: 55 territories, 95 datasets, 16,195 features.**

Country outlines from Natural Earth, first-level and municipal divisions from
geoBoundaries, and Chile from IDE Chile's *División Política Administrativa*
2023. Every dataset is permissively licensed — copyleft sources are excluded,
which is why some countries have no first-level divisions yet.

Europe, Africa, Asia and Oceania follow, one continent per release.
[Roadmap](about/roadmap.md) has the sequence and the known gaps.

--8<-- "abbreviations.md"
