# Roadmap

Honest about what is done, what is next, and what is aspirational.

## Now — foundations

Putting conventions and tooling in place before the data grows.

- [x] Documentation site with MkDocs + Material
- [x] Written conventions: naming, admin levels, property schema, CRS,
      planetary
- [x] Licensing policy and approved-source list
- [x] Disputed-boundaries policy
- [x] Catalog generator wired to manifests
- [x] CI building and deploying the site
- [x] Ingestion pipeline: fetch, normalise, simplify, split, manifest, preview
- [x] Chile from IDE Chile DPA 2023 — ADM1, ADM2 and ADM3
- [x] Preview generation and interactive maps
- [x] Data validation workflow with a licence allow-list

## Next — the Americas

All 57 UN M49 territories, one PR for the continent.

- [ ] ADM0 for every territory from Natural Earth
- [ ] ADM1 and the municipal tier from geoBoundaries, permissive licences only
- [ ] `CHL_ADM0` — the national outline
- [ ] Verify the suspect unit counts: Jamaica ADM2 (827 against 14 parishes),
      Saint Lucia ADM2 (547 against 10 quarters), Bahamas ADM1/ADM2 (32/34)
- [ ] Issue and PR templates for country submissions
- [ ] Translate generated catalog pages into Spanish

### Known coverage gaps

Excluding copyleft sources leaves thirteen Americas countries without an ADM1
this project can redistribute: Colombia, Costa Rica, Cuba, Guatemala, Guyana,
Honduras, Haiti, Nicaragua, Panama, Suriname, Trinidad and Tobago, Uruguay and
Saint Vincent and the Grenadines. Their geoBoundaries entries are ODbL.

Closing a gap means finding a national SDI or an HDX release under permissive
terms — not relaxing the rule. See
[Approved sources](../contributing/sources.md).

## Later — global coverage

- [ ] ADM0 for every country (Natural Earth is the obvious starting point)
- [ ] ADM1 for every country (geoBoundaries)
- [ ] ADM2 where openly licensed sources exist
- [ ] TopoJSON alongside GeoJSON
- [ ] Tagged data releases, and versioned documentation

ADM3 is explicitly not a goal at global scale. Very few countries publish it
openly and the file sizes become unmanageable.

## Eventually — the Moon and Mars

The conventions are [already written](../reference/planetary.md), deliberately:
the latitude convention in particular cannot be inferred from the data after
the fact, so getting it wrong is expensive to discover and expensive to fix.

- [ ] Lunar quadrangles, IAU 2015 body-fixed frame
- [ ] Martian quadrangles
- [ ] Named surface features from the IAU Gazetteer
- [ ] USGS Astrogeology WMS basemaps in preview maps

## Known data problems

Tracked, not hidden.

| Problem | Where | Status |
|---|---|---|
| Antártica commune (12202) absent — 345 of 346 | Chile ADM3 | Won't fix; the official DPA package excludes the Antarctic claim |
| 13 countries have no permissively licensed ADM1 | Americas | Awaiting a permissive source |
| Municipal tier assignment unverified for ~15 territories | `scripts/countries.json` | Marked `verify` and shipped as `review` |
| Peru's districts unavailable — geoBoundaries stops at provinces | Peru | Awaiting a source |
| Legacy files still at the repository root | `comunas.geojson` and friends | Deprecated, removed in the next major |

## Not planned

- **A hosted API or tile service.** This is a data repository. Cloudflare,
  jsDelivr and your own CDN do the serving better.
- **Geocoding or address data.** Different problem, different sources.
- **Historical boundaries.** Interesting, and a project of its own.
- **Sub-metre accuracy.** These are administrative boundaries, not cadastral
  surveys.

## Contributing to the roadmap

[Open an issue.](https://github.com/andresgmg/World-GeoJSON/issues) Countries
where you have local knowledge of the authoritative open source are especially
useful — finding a legally usable source is consistently the hardest part.

--8<-- "abbreviations.md"
