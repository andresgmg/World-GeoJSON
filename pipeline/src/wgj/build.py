"""Normalise source boundary data into the repository's data/ tree.

    wgj build CHL

Reads from .cache/sources/ (populated by `wgj fetch`), writes to
data/earth/{ISO3}/.

Geometry work is delegated to mapshaper via `npx`. That is deliberate: mapshaper
does topology-preserving simplification, shapefile reading, spatial joins and
splitting correctly and in one process, and it avoids adding a heavyweight GDAL
dependency to a repository whose contributors are mostly not Python developers.

Resolution policy
-----------------
Full-resolution source data is not viable on GitHub — geoBoundaries' Canada
ADM1 is 618 MiB for 13 polygons, and four Americas files exceed GitHub's hard
100 MiB block. Every output is therefore simplified to a fixed ground
tolerance (TOLERANCE_M), which is recorded in the manifest. Resolution has to
be transparent, not magic.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from collections.abc import Callable

from wgj.licensing import spdx
from wgj.paths import earth
from wgj.registry import CONTINENTS, countries, resolve_targets
from wgj.sources import SOURCE_INFO
from wgj.sources.geoboundaries import build_geoboundaries, gb_metadata, resplit_municipal
from wgj.sources.ide_chile import build_chile
from wgj.sources.natural_earth import build_adm0

BUILDERS: dict[str, Callable[..., list[dict]]] = {
    "ide-chile": build_chile,
    "geoboundaries": build_geoboundaries,
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("iso3", nargs="*", help="ISO 3166-1 alpha-3 codes")
    ap.add_argument("--continent", choices=sorted(CONTINENTS))
    ap.add_argument(
        "--skip-existing",
        action="store_true",
        help="leave countries that already have a data directory alone",
    )
    ap.add_argument(
        "--resplit",
        action="store_true",
        help="re-derive municipal parts from the committed files instead of building",
    )
    args = ap.parse_args(argv)
    targets = resolve_targets(args.iso3, args.continent)

    built, skipped, failed = [], [], []
    retrieved = dt.date.today().isoformat()

    if args.resplit:
        for iso3 in targets:
            entry = countries().get(iso3)
            if not entry:
                raise SystemExit(f"{iso3}: not in the country registry")
            resplit_municipal(iso3, entry)
        return 0

    for iso3 in targets:
        entry = countries().get(iso3)
        if not entry:
            raise SystemExit(f"{iso3}: not in the country registry")

        if args.skip_existing and (earth() / iso3).exists():
            skipped.append(iso3)
            continue

        print(f"\n{iso3} — {entry['name']['en']} ({entry.get('source')})")
        try:
            results = []
            adm0 = build_adm0(iso3, entry)
            if adm0:
                results.append(adm0)

            builder = BUILDERS.get(entry["source"])
            if builder is build_chile:
                results += build_chile()
            elif builder:
                results += builder(iso3, entry)

            if results:
                built.append(iso3)
                record_provenance(iso3, results, retrieved)
                # Ids, hierarchy, shapeISO corrections, bbox, canonical layout.
                from wgj.finalize import Country

                country = Country(earth() / iso3)
                country.finalize()
                for w in country.warnings:
                    print(f"      ! {w}")
                country.write()
            else:
                print("  nothing produced")
                failed.append(iso3)
        except SystemExit:
            raise
        except Exception as exc:
            print(f"  !! failed: {exc}")
            failed.append(iso3)

    print(f"\nbuilt {len(built)}, skipped {len(skipped)}, failed {len(failed)}")
    if failed:
        print("failed: " + ", ".join(failed))
    print("\nNow run: wgj previews && wgj manifest data/earth/*/ && wgj index")
    # A non-zero exit is what lets a shell loop or CI notice the failures.
    return 1 if failed else 0


def record_provenance(iso3: str, results: list[dict], retrieved: str) -> None:
    """Write identity, per-dataset provenance and the applied tolerance.

    `wgj manifest` preserves everything outside `datasets`, and carries
    forward the per-dataset keys it does not compute itself.
    """
    entry = countries()[iso3]
    mpath = earth() / iso3 / "manifest.json"
    manifest = json.loads(mpath.read_text("utf-8")) if mpath.exists() else {}

    manifest.setdefault("schema_version", 1)
    # Identity is derived from the registry and the folder, so it is always
    # rewritten. `name`, `status` and `notes` are hand-editable per
    # docs/reference/manifest.md, so an existing value wins.
    manifest["body"] = "earth"
    manifest["iso_a3"] = iso3
    manifest["iso_a2"] = entry["iso_a2"]
    manifest["m49_region"] = entry["m49_region"]
    manifest.setdefault("name", entry["name"])
    manifest["crs"] = {"authority": "OGC", "code": "CRS84", "epsg": 4326}
    manifest.setdefault("status", "review" if entry.get("verify") else "ok")

    provider = SOURCE_INFO[entry["source"]]
    source = manifest.get("source") or {}
    source.setdefault("name", provider["name"])
    source.setdefault("url", provider["url"])
    source.setdefault("retrieved", retrieved)
    manifest["source"] = source
    if entry.get("note") and "notes" not in manifest:
        manifest["notes"] = entry["note"]

    by_level = {d.get("level"): d for d in manifest.get("datasets", [])}
    for r in results:
        ds = by_level.setdefault(r["level"], {"level": r["level"]})
        if r.get("simplification"):
            ds["simplification"] = r["simplification"]
        # Always reset: a rebuild that places every feature must clear the
        # count a previous run recorded, not leave it behind.
        ds.pop("unassigned", None)
        if r.get("unassigned"):
            ds["unassigned"] = r["unassigned"]

        if r["level"] == "ADM0":
            ds["license"] = "public-domain"
            ds["src_provider"] = "Natural Earth"
        elif entry["source"] == "geoboundaries":
            meta = gb_metadata(iso3, r["level"])
            ident = spdx(meta.get("boundaryLicense", ""))
            if not ident:
                raise SystemExit(
                    f"{iso3} {r['level']}: upstream licence "
                    f"'{meta.get('boundaryLicense')}' is not permissive — this "
                    f"dataset should never have been fetched"
                )
            ds["license"] = ident
            if meta.get("boundarySource"):
                ds["src_provider"] = meta["boundarySource"]
            if meta.get("boundaryYearRepresented"):
                ds["src_year"] = meta["boundaryYearRepresented"]
        else:
            ds["license"] = provider.get("license", "CC-BY-4.0")

    manifest["datasets"] = [by_level[k] for k in sorted(by_level)]

    # Derive the country-level licence from the datasets rather than assuming
    # one. A country whose only dataset is a public-domain Natural Earth
    # outline must not be labelled CC BY, and several here mix licences across
    # levels — Argentina's ADM1 is CC BY 2.5 and its ADM2 CC BY 3.0 IGO.
    licenses = sorted({d["license"] for d in manifest["datasets"] if d.get("license")})
    if len(licenses) == 1:
        source["license"] = licenses[0]
        source.pop("licenses", None)
    elif licenses:
        source["license"] = "mixed"
        source["licenses"] = licenses

    mpath.parent.mkdir(parents=True, exist_ok=True)
    mpath.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
        newline="\n",
    )
