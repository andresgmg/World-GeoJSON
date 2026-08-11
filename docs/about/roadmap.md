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
- [ ] Restructure Chile into `data/earth/CHL/` with manifests
- [ ] Apply the standard property schema to Chile
- [ ] Minify and trim coordinate precision on the existing files
- [ ] Preview generation and interactive maps
- [ ] Data validation workflow

## Next — Chile complete, then Latin America

- [ ] `CHL_ADM0` — the national outline
- [ ] The three missing communes: Antártica, Isla de Pascua, Juan Fernández
- [ ] `CHL_ADM2` — *provincias*, if an openly licensed source can be found
- [ ] Argentina, Peru, Bolivia, Uruguay, Paraguay
- [ ] Issue and PR templates for country submissions
- [ ] Translate generated catalog pages into Spanish

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
| 343 of 346 communes | `comunas.geojson` | Next |
| No ADM2 (*provincias*) boundary file | Chile | Next, source permitting |
| Coordinates at ~14 decimal places | Both files | Now |
| Pretty-printed, ~40% size overhead | Both files | Now |
| No `bbox` member | Both files | Now |
| `cod_comuna` as integer, loses leading zero | `comunas.geojson` | Now |
| GeoJSON `id` on 5 of 343 features | `comunas.geojson` | Now |
| Duplicate `.json` files | Repo root | Now |
| Inconsistent area units between files | Both files | Now |
| `Región de Aysén del Gral.Ibañez del Campo` malformed | `regiones.geojson` | Now |

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
