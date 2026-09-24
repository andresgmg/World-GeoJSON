# Contributing

Thanks for helping. The full guide lives in the documentation site — this file
is the short version and points there.

**Documentation:** <https://andresgmg.github.io/World-GeoJSON/contributing/>

## Two kinds of contribution

1. **Documentation fixes.** Click the pencil icon on any docs page, edit on
   GitHub, open a PR. No local setup needed. Every `X.md` has a Spanish twin
   `X.es.md`; please change both when the substance changes.
2. **Data (a new country, a corrected level).** Read
   [Approved sources & licensing](https://andresgmg.github.io/World-GeoJSON/contributing/sources/)
   **first** — an incompatible upstream licence (GADM, ODbL, CC-BY-SA) ends a
   contribution before it starts. Then follow
   [Add a country](https://andresgmg.github.io/World-GeoJSON/contributing/add-a-country/)
   and the [review checklist](https://andresgmg.github.io/World-GeoJSON/contributing/checklist/).

## Local setup for the pipeline and its tests

```sh
python -m venv .venv && . .venv/bin/activate   # Windows: .\.venv\Scripts\activate
pip install -r requirements-dev.txt
npm ci                                          # pinned mapshaper
```

Then, before opening a PR:

```sh
ruff check . && ruff format --check . && mypy   # lint, format, types
pytest                                          # unit tests (no network needed)
wgj validate --checksums                        # every dataset under data/
```

If you have [`just`](https://github.com/casey/just) installed, `just ci` runs
the same sequence. Optional: `pip install pre-commit && pre-commit install`
runs ruff on each commit.

The pipeline itself is the `wgj` command (`wgj fetch` → `wgj build` →
`wgj previews` → `wgj manifest` → `wgj index` → `wgj validate`), installed
by `requirements-dev.txt` from `pipeline/`; it is documented in
[Pipeline](https://andresgmg.github.io/World-GeoJSON/contributing/pipeline/).

## Pull requests

- One country (or one focused fix) per PR.
- CI must be green: lint/tests (`ci.yml`), data validation
  (`validate-data.yml`) and the strict docs build (`docs.yml`).
- Regenerate manifests after touching data: CI fails on a stale manifest.
- Never rewrite published history; deprecations go through the process in
  [Versioning](https://andresgmg.github.io/World-GeoJSON/about/versioning/).

## Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md). Boundary
disputes get technical framing or get locked — see the "Boundaries and
sovereignty" section there.
