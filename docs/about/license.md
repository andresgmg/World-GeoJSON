# Licensing & attribution

## Two licences, not one

The repository currently ships a single MIT `LICENSE` file. That is
insufficient, because **data is not code** and the two need different terms.

| What | Licence |
|---|---|
| Scripts, configuration, documentation | **MIT** |
| Data contributed by this project | **CC BY 4.0** |
| Data from an upstream source | **The upstream licence**, recorded per dataset |

MIT is a software licence. It talks about "the Software" and warranty
disclaimers; it says nothing coherent about a database. Creative Commons
licences are designed for content, and CC BY 4.0 explicitly covers *sui
generis* database rights, which exist in the EU and matter for boundary data.

## The upstream licence always wins

This project cannot grant rights it does not have. A dataset sourced under CC
BY 4.0 stays CC BY 4.0 no matter what this page says, and its attribution
requirement passes through to you.

The licence is recorded **per dataset**, because the levels of one country
routinely come from different providers: Brazil's outline is public domain,
its states CC BY 2.5 and its municipalities CC BY 3.0 IGO. Every
`manifest.json` carries `datasets[].license`, and rolls the distinct values up
into `source.license` — `"mixed"` plus a `licenses` list when they differ.
Chile, abridged:

```json
"source": {
  "name": "IDE Chile / SUBDERE — División Política Administrativa 2023",
  "url": "https://www.geoportal.cl/",
  "license": "mixed",
  "retrieved": "2026-08-11",
  "licenses": ["CC-BY-4.0", "public-domain"]
},
"datasets": [
  { "level": "ADM0", "license": "public-domain", "src_provider": "Natural Earth", "…": "…" },
  { "level": "ADM1", "license": "CC-BY-4.0", "…": "…" }
]
```

Every dataset's catalog page names its source and licence too.
**Check the dataset page before redistributing.** There is no single answer for
the whole repository, and there never will be.

## No copyleft

Every dataset here is under a **permissive** licence — CC BY, CC0, public
domain or equivalent. Share-alike sources are excluded, and CI enforces the
[allow-list](../contributing/sources.md#the-allow-list) on every
`datasets[].license` and every `source.licenses` entry.

The reason is ODbL specifically. It defines a *Derivative Database*, and mixing
one ODbL dataset into this collection would arguably place the entire
collection under ODbL — changing the terms for every existing consumer without
their knowledge. That is not a trade this project will make, even though it
costs real coverage: a third of geoBoundaries' Americas entries are ruled out
this way, and 15 countries have no ADM1 here as a result.

Gaps are recorded on the [Roadmap](roadmap.md). They get closed by finding a
permissive source, not by relaxing the rule.

## Conditions that travel with a grant

Some open licences arrive with obligations beyond attribution. Those belong in
the manifest's `notes` field, beside the source they apply to — the manifest
has no separate licence-note field.

Chile is the current example. IDE Chile's DPA 2023 is published as CC BY, but
the underlying cartography circulates under **Resolución N°50 de 2019 of
DIFROL**, and Chilean rules ask that products derived from it be reviewed
equally. This is standard for Chilean official cartography — it exists because
of the Antarctic claim and the land borders — and it is reproduced here rather
than quietly dropped.

## Attribution

For datasets requiring it, attribute both the original source and this project:

> Boundaries from [source name], via World GeoJSON
> (<https://github.com/andresgmg/World-GeoJSON>), licensed under [licence].

For Chile's current data under `data/earth/CHL/`:

> Boundaries from IDE Chile / SUBDERE (División Política Administrativa 2023,
> CC BY 4.0) and Natural Earth, via World GeoJSON.

For the legacy `regiones.geojson` and `comunas.geojson` at the repository root:

> Boundaries from the Biblioteca del Congreso Nacional de Chile (BCN), via
> World GeoJSON.

## Citation

```bibtex
@misc{worldgeojson,
  author       = {Marquez, Andres},
  title        = {World GeoJSON: open administrative boundaries},
  year         = {2026},
  howpublished = {\url{https://github.com/andresgmg/World-GeoJSON}}
}
```

Cite the *source* dataset as well where your work depends on the geometry
rather than on the packaging.

## Contributing data

By contributing, you confirm that:

1. You have the right to contribute the data.
2. The upstream licence permits redistribution, including commercial use.
3. The `source` block and every `datasets[].license` in the manifest are
   accurate and complete.

See [Approved sources & licensing](../contributing/sources.md) for what is
acceptable — and specifically for why **GADM is not**.

## No warranty

These boundaries are provided as-is. They are not suitable for legal,
navigational or cadastral purposes. Feature counts are known to be incomplete
in places — Chile ships 345 of 346 communes — and geometry accuracy is
whatever the upstream source provided.

## Disputed boundaries

Boundaries follow the named upstream source. Their inclusion is not a statement
about sovereignty. See [Disputed boundaries](disputed-boundaries.md).

--8<-- "abbreviations.md"
