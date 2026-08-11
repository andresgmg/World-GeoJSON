# Property dictionary

Every property key that appears anywhere in the corpus, what it means, and
whether it is standard.

## Standard properties

Defined by this project and present on every feature. See
[Property schema](schema.md).

| Key | Type | Meaning |
|---|---|---|
| `shapeName` | string | Local-language name, with diacritics |
| `shapeISO` | string | Official code for the unit |
| `shapeGroup` | string | ISO 3166-1 alpha-3 of the country, or body code |
| `shapeType` | string | `ADM0`–`ADM3` or `QUAD` |
| `shapeID` | string | `{shapeGroup}-{shapeType}-{shapeISO}` |
| `parentISO` | string | `shapeISO` of the parent unit |
| `shapeNameEn` | string | English exonym, where meaningfully different |

## Source properties — Chile

Preserved from BCN / IDE Chile under the `src_` prefix.

| Key | Type | Meaning |
|---|---|---|
| `src_cod_comuna` | integer | INE/SUBDERE commune code. **Loses its leading zero** — see below |
| `src_codregion` | integer | Region code, 1–16 |
| `src_provincia` | string | Province name. No boundary file exists for this tier |
| `src_dis_elec` | integer | Electoral district |
| `src_cir_sena` | integer | Senatorial constituency |

The presence of `dis_elec` and `cir_sena` is the clearest evidence that the
upstream source is the Biblioteca del Congreso Nacional's shapefile set rather
than a plain INE boundary file — electoral divisions are not something a
statistics agency ships with administrative boundaries.

## Legacy properties (pre-migration)

Present in the current root-level files. These are being removed or renamed;
see the [migration table](schema.md#migration-table-for-chile).

| Key | Fate | Why |
|---|---|---|
| `Region` | → `shapeName` / `parentISO` | Inconsistent TitleCase; unaccented key, accented value |
| `Comuna` | → `shapeName` | |
| `Provincia` | → `src_provincia` | |
| `codregion` | → `src_codregion` | |
| `cod_comuna` | → `shapeISO` as zero-padded string | |
| `objectid` | **dropped** | Esri internal row number, not stable |
| `st_area_sh` | **dropped** | Precomputed area in m², projection unstated |
| `st_length_` | **dropped** | Precomputed perimeter, same problem |
| `shape_leng` | **dropped** | Duplicate of `st_length_`, truncated to the dBase 10-char limit |
| `area_km` | **dropped** | Precomputed area in km² — different units from `st_area_sh` |

## Known traps

!!! danger "`cod_comuna` loses its leading zero"

    Stored as a JSON number, so Camiña is `1402`. The official code is the
    string `01402`. Every commune in regions 1–9 is affected, and joins against
    official statistics silently match nothing.

    JSON numbers cannot represent a leading zero at all, which is why
    `shapeISO` is always a string.

!!! warning "Area units differ between files"

    `regiones.geojson` carries `area_km` in **square kilometres**.
    `comunas.geojson` carries `st_area_sh` in **square metres**. Neither file
    documents this. Compare them naively and your answer is off by 10⁶.

!!! warning "`Region` is unaccented as a key, accented as a value"

    The key is `"Region"`; the value is `"Región de Tarapacá"`. Code that
    round-trips key names through a normaliser will not find the field.

!!! warning "The GeoJSON `id` member is unreliable"

    Present on 5 of 343 commune features, absent from all 16 regions. Values
    are non-sequential and do not correspond to feature position. Use
    `shapeID` in properties instead.

## Regenerating this page

Property lists are recorded per dataset in each
[`manifest.json`](manifest.md). This page is currently maintained by hand;
generating it from the manifests is on the [Roadmap](../about/roadmap.md).

--8<-- "abbreviations.md"
