# Reference

These pages define how data in this repository is organised. They are the
contract: a contribution that follows them can be merged; one that does not
cannot, no matter how good the underlying geometry is.

They exist because the project is scaling from one country to potentially two
hundred. Two files with ad-hoc property names are merely untidy; four hundred
files with ad-hoc property names are unusable.

## At a glance

| Question | Answer | Detail |
|---|---|---|
| Where does a file go? | `data/{body}/{ISO3}/{ISO3}_{LEVEL}.geojson` | [Naming](naming.md) |
| What is ADM1? | First-level divisions, whatever they are called locally | [Admin levels](admin-levels.md) |
| What properties must a feature have? | `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` | [Schema](schema.md) |
| What coordinate system? | OGC:CRS84 (≡ EPSG:4326), longitude first | [CRS](crs.md) |
| May a file declare its own CRS? | **No.** RFC 7946 removed that member | [CRS](crs.md#the-crs-member-is-forbidden) |
| How do the Moon and Mars work? | IAU 2015 body-fixed frames, no ISO codes | [Planetary](planetary.md) |
| Where does catalog metadata come from? | `manifest.json` beside the data | [Manifest](manifest.md) |
| How do I identify one feature? | Its `id`: `{ISO3}:{LEVEL}:{key}`, stable within a data version | [Properties](properties.md) |
| How do I list everything in one request? | `data/index.json` | [Global index & schemas](index-json.md) |

## Conformance language

These pages use **must**, **should** and **may** in the
[RFC 2119](https://www.rfc-editor.org/rfc/rfc2119) sense. "Must" is enforced in
review and, where practical, in CI.

## The legacy files

Everything under `data/` follows these conventions. The four files still sitting
in the repository root — `regiones.geojson`, `comunas.geojson` and their `.json`
duplicates — do not: they predate the conventions entirely.

They remain in place, unchanged, for one full major version so that existing
deep links keep working, and they are **deprecated**. Use `data/earth/CHL/`.

See [Versioning & stability](../about/versioning.md) for the removal schedule.

--8<-- "abbreviations.md"
