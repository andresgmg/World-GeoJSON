"""Generate the documentation catalog from data/**/manifest.json.

Wired in as a MkDocs *hook* (see `hooks:` in mkdocs.yml), not as a
mkdocs-gen-files script. That choice is forced, not stylistic:

    mkdocs-static-i18n only processes files whose abs_src_path lies inside
    docs_dir (reconfigure.py, `is_relative_to(file.abs_src_path,
    mkdocs_config.docs_dir)`). mkdocs-gen-files writes its virtual pages into
    a temp directory, so generated Markdown falls through i18n's classifier
    to `log.warning("Unhandled file case")` and is DROPPED from the build —
    taking the whole Catalog tree and every link to it with it.

    Writing real files into docs_dir before the file collection is built
    sidesteps this entirely: i18n, literate-nav and the theme all see
    ordinary pages.

The generated tree is git-ignored; it is a build artifact.

HARD RULE
---------
This must stay O(number of datasets), never O(bytes of data). It reads
manifest.json sidecars only and must NEVER open a .geojson file. If you find
yourself reaching for `json.load(open(dataset["path"]))` here, stop: that work
belongs in scripts/build_manifest.py, which runs when the data changes rather
than on every documentation build.

Breaking that rule would make `mkdocs serve` unusable, slow CI down, and
invalidate the sparse-checkout in .github/workflows/docs.yml, which does not
check the .geojson files out at all.
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

log = logging.getLogger("mkdocs.hooks.gen_catalog")

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"

BODIES = {"earth": "Earth", "moon": "Moon", "mars": "Mars"}

LEVELS = {
    "ADM0": "Country / body outline",
    "ADM1": "First-level divisions",
    "ADM2": "Second-level divisions",
    "ADM3": "Third-level divisions",
    "QUAD": "Quadrangles",
}

# Maps a generated page path -> the manifest it came from, so on_page_markdown
# can repoint the "edit this page" button at something that actually exists.
_EDIT_TARGETS: dict[str, str] = {}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


def slug(text: str) -> str:
    return text.lower().replace(" ", "-").replace("/", "-")


def human_bytes(n: int | None) -> str:
    if n is None:
        return "—"
    size = float(n)
    for unit in ("B", "KB", "MB"):
        if size < 1024:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} GB"


def write_if_changed(path: Path, content: str) -> bool:
    """Write only when content differs.

    `mkdocs serve` watches docs_dir, and this hook writes into docs_dir.
    Unconditional writes would retrigger the watcher on every build and spin
    forever. Comparing first means the build settles after one extra pass.
    """
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


# ---------------------------------------------------------------------------
# rendering
# ---------------------------------------------------------------------------


def render_dataset(out: list[str], manifest: dict, ds: dict, up: str, cdn: str, raw: str) -> None:
    level = ds["level"]
    out.append(f"## {level} — {LEVELS.get(level, level)}\n")

    if ds.get("preview"):
        out.append(
            f'<div class="geojson-map"\n'
            f'     data-src="{cdn}/{ds["preview"]}"\n'
            f'     data-body="{manifest["body"]}"\n'
            f'     data-label="{manifest["name"]["en"]} {level}"></div>\n'
        )
        out.append(
            f"<small>The map above is a simplified preview "
            f"({human_bytes(ds.get('preview_bytes'))}). Download the "
            f"full-resolution file below.</small>\n"
        )
    else:
        out.append(
            '!!! warning "No preview available"\n\n'
            "    Generate one with `node scripts/make_previews.mjs` — see\n"
            f"    [Simplification and previews]({up}contributing/previews.md).\n"
        )

    out.append("| | |")
    out.append("|---|---|")
    out.append(f"| Features | {ds['features']:,} |")
    out.append(f"| File size | {human_bytes(ds.get('bytes'))} |")
    types = ", ".join(ds.get("geometry_types", {})) or "—"
    out.append(f"| Geometry | {types} |")
    bbox = ds.get("bbox") or []
    if len(bbox) == 4:
        out.append(f"| Bounding box | `{bbox[0]}, {bbox[1]}, {bbox[2]}, {bbox[3]}` |")
    if ds.get("sha256"):
        out.append(f"| SHA-256 | `{ds['sha256'][:16]}…` |")
    out.append("")

    props = ds.get("properties") or []
    if props:
        out.append("**Properties:** " + ", ".join(f"`{p}`" for p in props) + "\n")

    out.append('=== "CDN"\n')
    out.append(f"    ```\n    {cdn}/{ds['path']}\n    ```\n")
    out.append('=== "Raw"\n')
    out.append(f"    ```\n    {raw}/{ds['path']}\n    ```\n")
    out.append('=== "curl"\n')
    out.append(f"    ```bash\n    curl -LO {raw}/{ds['path']}\n    ```\n")


def render_country(manifest: dict, up: str, cdn: str, raw: str) -> str:
    body = manifest["body"]
    title = manifest["name"]["en"]
    out: list[str] = [f"# {title}\n"]

    if body == "earth":
        out.append(
            f"**ISO 3166-1:** `{manifest.get('iso_a2', '—')}` / "
            f"`{manifest.get('iso_a3', '—')}` · "
            f"**Region:** {manifest.get('m49_region', '—')}\n"
        )
    else:
        out.append(
            f"**Body:** {BODIES.get(body, body)} · "
            f"**Code:** `{manifest.get('code', '—')}` · "
            f"**No ISO 3166 equivalent** — see "
            f"[Planetary bodies]({up}reference/planetary.md)\n"
        )

    crs = manifest.get("crs", {})
    out.append(
        '!!! info "Coordinate reference system"\n\n'
        f"    `{crs.get('authority', '?')}:{crs.get('code', '?')}` — see the\n"
        f"    [CRS policy]({up}reference/crs.md).\n"
    )

    if manifest.get("notes"):
        out.append(f'!!! note "Known gaps"\n\n    {manifest["notes"]}\n')

    for ds in manifest.get("datasets", []):
        render_dataset(out, manifest, ds, up, cdn, raw)

    out.append("## Source and licence\n")
    src = manifest.get("source") or {}
    if src:
        line = (
            f"[{src.get('name', 'Unknown')}]({src.get('url', '#')}) — "
            f"`{src.get('license', 'unknown')}`"
        )
        if src.get("retrieved"):
            line += f", retrieved {src['retrieved']}"
        out.append(line + ".\n")
        out.append(
            f"See [Licensing and attribution]({up}about/license.md) for how "
            "dataset licences relate to this project's own licence.\n"
        )
    else:
        out.append("Not recorded. This dataset is incomplete.\n")

    return "\n".join(out)


def render_index(coverage: list[dict]) -> str:
    out = ["# Catalog\n"]
    if not coverage:
        out.append(
            '!!! info "The catalog is not populated yet"\n\n'
            "    No `data/**/manifest.json` files exist in the repository yet,\n"
            "    so there is nothing to list. The generator, the navigation\n"
            "    wiring and the page templates are already in place — the\n"
            "    catalog fills in automatically as datasets are given\n"
            "    manifests.\n\n"
            "    See [Add a country](../contributing/add-a-country.md) to\n"
            "    contribute one, or [Roadmap](../about/roadmap.md) for the\n"
            "    planned sequence.\n"
        )
        return "\n".join(out)

    datasets = sum(len(c["levels"]) for c in coverage)
    bodies = len({c["body"] for c in coverage})
    out.append(
        f"{len(coverage)} entries · {datasets} datasets · {bodies} bodies.\n"
    )
    out.append(
        "Every page below is generated from that dataset's `manifest.json`. "
        "To correct a fact, edit the manifest — not the page.\n"
    )
    out.append("| Entry | Code | Group | Levels | Features |")
    out.append("|---|---|---|---|---|")
    for c in sorted(coverage, key=lambda x: (x["body"], x["group"], x["name"])):
        levels = ", ".join(c["levels"]) or "—"
        out.append(
            f"| [{c['name']}]({c['url']}) | `{c['code']}` | {c['group']} "
            f"| {levels} | {c['features']:,} |"
        )
    out.append("")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# generation
# ---------------------------------------------------------------------------


def generate(docs_dir: Path, cdn: str, raw: str) -> int:
    catalog = docs_dir / "catalog"
    wanted: dict[Path, str] = {}
    coverage: list[dict] = []
    nav_lines: list[str] = []
    _EDIT_TARGETS.clear()

    grouped: dict[tuple[str, str], list[tuple[str, Path, dict]]] = {}

    for manifest_path in sorted(DATA.glob("*/*/manifest.json")):
        manifest = json.loads(manifest_path.read_text("utf-8"))
        body = manifest["body"]
        code = (manifest.get("iso_a3") or manifest.get("code", "")).lower()
        group = manifest.get("m49_region") or BODIES.get(body, body)
        title = manifest["name"]["en"]

        rel = Path(body, slug(group), f"{code}.md")
        # catalog/<body>/<group>/<code>.md sits three directories below the
        # docs root, so links back out need three levels of `../`.
        wanted[catalog / rel] = render_country(manifest, "../../../", cdn, raw)
        _EDIT_TARGETS[(Path("catalog") / rel).as_posix()] = (
            manifest_path.relative_to(REPO).as_posix()
        )

        grouped.setdefault((BODIES.get(body, body), group), []).append(
            (title, rel, manifest)
        )
        coverage.append(
            {
                "body": body,
                "code": code.upper(),
                "name": title,
                "group": group,
                "url": rel.as_posix(),
                "levels": [d["level"] for d in manifest.get("datasets", [])],
                "features": sum(
                    d.get("features", 0) for d in manifest.get("datasets", [])
                ),
            }
        )

    # literate-nav SUMMARY
    nav_lines.append("- [Catalog](index.md)")
    last_body = None
    for (body_label, group), entries in sorted(grouped.items()):
        if body_label != last_body:
            nav_lines.append(f"- {body_label}")
            last_body = body_label
        nav_lines.append(f"    - {group}")
        for title, rel, _ in sorted(entries):
            nav_lines.append(f"        - [{title}]({rel.as_posix()})")

    wanted[catalog / "index.md"] = render_index(coverage)
    wanted[catalog / "SUMMARY.md"] = "\n".join(nav_lines) + "\n"

    # Drop stale pages from a previous run (a country removed or renamed).
    if catalog.exists():
        for existing in catalog.rglob("*.md"):
            if existing not in wanted:
                existing.unlink()
        for d in sorted(catalog.rglob("*"), reverse=True):
            if d.is_dir() and not any(d.iterdir()):
                d.rmdir()
    else:
        catalog.mkdir(parents=True, exist_ok=True)

    changed = sum(write_if_changed(p, c) for p, c in wanted.items())
    return changed


def purge(docs_dir: Path) -> None:
    shutil.rmtree(docs_dir / "catalog", ignore_errors=True)


# ---------------------------------------------------------------------------
# MkDocs hooks
# ---------------------------------------------------------------------------


def on_config(config):
    """Materialise docs/catalog/ before MkDocs collects the file tree."""
    extra = config.get("extra", {})
    changed = generate(
        Path(config["docs_dir"]),
        extra.get("data_cdn", ""),
        extra.get("data_raw", ""),
    )
    log.info("gen_catalog: %d catalog file(s) written", changed)
    return config


def on_files(files, config):
    """Drop catalog/SUMMARY.md from the build output.

    literate-nav reads it to build the Catalog subtree and normally removes it
    itself, but i18n has already wrapped it in an I18nFile so that removal
    misses. Left alone it gets published as a stray page containing the raw
    nav list. Hooks run after plugins, so literate-nav has had its turn by the
    time this fires.
    """
    keep = [f for f in files if not f.src_uri.replace("\\", "/").endswith("catalog/SUMMARY.md")]
    return files.__class__(keep)


def on_page_markdown(markdown, page, config, files):
    """Point the edit button at the manifest, not the generated page."""
    target = _EDIT_TARGETS.get(page.file.src_uri)
    if target and config.get("repo_url"):
        page.edit_url = f"{config['repo_url'].rstrip('/')}/edit/main/{target}"
    return markdown
