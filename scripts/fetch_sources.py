"""Download source boundary data into .cache/sources/.

    python scripts/fetch_sources.py --continent americas --dry-run
    python scripts/fetch_sources.py --continent americas
    python scripts/fetch_sources.py --iso3 CHL

Nothing here writes to data/ — that is build_data.py's job. The cache is
git-ignored.

Licence filtering happens at this stage, on purpose. geoBoundaries' `gbOpen`
release is a container of heterogeneous upstream licences, not a uniformly
CC BY 4.0 dataset: a third of its Americas entries are ODbL or CC-BY-SA. Data
that cannot be redistributed should never reach the working tree, let alone git
history, where removing it means rewriting history and breaking every clone.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CACHE = REPO / ".cache" / "sources"
COUNTRIES = {
    k: v
    for k, v in json.loads(
        (REPO / "scripts" / "countries.json").read_text("utf-8")
    ).items()
    if not k.startswith("$")  # drop the `$comment` block
}

GB_ALL = "https://www.geoboundaries.org/api/current/gbOpen/ALL/ALL/"
NE_ADM0 = (
    "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/"
    "geojson/ne_10m_admin_0_countries.geojson"
)
IDE_CHILE_DPA = (
    "https://geoportal.cl/geoportal/catalog/download/"
    "912598ad-ac92-35f6-8045-098f214bd9c2"
)

CONTINENTS = {
    "americas": {
        "Northern America",
        "Central America",
        "Caribbean",
        "South America",
    }
}

# Matched case-insensitively against geoBoundaries' free-text `boundaryLicense`.
# Anything not matching here is refused — including every ODbL and CC-BY-SA
# variant. Kept deliberately conservative: an unrecognised licence is a reason
# to stop and read it, not to guess.
PERMISSIVE = [
    (re.compile(r"public domain", re.I), "public-domain"),
    (re.compile(r"\bCC0\b", re.I), "CC0-1.0"),
    (re.compile(r"creative commons attribution 4\.0|CC[ -]BY[ -]4\.0", re.I), "CC-BY-4.0"),
    (re.compile(r"attribution 3\.0 intergovernmental|CC[ -]BY[ -]3\.0 IGO", re.I), "CC-BY-3.0-IGO"),
    (re.compile(r"creative commons attribution 3\.0|CC[ -]BY[ -]3\.0", re.I), "CC-BY-3.0"),
    (re.compile(r"creative commons attribution 2\.5|CC[ -]BY[ -]2\.5", re.I), "CC-BY-2.5"),
    (re.compile(r"etalab", re.I), "Etalab-2.0"),
    # geoBoundaries writes this as "Open Government Canada 2.0" — no "licence".
    (re.compile(r"open government.*canada", re.I), "OGL-Canada-2.0"),
]
COPYLEFT = re.compile(r"ODbL|open data commons|share.?alike|CC[ -]BY[ -]SA", re.I)


def spdx(license_text: str) -> str | None:
    """Map geoBoundaries' free-text licence onto an SPDX id, or None."""
    if not license_text or COPYLEFT.search(license_text):
        return None
    for pattern, ident in PERMISSIVE:
        if pattern.search(license_text):
            return ident
    return None


