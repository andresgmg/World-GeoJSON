"""Validate every dataset in data/ against the repository's conventions.

    python scripts/validate_data.py                 # everything under data/
    python scripts/validate_data.py data/earth/CHL  # one or more country dirs

Run by .github/workflows/validate-data.yml on any PR touching data/. The checks
here are the ones docs/reference/manifest.md promises, and the licence
allow-list in particular is the guardrail that keeps copyleft data out: a third
of geoBoundaries' Americas entries are ODbL or CC-BY-SA, and ODbL's share-alike
term would propagate to the whole collection.

Exit status is 1 when any error was found. Warnings never fail the run. Under
GitHub Actions (GITHUB_ACTIONS=true) findings are printed as workflow
annotations; elsewhere as plain lines.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"

# SPDX identifiers that permit redistribution and commercial use without a
# share-alike obligation. Anything absent from this list is rejected, including
# every ODbL and CC-BY-SA variant. See docs/contributing/sources.md.
ALLOWED_LICENSES = {
    "CC0-1.0",
    "CC-BY-3.0",
    "CC-BY-3.0-IGO",
    "CC-BY-4.0",
    "CC-BY-2.5",
    "Etalab-2.0",
    "OGL-Canada-2.0",
    "public-domain",
}

MAX_DATA_BYTES = 50 * 1024 * 1024  # GitHub warns above this
MAX_PREVIEW_BYTES = 2 * 1024 * 1024  # docs/contributing/previews.md
REQUIRED_MANIFEST = ("body", "name", "crs", "source", "status")
REQUIRED_SOURCE = ("name", "url", "license", "retrieved")
REQUIRED_PROPS = {"shapeName", "shapeISO", "shapeGroup", "shapeType"}


@dataclass
class Report:
    """Findings for one run. Passed explicitly so nothing leaks between runs."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checked: int = 0

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    @property
    def ok(self) -> bool:
        return not self.errors


def _rel(path: Path) -> str:
    """Repository-relative POSIX path when inside the repo, else as given.

    Tests validate copies under a temporary directory; those must not crash
    on `relative_to`.
    """
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


def check_geojson(path: Path, label: str, report: Report) -> None:
    size = path.stat().st_size
    if size > MAX_DATA_BYTES:
        report.err(f"{label}: {size / 1024 / 1024:.1f} MB exceeds the 50 MB limit")

    # Read once; the precision heuristic below reuses the raw text.
    raw = path.read_text("utf-8")
    try:
        data = json.loads(raw)
    except Exception as exc:
        report.err(f"{label}: not valid JSON ({exc})")
        return

    if data.get("type") != "FeatureCollection":
        report.err(f"{label}: top-level type is not FeatureCollection")
    if "crs" in data:
        report.err(f"{label}: has a `crs` member, which RFC 7946 removed")
    if "bbox" not in data:
        report.err(f"{label}: missing the top-level `bbox` member")

    features = data.get("features") or []
    if not features:
        report.err(f"{label}: no features")
        return

    for i, f in enumerate(features):
        if f.get("geometry") is None:
            report.err(f"{label}: feature {i} has null geometry")
            break

    # Every feature, not just the first: a file whose tail was produced by a
    # different tool or a hand edit would otherwise pass.
    for i, f in enumerate(features):
        missing = REQUIRED_PROPS - set(f.get("properties") or {})
        if missing:
            report.err(f"{label}: feature {i} is missing required properties {sorted(missing)}")
            break

    for f in features:
        p = f.get("properties") or {}
        if not isinstance(p.get("shapeISO", ""), str):
            report.err(
                f"{label}: shapeISO must be a string "
                f"(got {type(p.get('shapeISO')).__name__} on '{p.get('shapeName')}')"
            )
            break

    # 6 decimal places is ~11 cm; anything finer is noise occupying real bytes.
    for token in raw.split("[")[1:200]:
        for num in token.split(",")[:2]:
            num = num.strip().rstrip("]}")
            if "." in num and len(num.split(".")[-1]) > 6:
                report.warn(f"{label}: coordinate precision beyond 6 decimals ({num})")
                return


