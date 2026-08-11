# File & folder naming

## The canonical path

```
data/{body}/{CODE}/{CODE}_{LEVEL}.geojson
```

| Segment | Rule | Example |
|---|---|---|
| `body` | Lowercase body name | `earth`, `moon`, `mars` |
| `CODE` | Uppercase ISO 3166-1 alpha-3, or a body-specific code | `CHL`, `NZL`, `MARS` |
| `LEVEL` | `ADM0`–`ADM3`, or `QUAD` for planetary quadrangles | `ADM2` |

Worked example:

```
data/
└─ earth/
   └─ CHL/
      ├─ manifest.json
      ├─ CHL_ADM0.geojson
      ├─ CHL_ADM1.geojson          # regiones
      ├─ CHL_ADM3.geojson          # comunas
      └─ preview/
         ├─ CHL_ADM1.preview.geojson
         └─ CHL_ADM3.preview.geojson
```

Chile has no `CHL_ADM2.geojson` because no open boundary file exists for its
*provincias*. **Gaps in the level sequence are expected and allowed** — name
each file for the level it actually represents rather than renumbering to close
the gap.

## Rules

- Files **must** use the `.geojson` extension. Not `.json`.
- Every country directory **must** contain a `manifest.json`
  ([format](manifest.md)).
- Simplified previews **must** live in `preview/` and be named
  `{stem}.preview.geojson`.
- Directory and file names **must not** contain spaces, accents or non-ASCII
  characters. Accents belong in property *values*, never in paths.
- One administrative level per file. Do not bundle levels into a single
  `FeatureCollection`.

!!! note "Why not `.json` as well?"

    The repository currently ships both `comunas.geojson` and `comunas.json`,
    byte-identical. Git stores them as a single blob, so the duplication costs
    nothing in repository size — but it doubles the working tree, and it makes
    the catalog ambiguous about which path is canonical. Going forward there is
    exactly one file per dataset.

## Why ISO 3166-1 alpha-3

Alpha-3 (`CHL`) rather than alpha-2 (`CL`):

- **No collisions with subdivision codes.** Alpha-2 country codes overlap US
  state abbreviations and other subnational schemes, which becomes a real
  problem in a repository that also stores subdivisions.
- **It is what the reference datasets use.** geoBoundaries and GADM both key on
  alpha-3, so cross-referencing against them requires no translation table.
- **More visually distinct** in a directory listing of two hundred entries.

The alpha-2 code is still recorded in `manifest.json` as `iso_a2`, because many
consumers want it.

## Territories and dependencies

Some non-sovereign territories have their own alpha-3 code. Use it, and treat
them as top-level entries:

| Territory | Code | Not filed under |
|---|---|---|
| Puerto Rico | `PRI` | `USA` |
| Greenland | `GRL` | `DNK` |
| Hong Kong | `HKG` | `CHN` |

Territories **without** their own alpha-3 code are filed as ADM1/ADM2 features
of their administering country, exactly as the upstream source models them.
Do not invent codes. If you believe a territory genuinely needs its own entry
and has no ISO code, open an issue rather than choosing a code yourself —
inventing identifiers is how registries become unusable.

!!! warning "This is where sovereignty disputes surface"

    Deciding whether a place is a country, a territory or a subdivision is
    frequently the substance of a political dispute rather than a filing
    question. This project does not adjudicate. Follow the upstream source,
    record it in the manifest, and read
    [Disputed boundaries](../about/disputed-boundaries.md) before opening a PR
    on contested ground.

## Planetary paths

The Moon and Mars have no ISO 3166 equivalent — no such registry exists. They
use the body's own name as the code, and their features are named from the IAU
Gazetteer of Planetary Nomenclature:

```
data/moon/MOON/MOON_QUAD.geojson
data/mars/MARS/MARS_QUAD.geojson
```

Body codes are chosen so they can never collide with a real or future ISO
alpha-3. See [Planetary bodies](planetary.md).

--8<-- "abbreviations.md"
