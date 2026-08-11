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
      ├─ CHL_ADM1.geojson          # 16 regiones
      ├─ CHL_ADM2.geojson          # 56 provincias
      ├─ CHL_ADM3.geojson          # 345 comunas, whole country
      ├─ ADM3/                     # …and split by region
      │  ├─ CL-AP.geojson
      │  ├─ CL-RM.geojson
      │  └─ …
      └─ preview/
         ├─ CHL_ADM1.preview.geojson
         ├─ CHL_ADM2.preview.geojson
         └─ CHL_ADM3.preview.geojson
```

**Gaps in the level sequence are expected and allowed** — name each file for
the level it actually represents rather than renumbering to close the gap.

## The municipal level is split

The deepest level this project publishes is the **municipal tier**, and it is
always split into one file per ADM1 parent:

```
data/{body}/{CODE}/{LEVEL}/{parent code}.geojson
```

Brazil has 5,570 municipalities and Mexico 2,457; a single file per country
would be tens of megabytes and unusable in a browser. Splitting by first-level
division keeps every file small, lets consumers fetch only the state they care
about, and keeps everything inside the CDN's 20 MB ceiling.

The parent code is the ADM1 unit's **ISO 3166-2 code** where one is known
(`CL-RM`, `CL-AP`). Where it is not — geoBoundaries frequently ships an empty
`shapeISO` — the fallback is a slug of the ADM1 name, and `manifest.json`
records the mapping so consumers never have to guess.

### The whole-country file is conditional

A combined file (`CHL_ADM3.geojson`) is published **only when it stays under
20 MB**, because that is the largest file jsDelivr will serve. Above that, only
the split files exist, and the dataset's catalog page says so explicitly.

So: check the catalog page or the manifest rather than assuming a combined file
exists.

### `parentISO` is the immediate parent, not the file key

A commune's `parentISO` names its *province* — the immediate parent in the
official hierarchy — even though the file it lives in is keyed by *region*.
Those are different things and both are useful, so both are recorded:
`parentISO` for the hierarchy, `adm1ISO` for the file it belongs to.

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