def check_country(d: Path, report: Report) -> None:
    rel = _rel(d)
    mpath = d / "manifest.json"
    if not mpath.exists():
        report.err(f"{rel}: no manifest.json")
        return

    try:
        manifest = json.loads(mpath.read_text("utf-8"))
    except Exception as exc:
        report.err(f"{rel}: manifest.json is not valid JSON ({exc})")
        return
    if not isinstance(manifest, dict):
        report.err(f"{rel}: manifest.json is not a JSON object")
        return

    for key in REQUIRED_MANIFEST:
        if key not in manifest:
            report.err(f"{rel}: manifest missing '{key}'")

    src = manifest.get("source") or {}
    for key in REQUIRED_SOURCE:
        if not src.get(key):
            report.err(f"{rel}: source.{key} is missing or empty")

    def check_license(value: str, where: str) -> None:
        if value not in ALLOWED_LICENSES:
            report.err(
                f"{rel}: {where} '{value}' is not on the permissive allow-list. "
                f"Copyleft (ODbL, CC-BY-SA) cannot be redistributed here — see "
                f"docs/contributing/sources.md"
            )

    lic = src.get("license")
    if lic == "mixed":
        # Levels can come from different upstreams under different terms, so a
        # single country-level licence would be a false claim. "mixed" is only
        # acceptable alongside the actual list.
        listed = src.get("licenses") or []
        if not listed:
            report.err(f"{rel}: source.license is 'mixed' but source.licenses is missing")
        for value in listed:
            check_license(value, "source.licenses entry")
    elif lic:
        check_license(lic, "source.license")

    datasets = manifest.get("datasets") or []

    # The per-dataset licence is the one that actually governs each file.
    for ds in datasets:
        value = ds.get("license")
        if not value:
            report.err(f"{rel} {ds.get('level', '?')}: no licence recorded")
        else:
            check_license(value, f"{ds.get('level', '?')} license")

    if "\n" in (manifest.get("notes") or ""):
        report.err(
            f"{rel}: manifest 'notes' must be a single line (it renders inside an admonition)"
        )

    for ds in datasets:
        level = ds.get("level", "?")
        label = f"{rel} {level}"
        if "features" not in ds:
            report.err(f"{label}: manifest entry has no feature count")

        parts = ds.get("parts") or []
        if parts:
            total = sum(p.get("features", 0) for p in parts)
            if total != ds.get("features"):
                report.err(
                    f"{label}: parts sum to {total} features but the level "
                    f"reports {ds.get('features')} — the split lost or "
                    f"duplicated geometry"
                )

        preview = ds.get("preview")
        if preview:
            p = REPO / preview
            if not p.exists():
                report.err(f"{label}: preview {preview} is missing")
            elif p.stat().st_size > MAX_PREVIEW_BYTES:
                report.err(
                    f"{label}: preview is {p.stat().st_size / 1024 / 1024:.1f} MB, "
                    f"over the 2 MB budget"
                )
        else:
            report.warn(f"{label}: no preview — the catalog map will be empty")

    # Sort on the name, not the Path: WindowsPath compares case-insensitively.
    for f in sorted(d.rglob("*.geojson"), key=lambda p: p.relative_to(d).as_posix()):
        if "preview" in f.parts:
            continue
        check_geojson(f, _rel(f), report)


def validate(dirs: list[Path]) -> Report:
    report = Report()
    for d in dirs:
        check_country(d, report)
        report.checked += 1
    return report


def discover(data: Path = DATA) -> list[Path]:
    """Every data/<body>/<code>/ directory, in a platform-independent order."""
    return sorted((p for p in data.glob("*/*") if p.is_dir()), key=lambda p: p.as_posix())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "dirs",
        nargs="*",
        type=Path,
        help="country directories to check (default: every one under data/)",
    )
    args = ap.parse_args(argv)

    if args.dirs:
        dirs = []
        for raw in args.dirs:
            d = raw.resolve()
            if not d.is_dir():
                ap.error(f"{raw}: not a directory")
            dirs.append(d)
    else:
        if not DATA.exists():
            print("no data/ directory — nothing to validate")
            return 0
        dirs = discover()
        if not dirs:
            print("no datasets found under data/")
            return 0

    report = validate(dirs)

    annotate = os.environ.get("GITHUB_ACTIONS") == "true"
    for w in report.warnings:
        print(f"::warning::{w}" if annotate else f"warning: {w}")
    for e in report.errors:
        print(f"::error::{e}" if annotate else f"error: {e}")

    print(
        f"\n{report.checked} dataset(s) checked — "
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)"
    )
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
