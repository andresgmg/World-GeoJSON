## Summary

<!-- What changes and why, in a few lines. Link the issue if there is one. -->

## Kind of change

- [ ] Data (a new territory, a new level, a correction)
- [ ] Pipeline (`pipeline/`, the `wgj` command)
- [ ] Libraries (`packages/`)
- [ ] Documentation only

## Checklist

<!-- Tick what applies; leave the rest unticked. -->

- [ ] Source licence is on the allow-list and recorded in the manifest (data)
- [ ] `wgj validate --checksums` passes and manifests plus `data/index.json` are regenerated (data)
- [ ] `ruff check . && ruff format --check . && mypy && pytest` pass (Python)
- [ ] `npm test` passes (JavaScript)
- [ ] Every changed `X.md` has its `X.es.md` twin updated
- [ ] Changelog entry under "Unreleased" in both languages, when users would notice the change
