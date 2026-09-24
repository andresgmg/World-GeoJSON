"""Simplified previews for the catalog maps.

    wgj previews data/earth/CHL
    wgj previews                # every country

Full-resolution data cannot be displayed in a browser, so every dataset ships
a small companion (at most 2 MB) used only by the map on its catalog page.
See docs/contributing/previews.md.

A split level is merged before simplification so the preview shows the
whole country rather than one region. mapshaper drops a GeoJSON Feature's
`id` as soon as the attribute table is edited, so the id is carried through
as a property (`id-field=__id`) and moved back afterwards; the file is then
written in the repository's canonical layout, like the full-resolution data.
Run this AFTER finalize (the ids come from there) and BEFORE manifest.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from wgj.geojson_io import load, serialise
from wgj.levels import LEVEL_DIR, LEVEL_FILE, preview_name
from wgj.mapshaper import run_mapshaper
from wgj.paths import country_dirs, earth, rel
from wgj.text import mb

TARGET_BYTES = 800 * 1024  # aim below this
HARD_LIMIT = 2 * 1024 * 1024  # CI fails above this
MIN_PERCENTAGE = 0.2
KEEP_FIELDS = ("shapeName", "shapeISO", "shapeType")


def _write(inputs: list[Path], dest: Path, pct: float) -> int:
    combine = ["combine-files", "-merge-layers", "force"] if len(inputs) > 1 else []
    run_mapshaper(
        [
            "-i",
            *map(str, inputs),
            "id-field=__id",
            *combine,
            "-simplify",
            f"percentage={pct}%",
            "keep-shapes",
            "-filter-fields",
            ",".join([*KEEP_FIELDS, "__id"]),
            "-o",
            "precision=0.0001",
            "bbox",
            "format=geojson",
            str(dest),
        ]
    )
    features = []
    for f in load(dest):
        props = dict(f["properties"])
        fid = props.pop("__id", None)
        if fid is None:
            raise SystemExit(f"{dest.name}: a feature has no id — run `wgj finalize` first")
        features.append({"id": fid, "properties": props, "geometry": f["geometry"]})
    data = serialise(features)
    dest.write_bytes(data)
    return len(data)


def build_preview(inputs: list[Path], dest: Path, source_features: int) -> tuple[int, float, int]:
    """Simplify until the result fits the target, then verify nothing was lost.

    `keep-shapes` stops whole polygons collapsing, but a multipolygon can
    still shed small members — so the feature count is compared against the
    source and a mismatch is a hard error, not a warning. Returns
    (bytes, percentage, features).
    """
    pct = 5.0
    size = _write(inputs, dest, pct)
    while size > TARGET_BYTES and pct > MIN_PERCENTAGE:
        pct = max(MIN_PERCENTAGE, pct / 2)
        size = _write(inputs, dest, pct)

    got = len(load(dest))
    if got != source_features:
        raise SystemExit(
            f"{dest.name}: simplification dropped geometry — {got} features out of "
            f"{source_features}. Raise the percentage."
        )
    if size > HARD_LIMIT:
        raise SystemExit(
            f"{dest.name}: {mb(size)} exceeds the {mb(HARD_LIMIT)} budget even at {pct}%."
        )
    return size, pct, got


def level_inputs(d: Path) -> dict[str, list[Path]]:
    """level -> files to merge. A combined file wins over its parts when both exist:
    it holds the same features and a single input is the cheaper merge."""
    levels: dict[str, list[Path]] = {}
    for entry in sorted(d.iterdir(), key=lambda p: p.name):
        if entry.is_file() and LEVEL_FILE.match(entry.stem) and entry.suffix == ".geojson":
            levels[entry.stem.rsplit("_", 1)[-1]] = [entry]
        elif entry.is_dir() and LEVEL_DIR.match(entry.name):
            parts = sorted(entry.glob("*.geojson"), key=lambda p: p.name)
            if parts and entry.name not in levels:
                levels[entry.name] = parts
    return levels


def count_features(paths: list[Path]) -> int:
    return sum(len(load(p)) for p in paths)


def preview_country(d: Path) -> list[str]:
    """Write every preview for one country directory; returns one report line per level."""
    code = d.name
    levels = level_inputs(d)
    if not levels:
        return []
    preview_dir = d / "preview"
    preview_dir.mkdir(exist_ok=True)
    lines = []
    for level, inputs in sorted(levels.items()):
        dest = preview_dir / preview_name(code, level)
        src = count_features(inputs)
        size, pct, features = build_preview(inputs, dest, src)
        pct_text = f"{pct:g}"
        lines.append(f"  {code} {level:<5} {features:>5} features  {mb(size):>8}  at {pct_text}%")
    return lines


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("dirs", nargs="*", type=Path, help="country directories (default: all)")
    args = ap.parse_args(argv)

    targets = [d.resolve() for d in args.dirs] if args.dirs else country_dirs(earth().parent)
    for t in targets:
        if not t.is_dir():
            ap.error(f"{t}: not a directory")
    if not targets:
        print(f"no country directories found under {rel(earth())}")
        return 1

    for t in targets:
        for line in preview_country(t):
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
