"""Normalise source boundary data into the repository's data/ tree.

    python scripts/build_data.py CHL

Reads from .cache/sources/ (populated by fetch_sources.py), writes to
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
import json
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CACHE = REPO / ".cache" / "sources"
DATA = REPO / "data" / "earth"

COUNTRIES = {
    k: v
    for k, v in json.loads(
        (REPO / "scripts" / "countries.json").read_text("utf-8")
    ).items()
    if not k.startswith("$")  # drop the `$comment` block
}
ISO2_MAP = json.loads((REPO / "scripts" / "iso3166_2.json").read_text("utf-8"))

# Standard simplification tolerance, in metres on the ground.
#
# This is a *distance*, not a percentage, and that choice matters. A percentage
# keeps a fixed share of each file's vertices, so the resulting ground
# resolution depends entirely on how densely the source happened to be
# digitised — two neighbouring countries end up at different fidelities. A
# distance tolerance gives every dataset in the repository the same real-world
# resolution, which is the property a coherent collection needs.
#
# Calibrated against Chile, which has one of the most complex coastlines on
# Earth: its 16 regions come to 49.7 MB at 10 m, 21.2 MB at 25 m, 10.0 MB at
# 50 m, 4.6 MB at 100 m and 1.6 MB at 250 m. 100 m is far finer than any
# administrative boundary is meaningfully surveyed to for general use, and it
# keeps even the worst case comfortably inside the CDN ceiling.
TOLERANCE_M = 100

# Hard ceiling. jsDelivr refuses files over 20 MB, so nothing may approach it.
# Applied only as a fallback: a dataset that still exceeds this at the standard
# tolerance gets a coarser one, and the value used is recorded in the manifest.
SIZE_BUDGET = 18 * 1024 * 1024

STANDARD_FIELDS = ["shapeName", "shapeISO", "shapeGroup", "shapeType", "parentISO"]


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------


_NPX = shutil.which("npx") or shutil.which("npx.cmd")


def run_mapshaper(args: list[str]) -> None:
    """Invoke mapshaper with shell=False.

    shell=True would hand the argument list to cmd.exe, which re-parses it and
    mangles the quoting inside the -each expressions. shell=False lets Python
    quote each argument correctly, which is why the JS object literals below
    can use single quotes and survive intact.
    """
    if not _NPX:
        raise SystemExit("npx not found on PATH — Node.js is required")
    proc = subprocess.run(
        [_NPX, "-y", "mapshaper", *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout or "")
        sys.stderr.write(proc.stderr or "")
        raise SystemExit(f"mapshaper failed: {' '.join(args[:4])}…")


def js_lookup(mapping: dict[str, str]) -> str:
    """A single-quoted JS object literal, safe to pass as one argv element."""
    body = ",".join(f"'{k}':'{v}'" for k, v in mapping.items())
    return "{" + body + "}"


def slug(text: str) -> str:
    ascii_text = (
        unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    )
    out = "".join(c if c.isalnum() else "-" for c in ascii_text.lower())
    while "--" in out:
        out = out.replace("--", "-")
    return out.strip("-")


def feature_count(path: Path) -> int:
    """Count features without holding the parsed file in memory."""
    import ijson

    n = 0
    with path.open("rb") as fh:
        for prefix, event, _ in ijson.parse(fh, use_float=True):
            if event == "start_map" and prefix == "features.item":
                n += 1
    return n


def js_expr(pairs: dict[str, str]) -> str:
    return ", ".join(f"{k}={v}" for k, v in pairs.items())


# ---------------------------------------------------------------------------
# simplification with a size budget
# ---------------------------------------------------------------------------


def simplify(
    src: Path, dest: Path, budget: int = SIZE_BUDGET, extra: list[str] | None = None
) -> dict:
    """Simplify to the standard ground tolerance, coarsening only if oversized.

    Returns what was actually applied, for the manifest. The standard tolerance
    is used unmodified for essentially every dataset; the doubling loop is a
    safety net for pathological inputs, not the normal path.
    """
    extra = extra or []

    def write(interval: int) -> int:
        run_mapshaper(
            [
                str(src),
                "-simplify",
                f"interval={interval}",
                "keep-shapes",
                *extra,
                "-o",
                "precision=0.000001",
                "bbox",
                "format=geojson",
                str(dest),
            ]
        )
        return dest.stat().st_size

    interval = TOLERANCE_M
    size = write(interval)
    while size > budget and interval < 10_000:
        interval *= 2
        print(f"      over budget at {interval // 2} m, retrying at {interval} m")
        size = write(interval)

    if size > budget:
        raise SystemExit(
            f"{dest.name}: {size/1024/1024:.1f} MB still exceeds the budget at "
            f"{interval} m tolerance"
        )

    print(f"      {interval} m tolerance  ->  {size/1024/1024:.1f} MB")
    return {"method": "visvalingam", "tolerance_m": interval}


# ---------------------------------------------------------------------------
# Chile — IDE Chile DPA 2023
# ---------------------------------------------------------------------------


def build_chile() -> list[dict]:
    """Chile comes from IDE Chile DPA 2023, not geoBoundaries.

    geoBoundaries' Chile is a three-source mix whose ADM2 (provinces) is
    OpenStreetMap under ODbL — copyleft, and therefore excluded from this
    repository. DPA 2023 gives all three tiers from one CC BY source, in one
    vintage, with CUT codes already stored as zero-padded strings.
    """
    src_dir = CACHE / "DPA_2023"
    if not src_dir.exists():
        raise SystemExit(f"missing {src_dir} — run fetch_sources.py first")

    out_dir = DATA / "CHL"
    out_dir.mkdir(parents=True, exist_ok=True)
    codes = {k: v for k, v in ISO2_MAP["CHL"].items() if not k.startswith("_")}
    results: list[dict] = []

    # --- ADM1: regions -----------------------------------------------------
    print("  ADM1 (regiones)")
    adm1_out = out_dir / "CHL_ADM1.geojson"
    iso_lookup = js_lookup(codes)
    simp = simplify(
        src_dir / "REGIONES" / "REGIONES_v1.shp",
        adm1_out,
        extra=[
            "-each",
            js_expr(
                {
                    "shapeName": "REGION",
                    "shapeISO": f"({iso_lookup})[CUT_REG] || CUT_REG",
                    "shapeGroup": "'CHL'",
                    "shapeType": "'ADM1'",
                    "src_cut_reg": "CUT_REG",
                    "src_superficie_km2": "SUPERFICIE",
                }
            ),
            "-filter-fields",
            ",".join(STANDARD_FIELDS[:4] + ["src_cut_reg", "src_superficie_km2"]),
        ],
    )
    results.append({"level": "ADM1", "path": adm1_out, "simplification": simp})

    # --- ADM2: provinces ---------------------------------------------------
    print("  ADM2 (provincias)")
    adm2_out = out_dir / "CHL_ADM2.geojson"
    simp = simplify(
        src_dir / "PROVINCIAS" / "PROVINCIAS_v1.shp",
        adm2_out,
        extra=[
            "-each",
            js_expr(
                {
                    "shapeName": "PROVINCIA",
                    "shapeISO": "CUT_PROV",
                    "shapeGroup": "'CHL'",
                    "shapeType": "'ADM2'",
                    "parentISO": f"({iso_lookup})[CUT_REG] || CUT_REG",
                    "src_cut_prov": "CUT_PROV",
                    "src_cut_reg": "CUT_REG",
                    "src_region": "REGION",
                }
            ),
            "-filter-fields",
            ",".join(STANDARD_FIELDS + ["src_cut_prov", "src_cut_reg", "src_region"]),
        ],
    )
    results.append({"level": "ADM2", "path": adm2_out, "simplification": simp})

    # --- ADM3: communes, split by region ----------------------------------
    print("  ADM3 (comunas, split by region)")
    adm3_dir = out_dir / "ADM3"
    if adm3_dir.exists():
        shutil.rmtree(adm3_dir)
    adm3_dir.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        combined = Path(tmp) / "CHL_ADM3.geojson"
        simp = simplify(
            src_dir / "COMUNAS" / "COMUNAS_v1.shp",
            combined,
            extra=[
                "-each",
                js_expr(
                    {
                        "shapeName": "COMUNA",
                        "shapeISO": "CUT_COM",
                        "shapeGroup": "'CHL'",
                        "shapeType": "'ADM3'",
                        # Immediate parent is the province, per the official
                        # hierarchy Región > Provincia > Comuna. The file the
                        # feature lands in is keyed by region — see naming.md.
                        "parentISO": "CUT_PROV",
                        "adm1ISO": f"({iso_lookup})[CUT_REG] || CUT_REG",
                        "src_cut_com": "CUT_COM",
                        "src_cut_prov": "CUT_PROV",
                        "src_cut_reg": "CUT_REG",
                        "src_provincia": "PROVINCIA",
                        "src_region": "REGION",
                    }
                ),
                "-filter-fields",
                ",".join(
                    STANDARD_FIELDS
                    + [
                        "adm1ISO",
                        "src_cut_com",
                        "src_cut_prov",
                        "src_cut_reg",
                        "src_provincia",
                        "src_region",
                    ]
                ),
            ],
        )

        total = feature_count(combined)
        print(f"      {total} communes total")

        # Split by region. mapshaper names outputs after the split value.
        run_mapshaper(
            [
                str(combined),
                "-split",
                "adm1ISO",
                "-o",
                "precision=0.000001",
                "bbox",
                "format=geojson",
                str(adm3_dir),
            ]
        )

        parts = []
        for f in sorted(adm3_dir.glob("*.json")) + sorted(adm3_dir.glob("*.geojson")):
            code = f.stem
            target = adm3_dir / f"{code}.geojson"
            if f != target:
                f.rename(target)
            parts.append(target)

        combined_size = combined.stat().st_size
        # Only publish a whole-country file when it fits the CDN ceiling.
        if combined_size <= SIZE_BUDGET:
            shutil.copyfile(combined, out_dir / "CHL_ADM3.geojson")
            print(f"      combined file published ({combined_size/1024/1024:.1f} MB)")
        else:
            print(
                f"      combined file omitted ({combined_size/1024/1024:.1f} MB "
                f"exceeds the {SIZE_BUDGET/1024/1024:.0f} MB CDN budget)"
            )

    results.append({"level": "ADM3", "path": adm3_dir, "simplification": simp, "split": True})
    return results


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


BUILDERS = {"ide-chile": build_chile}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("iso3", nargs="+", help="ISO 3166-1 alpha-3 codes")
    args = ap.parse_args()

    for iso3 in args.iso3:
        entry = COUNTRIES.get(iso3.upper())
        if not entry:
            raise SystemExit(f"{iso3}: not in scripts/countries.json")
        source = entry.get("source")
        builder = BUILDERS.get(source)
        if not builder:
            raise SystemExit(f"{iso3}: no builder for source '{source}' yet")
        print(f"{iso3.upper()} — {entry['name']['en']} (source: {source})")
        builder()
    print("\nNow run: python scripts/build_manifest.py data/earth/<ISO3>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
