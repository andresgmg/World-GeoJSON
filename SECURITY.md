# Security policy

This repository publishes static data files and the scripts that produce them.
There is no server, no accounts and no user data. The realistic risks are:

- **Data integrity** — a GeoJSON file or manifest that does not match its
  published checksum, or geometry altered outside the documented pipeline.
- **Licence violations** — copyleft or proprietary data reaching `data/`.
- **Supply chain** — the pinned toolchain (`mapshaper`, Python packages,
  GitHub Actions) being compromised.

## Reporting

Please **do not open a public issue** for anything you believe is exploitable
or could be used to distribute tampered data. Use GitHub's private
vulnerability reporting on this repository ("Security" tab → "Report a
vulnerability"). If that is unavailable, open an issue asking for a private
contact without including details.

For plain data errors (a wrong boundary, a mis-tiered level) a normal issue is
the right place — see [Contributing](CONTRIBUTING.md).

## What you can expect

- An acknowledgement within a week.
- Checksum or licence problems are treated as release blockers: the affected
  files are fixed or withdrawn, the manifests regenerated and the change
  recorded in the changelog. Git history is never rewritten.

## Verifying what you download

Every dataset's `manifest.json` records its size and SHA-256. Compare them
after downloading:

```sh
sha256sum data/earth/CHL/CHL_ADM1.geojson
```
