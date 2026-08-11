# Download & CDN

There are three ways to get a file. They are not interchangeable.

## jsDelivr CDN

Fast, globally cached, correct CORS headers. **Best for browsers.**

```
https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@main/<path>
```

!!! danger "20 MB hard limit"

    jsDelivr refuses to serve files larger than **20 MB**. Chile's communes
    file is 70 MB, so the CDN route simply does not exist for it — you get an
    error, not a slow download. Use raw GitHub for large files, or use the
    simplified preview files, which are built specifically to stay well under
    this limit.

**Pin a tag in production.** `@main` follows the default branch, so a boundary
correction merged upstream changes what your application receives, silently.

=== "Pinned (recommended)"

    ```
    https://cdn.jsdelivr.net/gh/andresgmg/World-GeoJSON@v1.0.0/<path>
    ```

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

## Git

For working with the data locally or in a pipeline.

The repository's packed size is only about 8.5 MB — the pretty-printed JSON
compresses roughly 9:1 — so a full clone is faster than the file sizes suggest.
What is slow is checking out 148 MB of working tree you may not need.

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

Each dataset page publishes a SHA-256 for its file. Verify a download with:

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
    Chile's communes file that is a 1.8 MB difference, and a completely
    different hash.

    The repository's `.gitattributes` pins `*.geojson` to LF precisely so that
    published checksums match everywhere. If your hash disagrees, check
    `git config core.autocrlf` before assuming the file is corrupt.

--8<-- "abbreviations.md"
