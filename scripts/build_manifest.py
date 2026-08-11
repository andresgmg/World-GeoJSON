"""Scan a dataset directory and write its manifest.json.

    python scripts/build_manifest.py data/earth/CHL

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
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import ijson

REPO = Path(__file__).resolve().parents[1]
SCHEMA_VERSION = 1

LEVEL_DIR = re.compile(r"^ADM\d$|^QUAD$")
LEVEL_FILE = re.compile(r"^[A-Z]{3,4}_(ADM\d|QUAD)$")


# ---------------------------------------------------------------------------
# scanning
# ---------------------------------------------------------------------------


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def scan(path: Path) -> dict:
    """One streaming pass: feature count, bbox, geometry types, property keys.

    Never retains more than a single coordinate position, so memory is flat
    regardless of file size.
    """
    n_features = 0
    minx = miny = float("inf")
    maxx = maxy = float("-inf")
    prop_keys: set[str] = set()
    geom_types: Counter[str] = Counter()
    pos: list[float] = []

    with path.open("rb") as fh:
        for prefix, event, value in ijson.parse(fh, use_float=True):
            if event == "start_map" and prefix == "features.item":
                n_features += 1
            elif event == "map_key" and prefix == "features.item.properties":
                prop_keys.add(value)
            elif event == "string" and prefix.endswith("geometry.type"):
                geom_types[value] += 1
            elif ".coordinates" in prefix:
                # ijson emits one `.item` per nesting level, so every coordinate
                # number's prefix contains ".coordinates". The innermost
                # start_array/end_array pair brackets one position.
                if event == "start_array":
                    pos = []
                elif event == "number":
                    pos.append(float(value))
                elif event == "end_array":
                    if len(pos) >= 2:
                        x, y = pos[0], pos[1]
                        minx, maxx = min(minx, x), max(maxx, x)
                        miny, maxy = min(miny, y), max(maxy, y)
                    pos = []

    bbox = (
        [round(v, 6) for v in (minx, miny, maxx, maxy)]
        if n_features and minx != float("inf")
        else []
    )
    return {
        "features": n_features,
        "bbox": bbox,
        "geometry_types": dict(sorted(geom_types.items())),
        "properties": sorted(prop_keys),
    }


def describe(path: Path, preview: Path | None = None) -> dict:
    entry = {
        "path": path.relative_to(REPO).as_posix(),
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        **scan(path),
    }
    if preview and preview.exists():
        entry["preview"] = preview.relative_to(REPO).as_posix()
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
    for f in sorted(d.glob("*.geojson")):
        if not LEVEL_FILE.match(f.stem):
            print(f"  ! skipping {f.name}: does not match {{CODE}}_{{LEVEL}}.geojson")
            continue
        level = f.stem.rsplit("_", 1)[-1]
        datasets.setdefault(level, {"level": level})
        datasets[level].update(
            describe(f, preview_dir / f"{f.stem}.preview.geojson")
        )

    # Split levels.
    for sub in sorted(p for p in d.iterdir() if p.is_dir() and LEVEL_DIR.match(p.name)):
        level = sub.name
        parts = []
        for f in sorted(sub.glob("*.geojson")):
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
            entry["preview"] = preview.relative_to(REPO).as_posix()
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dirs", nargs="+", type=Path)
    args = ap.parse_args()

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
            licenses = sorted(
                {ds["license"] for ds in manifest["datasets"] if ds.get("license")}
            )
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
        levels = ", ".join(
            f"{ds['level']}={ds.get('features', 0)}" for ds in manifest["datasets"]
        )
        print(f"{mpath.relative_to(REPO)}  —  {levels}  (total {total} features)")

        missing = [k for k in ("body", "name", "source", "crs") if k not in manifest]
        if missing:
            print(f"  ! hand-authored fields still missing: {', '.join(missing)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
