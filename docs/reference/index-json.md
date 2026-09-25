# Global index & schemas

`data/index.json` is the whole catalog in one file: every territory and every
dataset, with each country's [manifest](manifest.md) embedded verbatim. One
request instead of fifty-five, and the entry point the
[client libraries](../libraries/index.md) read.

## What it is

`wgj index` walks the manifests and writes a single JSON document
that contains them, plus a few derived fields a client needs before it has
downloaded anything: the published levels, the licences that actually govern
the files, which level is the municipal tier and what the tiers are called
locally. Because the manifests are embedded rather than summarised, the index
can never disagree with a manifest — and CI regenerates it on every change
(`wgj index --check`) to make sure the committed copy is current.

## Shape

```json
{
  "schema_version": 1,
  "bodies": ["earth"],
  "totals": { "countries": 55, "datasets": 95, "features": 16195, "bytes": 125679933 },
  "countries": [ … ]
}
```

| Key | Meaning |
|---|---|
| `schema_version` | Format version of the index. `1` today |
| `bodies` | The bodies with data: `["earth"]` until the Moon and Mars arrive |
| `totals` | `countries`, `datasets`, `features` and `bytes` of full-resolution data across the corpus |
| `countries` | One entry per territory, sorted by `body` then `iso_a3` |

### Per country (`countries[]`)

Chile's entry, with the datasets abridged:

```json
{
  "body": "earth",
  "iso_a3": "CHL",
  "iso_a2": "CL",
  "m49_region": "South America",
  "name": { "en": "Chile", "es": "Chile" },
  "status": "ok",
  "manifest": "data/earth/CHL/manifest.json",
  "license": "mixed",
  "licenses": ["CC-BY-4.0", "public-domain"],
  "levels": ["ADM0", "ADM1", "ADM2", "ADM3"],
  "municipal_level": "ADM3",
  "terms": {
    "adm1": { "en": "Region", "es": "Región" },
    "adm2": { "en": "Province", "es": "Provincia" },
    "municipal": { "en": "Commune", "es": "Comuna" }
  },
  "crs": { "authority": "OGC", "code": "CRS84", "epsg": 4326 },
  "source": {
    "name": "IDE Chile / SUBDERE — División Política Administrativa 2023",
    "url": "https://www.geoportal.cl/",
    "license": "mixed",
    "retrieved": "2026-08-11",
    "licenses": ["CC-BY-4.0", "public-domain"]
  },
  "datasets": [ … ]
}
```

| Field | Meaning |
|---|---|
| `body`, `iso_a3`, `iso_a2`, `m49_region`, `name`, `status` | Identity, copied from the manifest |
| `manifest` | Path of the manifest, relative to the repository root |
| `license`, `licenses` | Roll-up of `datasets[].license`: the single value, or `"mixed"`, and the sorted distinct values |
| `levels` | The published levels, in order |
| `municipal_level` | Which level is the municipal tier, or `null` when none is published |
| `terms` | Local names of the tiers in both languages — `adm1`, `adm2` where one exists, `municipal` — from `pipeline/src/wgj/tables/countries.json`. Present when the registry defines them |
| `crs`, `source`, `notes` | As in the manifest; `notes` only where the manifest has one |
| `datasets` | The manifest's `datasets` array, **verbatim** — paths, `bytes`, `sha256`, `features`, `bbox`, `properties`, previews and split `parts`, exactly as [Manifest format](manifest.md#per-dataset-datasets) describes |

## Size and determinism

340 KB on disk, 39 KB gzipped — a fraction of the smallest data file. It has
no timestamp and no version field, deliberately: the file is byte-deterministic
for a given state of the manifests, so CI can regenerate it and `git diff`. The
data version is the git ref you fetched it from.

## Fetching it

=== "Latest (`main`)"

    ```
    https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/data/index.json
    ```

=== "Pinned (once v1.0.0 is tagged)"

    ```
    https://raw.githubusercontent.com/andresgmg/World-GeoJSON/v1.0.0/data/index.json
    ```

    `v1.0.0` is tagged from the merge of the data contract; until then only
    `main` resolves. Every tagged release also attaches `index.json` as a
    Release asset, next to the per-country zips and a `SHA256SUMS`:
    <https://github.com/andresgmg/World-GeoJSON/releases/tag/v1.0.0>. See
    [Download & CDN](../get-started/download.md#release-assets).

The `path` of every dataset is repository-relative, so `base + path` is the
download URL for whichever base you fetched the index from. Listing every
territory that publishes first-level divisions:

=== "JavaScript"

    ```js
    const base = "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/";
    const index = await fetch(`${base}data/index.json`).then((r) => r.json());

    for (const c of index.countries) {
      const adm1 = c.datasets.find((d) => d.level === "ADM1");
      if (adm1) {
        console.log(c.iso_a3, c.name.en, adm1.features, `${base}${adm1.path}`);
      }
    }
    ```

=== "Python"

    ```python
    import json
    import urllib.request

    BASE = "https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/"

    with urllib.request.urlopen(BASE + "data/index.json") as fh:
        index = json.load(fh)

    for c in index["countries"]:
        adm1 = next((d for d in c["datasets"] if d["level"] == "ADM1"), None)
        if adm1:
            print(c["iso_a3"], c["name"]["en"], adm1["features"], BASE + adm1["path"])
    ```

Before trusting a downloaded file, compare its SHA-256 with the `sha256` the
index carries for it — see
[Download & CDN → Checksums](../get-started/download.md#checksums).

## Schemas

Everything the pipeline writes is described by a JSON Schema (draft 2020-12).
The five files live in `schemas/` and are served from this site at their `$id`
URL, so a validator can resolve the cross-references online:

| File | `$id` | What it validates |
|---|---|---|
| `manifest.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/manifest.schema.json> | Every `data/{body}/{ISO3}/manifest.json` — identity, provenance and one entry per level. Its `license` enum **is** the licence allow-list |
| `index.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/index.schema.json> | `data/index.json`, this page |
| `feature.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/feature.schema.json> | One Feature of a full-resolution file: `type`, the required `id`, `properties`, a polygon geometry |
| `feature-properties.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/feature-properties.schema.json> | The `properties` object of a feature — the [contract](properties.md); no key outside it is allowed |
| `countries.schema.json` | <https://andresgmg.github.io/World-GeoJSON/schemas/countries.schema.json> | `pipeline/src/wgj/tables/countries.json`, the registry the pipeline reads |

`wgj validate` applies all five in CI: every manifest, the index,
the registry and every feature of every full-resolution file. Previews are not
covered — they carry a subset of the properties.

To check a file yourself with the [`jsonschema`](https://pypi.org/project/jsonschema/)
package — the properties schema has no cross-references, so it needs nothing
else:

```bash
pip install jsonschema
python -c "
import json, jsonschema
schema = json.load(open('schemas/feature-properties.schema.json'))
for f in json.load(open('data/earth/CHL/CHL_ADM1.geojson'))['features']:
    jsonschema.validate(f['properties'], schema)
print('ok')
"
```

For the schemas that reference each other (`feature.schema.json` →
`feature-properties.schema.json`; `index.schema.json` and
`countries.schema.json` → definitions in `manifest.schema.json`) run
`wgj validate`, which resolves them from the local
`schemas/` directory and adds the checks a schema cannot express — id
uniqueness, `parentID` resolution, bbox against coordinates, checksums.

--8<-- "abbreviations.md"
