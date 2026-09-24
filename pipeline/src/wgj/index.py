"""Write data/index.json: every territory and dataset in one file.

    wgj index
    wgj index --check     # CI: exit 1 if the committed file is stale

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
from pathlib import Path

from wgj.paths import data_dir, rel
from wgj.registry import countries

SCHEMA_VERSION = 1

# Manifest keys that are copied into each country entry, in this order.
IDENTITY = ("body", "iso_a3", "iso_a2", "m49_region", "name", "status")


def index_path() -> Path:
    return data_dir() / "index.json"


def country_entry(mpath: Path) -> dict:
    manifest = json.loads(mpath.read_text("utf-8"))
    iso3 = manifest["iso_a3"]
    reg = countries().get(iso3, {})
    datasets = manifest.get("datasets", [])
    source = manifest.get("source") or {}

    licenses = sorted({d["license"] for d in datasets if d.get("license")})
    entry: dict = {k: manifest[k] for k in IDENTITY if k in manifest}
    entry["manifest"] = rel(mpath)
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


def build_index(data: Path | None = None) -> dict:
    data = data or data_dir()
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
        current = index_path().read_text("utf-8") if index_path().exists() else None
        if current != text:
            print("::error::data/index.json is stale — run: wgj index")
            return 1
        print(f"data/index.json is up to date ({summary})")
        return 0

    index_path().write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {rel(index_path())} ({summary})")
    return 0
