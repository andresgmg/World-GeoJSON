"""Validate every dataset in data/ against the repository's conventions.

    python scripts/validate_data.py

Run by .github/workflows/validate-data.yml on any PR touching data/. The checks
here are the ones docs/reference/manifest.md promises, and the licence
allow-list in particular is the guardrail that keeps copyleft data out: a third
of geoBoundaries' Americas entries are ODbL or CC-BY-SA, and ODbL's share-alike
term would propagate to the whole collection.
"""

from __future__ import annotations

import json
import sys
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

MAX_DATA_BYTES = 50 * 1024 * 1024     # GitHub warns above this
MAX_PREVIEW_BYTES = 2 * 1024 * 1024   # docs/contributing/previews.md
REQUIRED_MANIFEST = ("body", "name", "crs", "source", "status")
REQUIRED_SOURCE = ("name", "url", "license", "retrieved")
REQUIRED_PROPS = {"shapeName", "shapeISO", "shapeGroup", "shapeType"}

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def check_geojson(path: Path, label: str) -> None:
    size = path.stat().st_size
    if size > MAX_DATA_BYTES:
        err(f"{label}: {size/1024/1024:.1f} MB exceeds the 50 MB limit")

    try:
        data = json.loads(path.read_text("utf-8"))
    except Exception as exc:  # noqa: BLE001 - report, do not crash the run
        err(f"{label}: not valid JSON ({exc})")
        return

    if data.get("type") != "FeatureCollection":
        err(f"{label}: top-level type is not FeatureCollection")
    if "crs" in data:
        err(f"{label}: has a `crs` member, which RFC 7946 removed")
    if "bbox" not in data:
        err(f"{label}: missing the top-level `bbox` member")

    features = data.get("features") or []
    if not features:
        err(f"{label}: no features")
        return

    for i, f in enumerate(features):
        if f.get("geometry") is None:
            err(f"{label}: feature {i} has null geometry")
            break

    props = set(features[0].get("properties") or {})
    missing = REQUIRED_PROPS - props
    if missing:
        err(f"{label}: missing required properties {sorted(missing)}")

    for f in features:
        p = f.get("properties") or {}
        if not isinstance(p.get("shapeISO", ""), str):
            err(
                f"{label}: shapeISO must be a string "
                f"(got {type(p.get('shapeISO')).__name__} on '{p.get('shapeName')}')"
            )
            break

    # 6 decimal places is ~11 cm; anything finer is noise occupying real bytes.
    raw = path.read_text("utf-8")
    for token in raw.split("[")[1:200]:
        for num in token.split(",")[:2]:
            num = num.strip().rstrip("]}")
            if "." in num and len(num.split(".")[-1]) > 6:
                warn(f"{label}: coordinate precision beyond 6 decimals ({num})")
                return


def check_country(d: Path) -> None:
    rel = d.relative_to(REPO).as_posix()
    mpath = d / "manifest.json"
    if not mpath.exists():
        err(f"{rel}: no manifest.json")
        return

    manifest = json.loads(mpath.read_text("utf-8"))

    for key in REQUIRED_MANIFEST:
        if key not in manifest:
            err(f"{rel}: manifest missing '{key}'")

    src = manifest.get("source") or {}
    for key in REQUIRED_SOURCE:
        if not src.get(key):
            err(f"{rel}: source.{key} is missing or empty")

    lic = src.get("license")
    if lic and lic not in ALLOWED_LICENSES:
        err(
            f"{rel}: source.license '{lic}' is not on the permissive allow-list. "
            f"Copyleft (ODbL, CC-BY-SA) cannot be redistributed here — see "
            f"docs/contributing/sources.md"
        )

    if "\n" in (manifest.get("notes") or ""):
        err(f"{rel}: manifest 'notes' must be a single line (it renders inside an admonition)")

    for ds in manifest.get("datasets", []):
        level = ds.get("level", "?")
        label = f"{rel} {level}"
        if "features" not in ds:
            err(f"{label}: manifest entry has no feature count")

        parts = ds.get("parts") or []
        if parts:
            total = sum(p.get("features", 0) for p in parts)
            if total != ds.get("features"):
                err(
                    f"{label}: parts sum to {total} features but the level "
                    f"reports {ds.get('features')} — the split lost or "
                    f"duplicated geometry"
                )

        preview = ds.get("preview")
        if preview:
            p = REPO / preview
            if not p.exists():
                err(f"{label}: preview {preview} is missing")
            elif p.stat().st_size > MAX_PREVIEW_BYTES:
                err(
                    f"{label}: preview is {p.stat().st_size/1024/1024:.1f} MB, "
                    f"over the 2 MB budget"
                )
        else:
            warn(f"{label}: no preview — the catalog map will be empty")

    for f in sorted(d.rglob("*.geojson")):
        if "preview" in f.parts:
            continue
        check_geojson(f, f"{f.relative_to(REPO).as_posix()}")


def main() -> int:
    if not DATA.exists():
        print("no data/ directory — nothing to validate")
        return 0

    countries = sorted(p for p in DATA.glob("*/*") if p.is_dir())
    if not countries:
        print("no datasets found under data/")
        return 0

    for d in countries:
        check_country(d)

    for w in warnings:
        print(f"::warning::{w}")
    for e in errors:
        print(f"::error::{e}")

    print(
        f"\n{len(countries)} dataset(s) checked — "
        f"{len(errors)} error(s), {len(warnings)} warning(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
