# wgj — the World GeoJSON pipeline

Not published. Installed into a contributor's environment with

    pip install -e ./pipeline[pipeline]

which puts the `wgj` command on the path. `wgj --help` lists the steps in
pipeline order: `fetch`, `build`, `finalize`, `previews`, `manifest`, `index`,
`validate`, `all`. See docs/contributing/pipeline.md.
