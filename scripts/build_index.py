"""Write data/index.json: every territory and dataset in one file.

    python scripts/build_index.py
    python scripts/build_index.py --check     # CI: exit 1 if the committed file is stale

One request instead of fifty-five. Each country's manifest is embedded
verbatim (so the index never disagrees with a manifest) plus a few derived
fields a client needs before it has downloaded anything: the published
levels, the licences that actually govern the files, which level is the
municipal tier and what the tiers are called locally (from the registry).

Deliberately no timestamp and no version field: the file must be
byte-deterministic so that CI can regenerate it and `git diff --quiet`. The
data version is the git tag the consumer asked for.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_data import COUNTRIES

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"
INDEX = DATA / "index.json"
SCHEMA_VERSION = 1

# Manifest keys that are copied into each country entry, in this order.
IDENTITY = ("body", "iso_a3", "iso_a2", "m49_region", "name", "status")


def country_entry(mpath: Path) -> dict:
    manifest = json.loads(mpath.read_text("utf-8"))
    iso3 = manifest["iso_a3"]
    reg = COUNTRIES.get(iso3, {})
    datasets = manifest.get("datasets", [])
    source = manifest.get("source") or {}

    licenses = sorted({d["license"] for d in datasets if d.get("license")})
    entry: dict = {k: manifest[k] for k in IDENTITY if k in manifest}
    entry["manifest"] = mpath.relative_to(REPO).as_posix()
    entry["license"] = source.get("license", licenses[0] if len(licenses) == 1 else "mixed")
    entry["licenses"] = licenses or [source["license"]]
    entry["levels"] = [d["level"] for d in datasets]
    entry["municipal_level"] = reg.get("municipal_level")

    terms = {}
    for key, out in (("adm1_term", "adm1"), ("adm2_term", "adm2"), ("municipal_term", "municipal")):
        if reg.get(key):
            terms[out] = reg[key]
    if terms:
        entry["terms"] = terms

    entry["crs"] = manifest["crs"]
    entry["source"] = source
    if manifest.get("notes"):
        entry["notes"] = manifest["notes"]
    entry["datasets"] = datasets
    return entry


def build_index(data: Path = DATA) -> dict:
    # Sort on the string form, not the Path: WindowsPath compares
    # case-insensitively while PosixPath does not.
    manifests = sorted(data.glob("*/*/manifest.json"), key=lambda p: p.as_posix())
    countries = [country_entry(m) for m in manifests]
    countries.sort(key=lambda c: (c["body"], c["iso_a3"]))

    datasets = [d for c in countries for d in c["datasets"]]
    return {
        "schema_version": SCHEMA_VERSION,
        "bodies": sorted({c["body"] for c in countries}),
        "totals": {
            "countries": len(countries),
            "datasets": len(datasets),
            "features": sum(d.get("features", 0) for d in datasets),
            "bytes": sum(d.get("bytes", 0) for d in datasets),
        },
        "countries": countries,
    }


def render(index: dict) -> str:
    return json.dumps(index, indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--check", action="store_true", help="exit 1 if data/index.json is stale")
    args = ap.parse_args(argv)

    index = build_index()
    text = render(index)
    t = index["totals"]
    summary = (
        f"{t['countries']} countries, {t['datasets']} datasets, "
        f"{t['features']:,} features, {t['bytes'] / 1024 / 1024:.1f} MB"
    )

    if args.check:
        current = INDEX.read_text("utf-8") if INDEX.exists() else None
        if current != text:
            print("::error::data/index.json is stale — run: python scripts/build_index.py")
            return 1
        print(f"data/index.json is up to date ({summary})")
        return 0

    INDEX.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {INDEX.relative_to(REPO).as_posix()} ({summary})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
