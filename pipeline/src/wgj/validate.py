"""Validate every dataset in data/ against the repository's conventions.

    wgj validate                 # everything under data/
    wgj validate data/earth/CHL  # one or more country dirs
    wgj validate --checksums     # also re-hash every file

Run by .github/workflows/validate-data.yml. The structural rules live in
schemas/*.schema.json (JSON Schema 2020-12) and are applied to every manifest,
to data/index.json, to the country registry and to every feature of every
full-resolution file. This module adds what a schema cannot say:

- the licence allow-list is the schema's `license` enum, and it is the
  guardrail that keeps copyleft data out — a third of geoBoundaries' Americas
  entries are ODbL or CC-BY-SA, and ODbL's share-alike term would propagate
  to the whole collection;
- feature ids are unique within a level and `parentID` points at a feature
  that exists in the country;
- the in-file `bbox` matches the coordinates;
- manifest feature counts match the files, split parts sum to the level,
  previews exist and stay under 2 MB, and (with --checksums) bytes and SHA-256
  match the manifest.

Exit status is 1 when any error was found. Warnings never fail the run. Under
GitHub Actions (GITHUB_ACTIONS=true) findings are printed as workflow
annotations; elsewhere as plain lines.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from wgj.geojson_io import bbox_of, sha256
from wgj.paths import country_dirs, data_base, data_dir, rel
from wgj.registry import raw_registry
from wgj.schema import allowed_licenses, validator
from wgj.schema import describe_error as _describe

MAX_DATA_BYTES = 50 * 1024 * 1024  # GitHub warns above this
MAX_PREVIEW_BYTES = 2 * 1024 * 1024  # docs/contributing/previews.md
PRECISION = re.compile(r"-?\d+\.\d{7,}")

# The licence allow-list is the schema's enum (checked against wgj.licensing).
ALLOWED_LICENSES = allowed_licenses()


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


@dataclass
class FileFacts:
    """What check_geojson learned about one file, for cross-checks."""

    features: int = 0
    ids: list[str] = field(default_factory=list)
    parents: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# checks
# ---------------------------------------------------------------------------


def check_geojson(path: Path, label: str, report: Report) -> FileFacts:
    facts = FileFacts()
    size = path.stat().st_size
    if size > MAX_DATA_BYTES:
        report.err(f"{label}: {size / 1024 / 1024:.1f} MB exceeds the 50 MB limit")

    # Read once; the precision heuristic below reuses the raw text.
    raw = path.read_text("utf-8")
    try:
        data = json.loads(raw)
    except Exception as exc:
        report.err(f"{label}: not valid JSON ({exc})")
        return facts

    if data.get("type") != "FeatureCollection":
        report.err(f"{label}: top-level type is not FeatureCollection")
    if "crs" in data:
        report.err(f"{label}: has a `crs` member, which RFC 7946 removed")
    if "bbox" not in data:
        report.err(f"{label}: missing the top-level `bbox` member")

    features = data.get("features") or []
    facts.features = len(features)
    if not features:
        report.err(f"{label}: no features")
        return facts

    for i, f in enumerate(features):
        if f.get("geometry") is None:
            report.err(f"{label}: feature {i} has null geometry")
            break

    # Every feature against the contract, first error only per file: one
    # bad feature is a bug in the pipeline, not one thousand findings.
    feature_validator = validator("feature.schema.json")
    for i, f in enumerate(features):
        error = next(feature_validator.iter_errors(f), None)
        if error is not None:
            name = (f.get("properties") or {}).get("shapeName", "?")
            report.err(f"{label}: feature {i} ('{name}') {_describe(error)}")
            break

    facts.ids = [f["id"] for f in features if isinstance(f.get("id"), str)]
    dupes = [k for k, c in Counter(facts.ids).items() if c > 1]
    if dupes:
        report.err(f"{label}: duplicate feature ids {sorted(dupes)[:5]}")
    facts.parents = [
        f["properties"]["parentID"]
        for f in features
        if isinstance((f.get("properties") or {}).get("parentID"), str)
    ]

    if "bbox" in data:
        want = bbox_of(features)
        got = [round(float(v), 6) for v in data["bbox"]] if len(data["bbox"]) == 4 else None
        if got != want:
            report.err(f"{label}: bbox {data['bbox']} does not match the coordinates {want}")

    # 6 decimal places is ~11 cm; anything finer is noise occupying real bytes.
    # Sampled from the head of the file: one offending vertex means the whole
    # file was written without rounding.
    m = PRECISION.search(raw[:262_144])
    if m:
        report.warn(f"{label}: coordinate precision beyond 6 decimals ({m.group(0)})")
    return facts


def check_country(d: Path, report: Report, checksums: bool = False) -> None:
    rel_dir = rel(d)
    mpath = d / "manifest.json"
    if not mpath.exists():
        report.err(f"{rel_dir}: no manifest.json")
        return

    try:
        manifest = json.loads(mpath.read_text("utf-8"))
    except Exception as exc:
        report.err(f"{rel_dir}: manifest.json is not valid JSON ({exc})")
        return

    schema_errors = list(validator("manifest.schema.json").iter_errors(manifest))
    for error in schema_errors[:10]:
        report.err(f"{rel_dir}/manifest.json: {_describe(error)}")
    if not isinstance(manifest, dict):
        return

    datasets = manifest.get("datasets") or []
    if isinstance(manifest.get("iso_a3"), str) and manifest["iso_a3"] != d.name:
        report.err(f"{rel_dir}: manifest iso_a3 '{manifest['iso_a3']}' does not match the folder")

    # File-level checks, collecting facts for the cross-checks below.
    facts: dict[str, FileFacts] = {}
    for f in sorted(d.rglob("*.geojson"), key=lambda p: p.relative_to(d).as_posix()):
        if "preview" in f.parts:
            continue
        facts[f.relative_to(d).as_posix()] = check_geojson(f, rel(f), report)

    ids_by_level: dict[str, set[str]] = {}
    for fact in facts.values():
        for fid in fact.ids:
            level = fid.split(":")[1] if fid.count(":") >= 2 else "?"
            ids_by_level.setdefault(level, set()).add(fid)
    for name, fact in facts.items():
        missing = sorted(
            {p for p in fact.parents if p not in ids_by_level.get(p.split(":")[1], set())}
        )
        if missing:
            report.err(f"{rel_dir}/{name}: parentID targets do not exist: {missing[:3]}")

    def check_file_entry(entry: dict, label: str, required: bool) -> None:
        path = entry.get("path")
        if not path:
            if required:
                report.err(f"{label}: manifest entry has no path")
            return
        p = data_base() / path
        if not p.exists():
            report.err(f"{label}: {path} is missing")
            return
        fact = facts.get(p.relative_to(d).as_posix()) if p.is_relative_to(d) else None
        if fact is not None and entry.get("features") != fact.features:
            report.err(
                f"{label}: manifest says {entry.get('features')} features, "
                f"the file holds {fact.features}"
            )
        if checksums:
            if entry.get("bytes") != p.stat().st_size:
                report.err(f"{label}: manifest bytes {entry.get('bytes')} != {p.stat().st_size}")
            if entry.get("sha256") != sha256(p):
                report.err(f"{label}: sha256 does not match {path}")

    for ds in datasets:
        if not isinstance(ds, dict):
            continue
        level = ds.get("level", "?")
        label = f"{rel_dir} {level}"
        parts = ds.get("parts") or []
        check_file_entry(ds, label, required=not parts)

        if parts:
            total = sum(p.get("features", 0) for p in parts)
            if total != ds.get("features"):
                report.err(
                    f"{label}: parts sum to {total} features but the level "
                    f"reports {ds.get('features')} — the split lost or "
                    f"duplicated geometry"
                )
            for part in parts:
                check_file_entry(part, f"{label} {part.get('code', '?')}", required=True)

        preview = ds.get("preview")
        if preview:
            p = data_base() / preview
            if not p.exists():
                report.err(f"{label}: preview {preview} is missing")
            elif p.stat().st_size > MAX_PREVIEW_BYTES:
                report.err(
                    f"{label}: preview is {p.stat().st_size / 1024 / 1024:.1f} MB, "
                    f"over the 2 MB budget"
                )
        else:
            report.warn(f"{label}: no preview — the catalog map will be empty")


def check_index(report: Report, data: Path | None = None) -> None:
    index = (data or data_dir()) / "index.json"
    if not index.exists():
        report.warn("data/index.json is missing — run: wgj index")
        return
    try:
        doc = json.loads(index.read_text("utf-8"))
    except Exception as exc:
        report.err(f"data/index.json: not valid JSON ({exc})")
        return
    for error in list(validator("index.schema.json").iter_errors(doc))[:10]:
        report.err(f"data/index.json: {_describe(error)}")


def check_registry(report: Report) -> None:
    doc = raw_registry("countries.json")
    for error in list(validator("countries.schema.json").iter_errors(doc))[:10]:
        report.err(f"wgj/tables/countries.json: {_describe(error)}")


def validate(dirs: list[Path], checksums: bool = False) -> Report:
    report = Report()
    for d in dirs:
        check_country(d, report, checksums=checksums)
        report.checked += 1
    return report


def discover(data: Path | None = None) -> list[Path]:
    """Every data/<body>/<code>/ directory, in a platform-independent order."""
    return country_dirs(data)


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
    ap.add_argument(
        "--checksums",
        action="store_true",
        help="also compare every file's bytes and SHA-256 with its manifest entry",
    )
    args = ap.parse_args(argv)

    whole_tree = not args.dirs
    if args.dirs:
        dirs = []
        for raw in args.dirs:
            d = raw.resolve()
            if not d.is_dir():
                ap.error(f"{raw}: not a directory")
            dirs.append(d)
    else:
        if not data_dir().exists():
            print("no data/ directory — nothing to validate")
            return 0
        dirs = discover()
        if not dirs:
            print("no datasets found under data/")
            return 0

    report = validate(dirs, checksums=args.checksums)
    if whole_tree:
        check_index(report)
        check_registry(report)

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
