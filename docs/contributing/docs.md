# Editing the docs

## Small changes

Click the :material-pencil: icon at the top of any page. GitHub opens the
source file in its editor; commit to a branch and open a PR. No local setup.

## Running the site locally

```powershell
git clone https://github.com/andresgmg/World-GeoJSON.git
cd World-GeoJSON
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-docs.txt
.\.venv\Scripts\python.exe -m mkdocs serve
```

Then open <http://127.0.0.1:8000>. Edits reload automatically.

!!! tip "Why `.\.venv\Scripts\python.exe -m mkdocs` and not `mkdocs`?"

    Calling the interpreter directly works regardless of PowerShell's
    execution policy. `.\.venv\Scripts\Activate.ps1` is blocked by default on
    many Windows installs, and the resulting error is confusing enough to stop
    a first-time contributor entirely.

    If you prefer an activated shell:

    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
    .\.venv\Scripts\Activate.ps1
    mkdocs serve
    ```

Before opening a PR:

```powershell
.\.venv\Scripts\python.exe -m mkdocs build --strict
```

`--strict` turns warnings into errors — broken internal links, pages missing
from the nav. CI runs the same command, so passing locally means passing there.

## Windows notes

**Microsoft Store Python.** If `python` resolves to
`…\WindowsApps\python.exe`, that is the Store build. It works, but its app
execution aliases occasionally confuse `venv` and it ships no `py` launcher.
Installing Python from python.org avoids a class of odd errors.

**OneDrive.** If your clone lives inside a OneDrive-synced folder, exclude
`.venv/` and `site/` from sync. Otherwise OneDrive tries to upload thousands of
virtualenv files and re-upload the built site after every build, which causes
"file in use" lock errors mid-build. Right-click each folder → **Always keep on
this device** off, or better, move the clone outside OneDrive.

If you hit rebuild loops, `mkdocs serve --no-livereload` is the escape hatch.

## How the site is organised

| Path | What it is |
|---|---|
| `docs/` | Hand-written pages. **Contains no data.** |
| `includes/abbreviations.md` | Glossary tooltips, appended to every page |
| `pipeline/mkdocs_hook.py` | The MkDocs hook that generates catalog pages from manifests at build time. It re-exports `wgj.catalog` from the pipeline package, so building the docs needs nothing beyond `requirements-docs.txt` |
| `mkdocs.yml` | Configuration and navigation |
| `data/` | The GeoJSON tree — deliberately outside `docs/` |

!!! warning "Never move data into `docs/`"

    MkDocs copies everything under `docs_dir` into the built site verbatim,
    with no size check. A single 70 MB file placed there would be published to
    GitHub Pages on the next deploy.

## Catalog pages are generated

Pages under **Catalog** do not exist on disk. `wgj.catalog`, wired in through
the `pipeline/mkdocs_hook.py` hook, builds them from each dataset's
`manifest.json` on every build.

To correct a fact on a catalog page, **edit the manifest**. The page's edit
button already points there.

The generator must never open a `.geojson` file — it reads manifests only. That
constraint is what keeps builds fast and lets CI check out the repository
without any data files at all.

## Bilingual content

The site is English by default with Spanish translations, using the file-suffix
scheme:

```
docs/index.md      → English
docs/index.es.md   → Spanish
```

A missing `.es.md` falls back to the English page rather than 404ing, so
partial translation is fine. Translating a page means adding the `.es.md`
sibling; nav labels are translated in `mkdocs.yml` under `nav_translations`.

Generated catalog pages are English-only for now — they are mostly tables,
numbers and URLs.

## Style

- Write for someone who knows GIS but not this project.
- Prefer a concrete example to an abstract description.
- Document the current state honestly, including the parts that are wrong.
  Several pages here describe known defects in the existing data; that is
  deliberate and worth preserving.
- Use admonitions for genuine traps, not for emphasis.

--8<-- "abbreviations.md"
