"""Scan a dataset directory and write its manifest.json.

    wgj manifest data/earth/CHL

Only the `datasets` array is machine-owned. Every other key — `name`, `source`,
`crs`, `status`, `notes` — is hand-authored and is preserved verbatim across
regenerations. That split is what makes it safe to re-run this routinely; see
docs/reference/manifest.md.

Files are scanned with ijson in constant memory: a 70 MB input costs a few
seconds and a few tens of MB of RSS rather than a gigabyte-plus of parsed
Python objects.

Checksums are over the raw bytes as stored with LF line endings. The
repository's .gitattributes pins *.geojson to eol=lf precisely so a hash
computed on Windows matches Linux CI and raw.githubusercontent.com.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from wgj.geojson_io import scan, sha256
from wgj.levels import LEVEL_DIR, LEVEL_FILE
from wgj.paths import rel

SCHEMA_VERSION = 1


def path_key(p: Path) -> str:
    """Sort key that does not depend on the platform.

    Sorting Path objects directly is not portable: WindowsPath compares
    case-insensitively while PosixPath does not. With a lowercase
    `unassigned.geojson` sitting among uppercase `US-XX.geojson` parts, the two
    platforms produce different orderings — and a manifest that reorders
    between machines fails the CI freshness check for no real reason.
    """
    return p.name


# ---------------------------------------------------------------------------
# scanning
# ---------------------------------------------------------------------------


def describe(path: Path, preview: Path | None = None) -> dict:
    entry = {
        "path": rel(path),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        **scan(path),
    }
    if preview and preview.exists():
        entry["preview"] = rel(preview)
        entry["preview_bytes"] = preview.stat().st_size
    return entry


# ---------------------------------------------------------------------------
# dataset assembly
# ---------------------------------------------------------------------------


def build_datasets(d: Path, prev: dict[str, dict]) -> list[dict]:
    """Collect one entry per administrative level.

    A level is either a single file (`CHL_ADM1.geojson`) or a directory of
    per-parent parts (`ADM3/CL-RM.geojson`). Split levels get one entry with a
    `parts` array rather than one entry per file, so the catalog renders a
    single section per level instead of sixteen.
    """
    preview_dir = d / "preview"
    datasets: dict[str, dict] = {}

    # Whole-level files, including the optional combined file for a split level.
    for f in sorted(d.glob("*.geojson"), key=path_key):
        if not LEVEL_FILE.match(f.stem):
            print(f"  ! skipping {f.name}: does not match {{CODE}}_{{LEVEL}}.geojson")
            continue
        level = f.stem.rsplit("_", 1)[-1]
        datasets.setdefault(level, {"level": level})
        datasets[level].update(describe(f, preview_dir / f"{f.stem}.preview.geojson"))

    # Split levels.
    subdirs = [p for p in d.iterdir() if p.is_dir() and LEVEL_DIR.match(p.name)]
    for sub in sorted(subdirs, key=path_key):
        level = sub.name
        parts = []
        for f in sorted(sub.glob("*.geojson"), key=path_key):
            part = describe(f)
            part["code"] = f.stem
            parts.append(part)
        if not parts:
            continue

        entry = datasets.setdefault(level, {"level": level})
        entry["split_by"] = "ADM1"
        entry["parts"] = parts
        # Totals cover the whole level whether or not a combined file exists,
        # so the catalog can always report a feature count.
        entry["features"] = sum(p["features"] for p in parts)
        entry.setdefault("bytes", sum(p["bytes"] for p in parts))
        entry.setdefault("properties", sorted({k for p in parts for k in p["properties"]}))
        types: Counter[str] = Counter()
        for p in parts:
            types.update(p["geometry_types"])
        entry.setdefault("geometry_types", dict(sorted(types.items())))
        if "bbox" not in entry or not entry["bbox"]:
            boxes = [p["bbox"] for p in parts if len(p["bbox"]) == 4]
            if boxes:
                entry["bbox"] = [
                    round(min(b[0] for b in boxes), 6),
                    round(min(b[1] for b in boxes), 6),
                    round(max(b[2] for b in boxes), 6),
                    round(max(b[3] for b in boxes), 6),
                ]
        preview = preview_dir / f"{d.name}_{level}.preview.geojson"
        if preview.exists():
            entry["preview"] = rel(preview)
            entry["preview_bytes"] = preview.stat().st_size

    # Carry forward everything build_data.py recorded that cannot be derived
    # from the files themselves: provenance, licence and what was done to the
    # geometry.
    carried = ("simplification", "license", "src_provider", "src_year", "unassigned")
    for level, entry in datasets.items():
        old = prev.get(level, {})
        for key in carried:
            if key in old:
                entry[key] = old[key]

    return [datasets[k] for k in sorted(datasets)]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("dirs", nargs="+", type=Path)
    args = ap.parse_args(argv)

    for raw in args.dirs:
        d = raw.resolve()
        if not d.is_dir():
            raise SystemExit(f"{raw}: not a directory")

        mpath = d / "manifest.json"
        manifest = json.loads(mpath.read_text("utf-8")) if mpath.exists() else {}
        prev = {ds.get("level"): ds for ds in manifest.get("datasets", [])}

        manifest.setdefault("schema_version", SCHEMA_VERSION)
        manifest["datasets"] = build_datasets(d, prev)

        # Keep the country-level licence honest: it is whatever the datasets
        # actually carry. A territory holding only a public-domain outline must
        # not read as CC BY, and levels sourced from different upstreams
        # legitimately differ.
        src = manifest.get("source")
        if isinstance(src, dict):
            licenses = sorted({ds["license"] for ds in manifest["datasets"] if ds.get("license")})
            if len(licenses) == 1:
                src["license"] = licenses[0]
                src.pop("licenses", None)
            elif licenses:
                src["license"] = "mixed"
                src["licenses"] = licenses

        mpath.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )

        total = sum(ds.get("features", 0) for ds in manifest["datasets"])
        levels = ", ".join(f"{ds['level']}={ds.get('features', 0)}" for ds in manifest["datasets"])
        print(f"{rel(mpath)}  —  {levels}  (total {total} features)")

        missing = [k for k in ("body", "name", "source", "crs") if k not in manifest]
        if missing:
            print(f"  ! hand-authored fields still missing: {', '.join(missing)}")
    return 0
