# Download & CDN

There are three ways to get a file. They are not interchangeable.

## jsDelivr CDN

Fast, globally cached, correct CORS headers — when it serves the repository.

```
https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@main/<path>
```

!!! danger "jsDelivr may refuse this repository"

    jsDelivr documents two limits for its GitHub endpoint: **20 MB per file**
    and **150 MB per repository**. Every file under `data/` is under the first
    — the largest is 14.9 MB, and levels that would exceed it are split by
    ADM1. The repository as a whole currently exceeds the second, so jsDelivr
    may refuse it. Treat the CDN as an optimisation to try, not a dependency:
    raw GitHub URLs are the reliable path today, and GitHub Release assets
    will be from v1.0.0 on.

    The legacy 72 MB `comunas.geojson` in the repository root is above the
    per-file limit regardless. Use `data/earth/CHL/CHL_ADM3.geojson`.

**Pin a tag in production.** `@main` follows the default branch, so a boundary
correction merged upstream changes what your application receives, silently.

=== "Pinned (once v1.0.0 is tagged)"

    ```
    https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0/<path>
    ```

    No tag exists yet — `v1.0.0` is planned next, see the
    [Roadmap](../about/roadmap.md). Until then only `@main` resolves. From
    v1.0.0 on, the per-country zips attached to the GitHub Release are the
    recommended pinned download.

=== "Latest"

    ```
    https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@main/<path>
    ```

## Raw GitHub

```
https://raw.githubusercontent.com/andresgmg/World-GeoJSON/main/<path>
```

Works for files of any size and sends `Access-Control-Allow-Origin: *`, so
browser `fetch` works. But it is **not a CDN**: no edge caching, and it is
rate-limited. Fine for development, scripts and server-side downloads; poor for
production browser traffic.

## Previews

For a map in a browser you rarely want the full file. Every dataset has a
simplified companion at

```
data/earth/{ISO3}/preview/{ISO3}_{LEVEL}.preview.geojson
```

— at most 2 MB and usually a few hundred KB, coordinates at four decimals, and
only `shapeName`, `shapeISO` and `shapeType` — served from the same URLs as
the full files and fine to load directly. Chile's 345 communes are 425 KB as a
preview against 7 MB in full.

## Git

For working with the data locally or in a pipeline.

The repository's pack is about 56 MiB and the working tree about 309 MB —
164 MB under `data/` and most of the rest the four legacy files in the root.
A full clone is not enormous, but a sparse checkout of one country is a lot
smaller.

=== "Everything"

    ```bash
    git clone https://github.com/andresgmg/World-GeoJSON.git
    ```

=== "One country (sparse)"

    ```bash
    git clone --filter=blob:none --sparse https://github.com/andresgmg/World-GeoJSON.git
    cd World-GeoJSON
    git sparse-checkout set data/earth/CHL
    ```

    `--filter=blob:none` makes the clone fetch file contents lazily, so you
    download only the blobs you actually check out.

=== "Metadata only"

    ```bash
    git clone --filter=blob:none --no-checkout https://github.com/andresgmg/World-GeoJSON.git
    cd World-GeoJSON
    git sparse-checkout set --no-cone '/*' '!/data/**' '/data/**/manifest.json'
    git checkout main
    ```

    Gets every manifest without a single GeoJSON file. This is exactly what
    this site's CI does — the documentation build reads manifests only.

## Checksums

Each catalog page shows the first 16 hex characters of the file's SHA-256; the
full hash is in the country's `manifest.json`, as `datasets[].sha256` and, for
split levels, `parts[].sha256`. Verify a download with:

=== "PowerShell"

    ```powershell
    Get-FileHash .\CHL_ADM1.geojson -Algorithm SHA256
    ```

=== "Bash"

    ```bash
    sha256sum CHL_ADM1.geojson
    ```

!!! warning "Line endings will break your checksum"

    Git normalises line endings on checkout. On Windows a `.geojson` checked
    out as CRLF is one byte per line larger than the same file on Linux — for
    the legacy 72 MB `comunas.geojson`, with one coordinate per line, that is
    a 1.8 MB difference and a completely different hash.

    The repository's `.gitattributes` pins `*.geojson` to LF precisely so that
    published checksums match everywhere. If your hash disagrees, check
    `git config core.autocrlf` before assuming the file is corrupt.

--8<-- "abbreviations.md"