def fetch(url: str, dest: Path, expect_json: bool = False) -> None:
    """Download with the checks a naive script skips.

    Two specific traps: geoBoundaries' repository uses Git LFS, so
    raw.githubusercontent.com serves ~130-byte pointer stubs rather than data;
    and a missing level answers 404 with a ~302 KB HTML page, which passes any
    "the file is not empty" test.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "World-GeoJSON/1.0"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        if resp.status != 200:
            raise RuntimeError(f"HTTP {resp.status}")
        ctype = (resp.headers.get("Content-Type") or "").lower()
        if "text/html" in ctype:
            raise RuntimeError(f"served HTML, not data (Content-Type: {ctype})")
        data = resp.read()

    if data.startswith(b"version https://git-lfs"):
        raise RuntimeError("got a Git LFS pointer, not the file contents")
    if len(data) < 1024:
        raise RuntimeError(f"suspiciously small ({len(data)} bytes)")
    if expect_json:
        try:
            json.loads(data)
        except Exception as exc:  # noqa: BLE001
            raise RuntimeError(f"not valid JSON: {exc}") from exc

    dest.write_bytes(data)


def geoboundaries_catalogue() -> list[dict]:
    cat = CACHE / "geoboundaries-all.json"
    if not cat.exists():
        print(f"fetching the geoBoundaries catalogue ({GB_ALL})")
        fetch(GB_ALL, cat, expect_json=True)
    return json.loads(cat.read_text("utf-8"))


def plan(iso3s: set[str]) -> tuple[list[dict], list[dict]]:
    """Decide what to take. Returns (accepted, rejected)."""
    accepted, rejected = [], []
    wanted_levels = {}
    for iso3 in iso3s:
        entry = COUNTRIES[iso3]
        levels = {"ADM1"}
        if entry.get("municipal_level"):
            levels.add(entry["municipal_level"])
        wanted_levels[iso3] = levels

    for rec in geoboundaries_catalogue():
        iso3 = rec.get("boundaryISO")
        level = rec.get("boundaryType")
        if iso3 not in iso3s or level not in wanted_levels.get(iso3, ()):
            continue
        # Chile is taken from IDE Chile instead; see build_data.build_chile.
        if COUNTRIES[iso3].get("source") != "geoboundaries":
            continue

        ident = spdx(rec.get("boundaryLicense", ""))
        row = {
            "iso3": iso3,
            "level": level,
            "license_text": rec.get("boundaryLicense", ""),
            "license": ident,
            "url": rec.get("gjDownloadURL"),
            "units": rec.get("admUnitCount"),
            "year": rec.get("boundaryYearRepresented"),
        }
        (accepted if ident and row["url"] else rejected).append(row)

    return accepted, rejected


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--continent", choices=sorted(CONTINENTS))
    ap.add_argument("--iso3", nargs="*", default=[])
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if args.iso3:
        iso3s = {c.upper() for c in args.iso3}
    elif args.continent:
        regions = CONTINENTS[args.continent]
        iso3s = {k for k, v in COUNTRIES.items() if v.get("m49_region") in regions}
    else:
        ap.error("pass --continent or --iso3")

    unknown = iso3s - set(COUNTRIES)
    if unknown:
        raise SystemExit(f"not in countries.json: {', '.join(sorted(unknown))}")

    CACHE.mkdir(parents=True, exist_ok=True)
    print(f"{len(iso3s)} territories in scope\n")

    # One global public-domain file supplies every country outline.
    ne = CACHE / "natural-earth" / "ne_10m_admin_0_countries.geojson"
    if args.dry_run:
        print(f"ADM0 would fetch Natural Earth 10m -> {ne.name}\n")
    elif ne.exists():
        print(f"ADM0 Natural Earth already cached ({ne.stat().st_size/1024/1024:.0f} MB)")
    else:
        print("ADM0 fetching Natural Earth 10m admin-0 (~13 MB)")
        fetch(NE_ADM0, ne, expect_json=True)

    if "CHL" in iso3s or COUNTRIES.get("CHL", {}).get("source") == "ide-chile":
        dpa = CACHE / "DPA_2023.zip"
        if args.dry_run:
            print(f"CHL  would fetch IDE Chile DPA 2023 -> {dpa.name}\n")
        elif dpa.exists():
            print(f"CHL  DPA 2023 already cached ({dpa.stat().st_size/1024/1024:.0f} MB)")
        else:
            print("CHL  fetching IDE Chile DPA 2023 (~297 MB)")
            fetch(IDE_CHILE_DPA, dpa)
        target = CACHE / "DPA_2023"
        if dpa.exists() and not target.exists():
            with zipfile.ZipFile(dpa) as z:
                z.extractall(target)
            print(f"     extracted to {target.relative_to(REPO)}")

    accepted, rejected = plan(iso3s)

    print(f"\nAccepted ({len(accepted)}):")
    for r in sorted(accepted, key=lambda x: (x["iso3"], x["level"])):
        print(f"  {r['iso3']} {r['level']:<5} {r['license']:<16} {r['units']:>6} units")

    if rejected:
        print(f"\nRejected on licence ({len(rejected)}):")
        for r in sorted(rejected, key=lambda x: (x["iso3"], x["level"])):
            print(f"  {r['iso3']} {r['level']:<5} {r['license_text'][:60]}")
        print(
            "\nThese are copyleft or unrecognised and cannot be redistributed "
            "here.\nSee docs/contributing/sources.md; gaps belong on the roadmap."
        )

    if args.dry_run:
        print("\ndry run — nothing downloaded")
        return 0

    failures = 0
    for r in sorted(accepted, key=lambda x: (x["iso3"], x["level"])):
        dest = CACHE / "geoboundaries" / f"{r['iso3']}_{r['level']}.geojson"
        if dest.exists():
            continue
        try:
            fetch(r["url"], dest, expect_json=True)
            print(f"  fetched {dest.name} ({dest.stat().st_size/1024/1024:.1f} MB)")
        except Exception as exc:  # noqa: BLE001
            failures += 1
            print(f"  !! {r['iso3']} {r['level']}: {exc}", file=sys.stderr)

    print(f"\ndone — {len(accepted)} datasets, {failures} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
