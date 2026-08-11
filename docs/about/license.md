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

Every dataset's catalog page names its source and licence. Every
`manifest.json` records them:

```json
"source": {
  "name": "geoBoundaries",
  "url": "https://www.geoboundaries.org/",
  "license": "CC-BY-4.0",
  "retrieved": "2026-08-10"
}
```

**Check the dataset page before redistributing.** There is no single answer for
the whole repository, and there never will be.

## No copyleft

Every dataset here is under a **permissive** licence — CC BY, CC0, public
domain or equivalent. Share-alike sources are excluded, and CI enforces the
[allow-list](../contributing/sources.md#the-allow-list).

The reason is ODbL specifically. It defines a *Derivative Database*, and mixing
one ODbL dataset into this collection would arguably place the entire
collection under ODbL — changing the terms for every existing consumer without
their knowledge. That is not a trade this project will make, even though it
costs real coverage: a third of geoBoundaries' Americas entries are ruled out
this way.

Gaps are recorded on the [Roadmap](roadmap.md). They get closed by finding a
permissive source, not by relaxing the rule.

## Conditions that travel with a grant

Some open licences arrive with obligations beyond attribution, and those are
recorded in the manifest's `source.license_note`.

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

For Chile's current data:

> Boundaries from the Biblioteca del Congreso Nacional de Chile (BCN) / IDE
> Chile, via World GeoJSON.

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
3. The `source` block in the manifest is accurate and complete.

See [Approved sources & licensing](../contributing/sources.md) for what is
acceptable — and specifically for why **GADM is not**.

## No warranty

These boundaries are provided as-is. They are not suitable for legal,
navigational or cadastral purposes. Feature counts are known to be incomplete
in places — Chile ships 343 of 346 communes — and geometry accuracy is
whatever the upstream source provided.

## Disputed boundaries

Boundaries follow the named upstream source. Their inclusion is not a statement
about sovereignty. See [Disputed boundaries](disputed-boundaries.md).

--8<-- "abbreviations.md"
