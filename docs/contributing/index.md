# Contributing

There are two kinds of contribution and they work quite differently.

## Fixing the documentation

Click the :material-pencil: icon at the top of any page. It opens that file on
GitHub; edit, describe the change, submit. No local setup needed.

If you want to preview your changes first, see
[Editing the docs](docs.md).

!!! note "Catalog pages cannot be edited directly"

    Pages under **Catalog** are generated from each dataset's
    `manifest.json`. Their edit button points at the manifest, which is the
    thing to change. Editing the generated page is impossible — it does not
    exist on disk.

## Adding or correcting data

This is a more involved process, because a boundary file carries legal and
factual weight that a documentation typo does not.

1. **Check the licence first.** Not last.
   [Approved sources & licensing](sources.md) has the green/amber/red list.
   This is the step most likely to end a contribution, so doing it first saves
   you the rest of the work.
2. Follow [Add a country](add-a-country.md) end to end.
3. Run through the [Review checklist](checklist.md) before opening the PR.

### What gets a PR rejected

Being direct about this up front, because the alternative is wasting your time:

- **An incompatible upstream licence.** GADM in particular is the most
  convenient global source and is not usable here. See
  [sources](sources.md#red-do-not-use).
- **No stated source.** "I found it online" is not provenance. The manifest's
  `source` block is mandatory.
- **Geometry edited to reflect a political position.** See
  [Disputed boundaries](../about/disputed-boundaries.md).
- **Files that ignore the conventions** in [Reference](../reference/index.md).
  These are usually fixable — expect review comments rather than a rejection.

## Reporting a problem

[Open an issue](https://github.com/andresgmg/World-GeoJSON/issues). Useful bug
reports include the dataset, the specific feature, and what you expected. A
screenshot of the wrong geometry is worth a lot.

Known gaps are already tracked on the [Roadmap](../about/roadmap.md) — worth a
look before filing.

## Ground rules

The [Code of conduct](code-of-conduct.md) applies. It is not boilerplate here:
a repository of national boundaries attracts sovereignty disputes, and those
discussions need to stay technical.

--8<-- "abbreviations.md"
