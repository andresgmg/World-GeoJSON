# Administrative levels

## Definitions

| Level | Meaning |
|---|---|
| **ADM0** | The outline of the country or body |
| **ADM1** | First-level divisions |
| **ADM2** | Second-level divisions |
| **ADM3** | Third-level divisions |

These follow the semantics used by
[geoBoundaries](https://www.geoboundaries.org/) and GADM, so datasets from this
project can be cross-referenced against them without a translation step.

## Level numbers are structural, not semantic

This is the rule that causes the most confusion, so it is worth stating
plainly: **ADM1 does not mean "province".** It means "whatever the first level
of subdivision is in this country". The local term is recorded separately in
the manifest.

| Country | ADM1 | ADM2 | ADM3 |
|---|---|---|---|
| Chile | Región | Provincia | Comuna |
| Argentina | Provincia | Departamento | Municipio |
| France | Région | Département | Commune |
| United States | State | County | — |
| Japan | Prefecture | Municipality | — |

Chile is a useful illustration of why the numbering has to be structural.
Communes are the tier everyone actually works with — they are the unit for
census data, elections and local government — but they are **ADM3**, not ADM2,
because a *provincia* tier sits between them and the regions. Numbering them
ADM2 because they are the more prominent tier would make Chile's levels
disagree with every other country's, and would break any cross-country query
that groups by level.

!!! info "When a country's tiers do not map cleanly"

    They frequently do not. Some countries have overlapping hierarchies,
    special-status cities that skip a level, or divisions that changed
    recently. Record what the upstream source models, describe the mismatch in
    the manifest's `notes` field, and do not silently reshape the hierarchy to
    make it look tidy.

## The municipal tier

This project publishes three things per country: the outline (ADM0), the
first-level divisions (ADM1), and the **municipal tier** — the level of local
government people actually live in. It stops there.

The municipal tier is a *semantic* target, not a level number, and its number
varies:

| Country | Municipal tier | Level |
|---|---|---|
| Chile | Comuna | **ADM3** |
| Mexico | Municipio | ADM2 |
| Brazil | Município | ADM2 |
| United States | County | ADM2 |
| Bolivia | Municipio | **ADM3** |
| Haiti | Commune | **ADM3** |
| Costa Rica | Cantón | ADM2 |

Because it cannot be inferred from the data, the mapping is curated by hand in
`scripts/countries.json` and is the one piece of this pipeline that will always
need human judgement.

Deeper levels — Panama's *corregimientos*, Costa Rica's *distritos* — are out
of scope. They exist in few countries, the file sizes grow sharply, and almost
nobody needs them.

The municipal level is always **split into one file per ADM1 parent**; see
[File & folder naming](naming.md#the-municipal-level-is-split).

## Coverage expectations

- **ADM0 and ADM1 are the priority.** They are the levels most consumers need
  and the ones most reliably available under an open licence.
- **The municipal tier where an openly licensed source exists.**

A country entry with only ADM1 is welcome. Partial coverage is normal and the
catalog shows exactly which levels exist for each entry.

!!! warning "Level numbers are not consistent between sources either"

    geoBoundaries' ADM numbering is assigned per country and does not always
    match the official hierarchy — it publishes Guadeloupe at ADM4 only,
    Puerto Rico with no ADM0 or ADM1, and Martinique at ADM3 and ADM4 with
    nothing in between. Never assume ADM2 means the same thing in two
    countries.

## Nesting must be consistent

Where multiple levels are provided for one country:

- Every ADM2 feature **must** nest inside exactly one ADM1 feature.
- The union of ADM1 features **should** equal the ADM0 outline, within the
  tolerance of the source geometry.
- Features **must** carry a reference to their parent — see
  [Property schema](schema.md).

Do not mix vintages. Boundaries change: a 2019 ADM1 file combined with a 2024
ADM2 file will not nest, and the mismatch is difficult to detect visually.
Record the vintage in the manifest.

## The Chile gap

Chile's current data has a documented hole worth knowing about:

- 343 communes are present; **346** exist officially. The missing three are the
  usual omissions from this source — Antártica, Isla de Pascua and Juan
  Fernández.
- **ADM2 is missing entirely.** The `Provincia` property is populated on every
  commune feature, so the middle tier can be *read*, but no provincial boundary
  file exists and so it cannot be drawn. Chile therefore currently jumps from
  ADM1 straight to ADM3.

Both are tracked on the [Roadmap](../about/roadmap.md).

--8<-- "abbreviations.md"
