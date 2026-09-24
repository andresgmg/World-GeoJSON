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
import datetime as dt
import json
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fetch_sources import spdx

REPO = Path(__file__).resolve().parents[1]
CACHE = REPO / ".cache" / "sources"
DATA = REPO / "data" / "earth"

COUNTRIES = {
    k: v
    for k, v in json.loads((REPO / "scripts" / "countries.json").read_text("utf-8")).items()
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


def _mapshaper_cmd() -> list[str]:
    """Prefer the pinned local install over `npx -y`.

    `npx -y mapshaper` re-resolves the package on every invocation, and a full
    continent means hundreds of them; concurrent runs then collide on the npm
    cache and fail intermittently. `npm install` pins the version in
    package.json, which also makes the pipeline reproducible.
    """
    local = REPO / "node_modules" / ".bin"
    for name in ("mapshaper.cmd", "mapshaper"):
        candidate = local / name
        if candidate.exists():
            return [str(candidate)]
    npx = shutil.which("npx") or shutil.which("npx.cmd")
    if not npx:
        raise SystemExit("mapshaper not found — run `npm install`")
    return [npx, "-y", "mapshaper"]


_MAPSHAPER: list[str] | None = None


def mapshaper_cmd() -> list[str]:
    """Resolve mapshaper on first use, not at import.

    Resolving at import made the module unimportable on a machine without
    Node — including the test runner — even for the pure helpers below.
    """
    global _MAPSHAPER
    if _MAPSHAPER is None:
        _MAPSHAPER = _mapshaper_cmd()
    return _MAPSHAPER


def run_mapshaper(args: list[str]) -> None:
    """Invoke mapshaper with shell=False.

    shell=True would hand the argument list to cmd.exe, which re-parses it and
    mangles the quoting inside the -each expressions. shell=False lets Python
    quote each argument correctly, which is why the JS object literals below
    can use single quotes and survive intact.
    """
    proc = subprocess.run(
        [*mapshaper_cmd(), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if proc.returncode != 0:
        detail = ((proc.stderr or "") + (proc.stdout or "")).strip().splitlines()
        tail = detail[-1] if detail else "no output"
        # RuntimeError, not SystemExit: main() catches it per country so one
        # bad dataset does not abandon the other fifty-six.
        raise RuntimeError(f"mapshaper: {tail}")


def js_lookup(mapping: dict[str, str]) -> str:
    """A single-quoted JS object literal, safe to pass as one argv element."""
    body = ",".join(f"'{k}':'{v}'" for k, v in mapping.items())
    return "{" + body + "}"


def slug(text: str) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
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
    src: Path,
    dest: Path,
    budget: int | None = SIZE_BUDGET,
    extra: list[str] | None = None,
    pre: list[str] | None = None,
) -> dict:
    """Simplify to the standard ground tolerance, coarsening only if oversized.

    Returns what was actually applied, for the manifest. The standard tolerance
    is used unmodified for essentially every dataset; the doubling loop is a
    safety net for pathological inputs, not the normal path.

    `budget=None` disables size-driven coarsening. Split levels use that: their
    canonical artefacts are the per-parent parts, and judging the level by the
    size of an *optional* whole-country file would needlessly degrade
    resolution — Brazil's 5,570 municipalities blow the ceiling as one file
    while every per-state file fits at the standard tolerance with room to
    spare.
    """
    extra = extra or []
    # `pre` runs before -simplify. Filtering there matters: the Natural Earth
    # source is one global file, and simplifying all 258 countries before
    # discarding 257 of them would be absurd.
    pre = pre or []

    def write(interval: int) -> int:
        run_mapshaper(
            [
                str(src),
                *pre,
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
    if budget is not None:
        while size > budget and interval < 10_000:
            interval *= 2
            print(f"      over budget at {interval // 2} m, retrying at {interval} m")
            size = write(interval)

        if size > budget:
            raise RuntimeError(
                f"{dest.name}: {size / 1024 / 1024:.1f} MB still exceeds the budget "
                f"at {interval} m tolerance"
            )

    print(f"      {interval} m tolerance  ->  {size / 1024 / 1024:.1f} MB")
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
            ",".join([*STANDARD_FIELDS[:4], "src_cut_reg", "src_superficie_km2"]),
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
            ",".join([*STANDARD_FIELDS, "src_cut_prov", "src_cut_reg", "src_region"]),
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
                    [
                        *STANDARD_FIELDS,
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
            print(f"      combined file published ({combined_size / 1024 / 1024:.1f} MB)")
        else:
            print(
                f"      combined file omitted ({combined_size / 1024 / 1024:.1f} MB "
                f"exceeds the {SIZE_BUDGET / 1024 / 1024:.0f} MB CDN budget)"
            )

    results.append({"level": "ADM3", "path": adm3_dir, "simplification": simp, "split": True})
    return results


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Natural Earth — country outlines
# ---------------------------------------------------------------------------


_NE_CODES: set[str] | None = None


def natural_earth_codes(src: Path) -> set[str]:
    """Every ADM0_A3 / ISO_A3 present in the global file, parsed once."""
    global _NE_CODES
    if _NE_CODES is None:
        data = json.loads(src.read_text("utf-8"))
        _NE_CODES = set()
        for f in data.get("features", []):
            p = f.get("properties") or {}
            for key in ("ADM0_A3", "ISO_A3"):
                v = p.get(key)
                if v and v != "-99":
                    _NE_CODES.add(v)
    return _NE_CODES


def build_adm0(iso3: str, entry: dict) -> dict | None:
    """Carve one country's outline out of the global Natural Earth file.

    Natural Earth rather than geoBoundaries for ADM0: it is public domain, a
    single coherent generalisation instead of 51 per-country files of wildly
    varying quality, and it covers the six Americas territories geoBoundaries
    has no ADM0 for at all.
    """
    src = CACHE / "natural-earth" / "ne_10m_admin_0_countries.geojson"
    if not src.exists():
        print("  ADM0 skipped — Natural Earth not cached")
        return None

    # Check membership up front. mapshaper aborts with a confusing
    # "Table is missing one or more fields" when a filter matches nothing,
    # because an empty table has no columns for -filter-fields to keep.
    if iso3 not in natural_earth_codes(src):
        print(f"  ADM0 — {iso3} is not in Natural Earth")
        return None

    out_dir = DATA / iso3
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / f"{iso3}_ADM0.geojson"

    print("  ADM0")
    simp = simplify(
        src,
        dest,
        # ADM0_A3 rather than ISO_A3: Natural Earth sets ISO_A3 to "-99" for
        # territories whose status is contested, and those are exactly the ones
        # we still want to ship. Filtering happens before simplification.
        pre=["-filter", f"ADM0_A3 === '{iso3}' || ISO_A3 === '{iso3}'"],
        extra=[
            "-each",
            js_expr(
                {
                    "shapeName": "NAME_LONG || NAME",
                    "shapeISO": f"'{iso3}'",
                    "shapeGroup": f"'{iso3}'",
                    "shapeType": "'ADM0'",
                }
            ),
            "-filter-fields",
            "shapeName,shapeISO,shapeGroup,shapeType",
        ],
    )

    if feature_count(dest) == 0:
        dest.unlink()
        print("  ADM0 — not present in Natural Earth")
        return None
    return {"level": "ADM0", "simplification": simp}


# ---------------------------------------------------------------------------
# geoBoundaries
# ---------------------------------------------------------------------------


def adm1_key_expr() -> str:
    """ISO 3166-2 where geoBoundaries provides it, a name slug otherwise.

    shapeISO is documented as "where available" and in practice a great many
    countries ship an empty string, so the fallback is not an edge case.

    The result becomes a filename when the municipal level is split, so it is
    sanitised. That is not theoretical: geoBoundaries ships an Ecuadorian
    province coded `EC-D*`, and the asterisk is illegal in a Windows filename —
    mapshaper fails with ENOENT halfway through writing the split. Real ISO
    3166-2 codes only ever contain letters, digits and a hyphen, so this can
    only ever alter a malformed upstream value.
    """
    return (
        "(shapeISO && shapeISO !== 'None' ? shapeISO : "
        "String(shapeName || 'unknown')"
        ".normalize('NFKD').replace(/[\\u0300-\\u036f]/g, '')"
        ".toLowerCase())"
        ".replace(/[^A-Za-z0-9-]+/g, '-').replace(/^-+|-+$/g, '')"
    )


def gb_source(iso3: str, level: str) -> Path | None:
    p = CACHE / "geoboundaries" / f"{iso3}_{level}.geojson"
    return p if p.exists() else None


def build_gb_adm1(iso3: str, out_dir: Path) -> tuple[dict | None, Path | None]:
    src = gb_source(iso3, "ADM1")
    if not src:
        return None, None

    dest = out_dir / f"{iso3}_ADM1.geojson"
    simp = simplify(
        src,
        dest,
        extra=[
            "-each",
            js_expr(
                {
                    "shapeISO": adm1_key_expr(),
                    "shapeGroup": f"'{iso3}'",
                    "shapeType": "'ADM1'",
                    "src_shape_id": "shapeID",
                }
            ),
            "-filter-fields",
            "shapeName,shapeISO,shapeGroup,shapeType,src_shape_id",
        ],
    )
    return {"level": "ADM1", "simplification": simp}, dest


def assign_parents(muni: Path, adm1: Path, dest: Path) -> int:
    """Attach each municipality's ADM1 parent, returning the unmatched count.

    geoBoundaries municipal files carry no reference to their parent, so it has
    to be derived. `largest-overlap` beats a centroid test here: a centroid can
    fall outside its own polygon, and independently digitised ADM1 and ADM2
    layers rarely agree exactly along their edges. On Argentina it cut the
    unmatched count from 13 to 8.

    Some genuinely cannot match. geoBoundaries publishes 23 ADM1 units for
    Argentina, but the country has 24 — the Autonomous City of Buenos Aires is
    missing — so its comunas overlap no province at all. Those are kept, not
    dropped; see build_gb_municipal.
    """
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        indexed, table = t / "m.json", t / "t.json"

        run_mapshaper([str(muni), "-each", "idx=this.id", "-o", str(indexed)])
        run_mapshaper(
            [
                str(indexed),
                # Keep only the index before joining: both layers carry a
                # shapeISO and mapshaper refuses to join same-named fields.
                "-filter-fields",
                "idx",
                "-join",
                str(adm1),
                "fields=shapeISO",
                "largest-overlap",
                "-rename-fields",
                "adm1ISO=shapeISO",
                "-o",
                "format=json",
                str(table),
            ]
        )
        rows = json.loads(table.read_text("utf-8"))
        unmatched = sum(1 for r in rows if not r.get("adm1ISO"))

        run_mapshaper(
            [
                str(indexed),
                "-join",
                str(table),
                "keys=idx,idx",
                "fields=adm1ISO",
                "-each",
                "adm1ISO = adm1ISO || 'unassigned'; delete idx",
                "-o",
                str(dest),
            ]
        )
    return unmatched


def build_gb_municipal(
    iso3: str, entry: dict, out_dir: Path, adm1_path: Path | None
) -> dict | None:
    level = entry.get("municipal_level")
    if not level or level == "ADM1":
        return None
    src = gb_source(iso3, level)
    if not src:
        return None

    normalised = out_dir / f"{iso3}_{level}.geojson"
    # No size budget here — see the note in simplify(). The parts are what
    # matter and they are checked individually below.
    simp = simplify(
        src,
        normalised,
        budget=None if adm1_path else SIZE_BUDGET,
        extra=[
            "-each",
            js_expr(
                {
                    # An empty shapeISO stays empty. finalize_geojson.py derives
                    # the feature id; it must not mistake an opaque upstream id
                    # for a code.
                    "shapeISO": "shapeISO && shapeISO !== 'None' ? shapeISO : ''",
                    "shapeGroup": f"'{iso3}'",
                    "shapeType": f"'{level}'",
                    "src_shape_id": "shapeID",
                }
            ),
            "-filter-fields",
            "shapeName,shapeISO,shapeGroup,shapeType,src_shape_id",
        ],
    )
    result: dict = {"level": level, "simplification": simp}

    if not adm1_path:
        # Puerto Rico, Guadeloupe, Martinique and French Guiana all publish a
        # municipal tier with no ADM1 above it. Nothing to split by, so the
        # whole-country file stands alone.
        print("      no ADM1 to split by — publishing whole-country only")
        if normalised.stat().st_size > SIZE_BUDGET:
            raise SystemExit(f"{normalised.name}: too large and cannot be split")
        return result

    unmatched = split_by_adm1(iso3, level, normalised, adm1_path, out_dir / level)
    if unmatched:
        result["unassigned"] = unmatched

    if normalised.stat().st_size > SIZE_BUDGET:
        normalised.unlink()
        print("      whole-country file omitted (over the CDN budget)")

    return result


def split_by_adm1(iso3: str, level: str, combined: Path, adm1_path: Path, split_dir: Path) -> int:
    """Attach ADM1 parents to `combined` and write one part per parent.

    The joined result is written back over the combined file, so the
    whole-country file carries the same `adm1ISO` as the parts. Returns the
    number of features without a parent (they land in `unassigned.geojson`).

    The ADM1 file's `shapeISO` is the join key, so any correction in
    scripts/shapeiso_fixes.json must already be applied to it (see
    resplit_municipal, and finalize_geojson.py for the rules).
    """
    if split_dir.exists():
        shutil.rmtree(split_dir)
    split_dir.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        joined = Path(tmp) / "joined.geojson"
        unmatched = assign_parents(combined, adm1_path, joined)
        shutil.copyfile(joined, combined)

        # No -filter here. Features whose parent could not be determined land
        # in an `unassigned` part rather than being discarded — silently losing
        # municipalities because an upstream ADM1 layer is incomplete would be
        # much worse than an oddly named file.
        run_mapshaper(
            [
                str(joined),
                "-split",
                "adm1ISO",
                "-o",
                "precision=0.000001",
                "bbox",
                "format=geojson",
                str(split_dir),
            ]
        )
        for f in list(split_dir.glob("*.json")):
            f.rename(split_dir / f"{f.stem}.geojson")

    total = feature_count(combined)
    placed = sum(feature_count(f) for f in split_dir.glob("*.geojson"))
    if placed != total:
        raise SystemExit(f"{iso3} {level}: split holds {placed} of {total} features")
    oversized = [f for f in split_dir.glob("*.geojson") if f.stat().st_size > SIZE_BUDGET]
    if oversized:
        raise RuntimeError(
            f"{oversized[0].name} is "
            f"{oversized[0].stat().st_size / 1024 / 1024:.1f} MB, over the "
            f"{SIZE_BUDGET / 1024 / 1024:.0f} MB per-file ceiling"
        )

    parts = len(list(split_dir.glob("*.geojson")))
    if unmatched:
        print(
            f"      {unmatched} of {total} features have no ADM1 parent "
            f"upstream — kept in {level}/unassigned.geojson"
        )
    print(f"      split into {parts} files")
    return unmatched


def apply_shapeiso_fixes(path: Path, iso3: str, level: str) -> int:
    """Apply scripts/shapeiso_fixes.json to one committed file in place.

    Used before a join that keys on ADM1's `shapeISO`; the full contract
    (ids, hierarchy, canonical layout) is applied afterwards by
    finalize_geojson.py.
    """
    from finalize_geojson import apply_fixes  # local: finalize imports this module

    fixes = json.loads((REPO / "scripts" / "shapeiso_fixes.json").read_text("utf-8"))
    level_fixes = fixes.get(iso3, {}).get(level, {})
    data = json.loads(path.read_text("utf-8"))
    changed = 0
    for f in data.get("features", []):
        before = f["properties"].get("shapeISO")
        apply_fixes(f["properties"], level_fixes)
        changed += f["properties"].get("shapeISO") != before
    if changed:
        path.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), "utf-8")
    return changed


def resplit_municipal(iso3: str, entry: dict) -> None:
    """Re-derive parents and parts from the committed files, without sources.

        python scripts/build_data.py --resplit USA MEX ECU

    For when the ADM1 keys change (a shapeISO correction, or a duplicate code
    resolved) and the municipal parts must follow, but a full rebuild from
    .cache/sources is not wanted: upstream may have moved on, and every
    checksum would churn.
    """
    level = entry.get("municipal_level")
    out_dir = DATA / iso3
    combined = out_dir / f"{iso3}_{level}.geojson"
    adm1 = out_dir / f"{iso3}_ADM1.geojson"
    if not level or level == "ADM1":
        raise SystemExit(f"{iso3}: no municipal level to re-split")
    if not combined.exists():
        raise SystemExit(f"{iso3}: {combined.name} is not published; nothing to re-split from")
    if not adm1.exists():
        raise SystemExit(f"{iso3}: no ADM1 to split by")

    print(f"\n{iso3} — re-splitting {level} by ADM1")
    fixed = apply_shapeiso_fixes(adm1, iso3, "ADM1")
    if fixed:
        print(f"      {fixed} ADM1 shapeISO value(s) corrected")
    unmatched = split_by_adm1(iso3, level, combined, adm1, out_dir / level)

    # Keep the manifest's `unassigned` honest; build_manifest.py carries it
    # forward from here.
    mpath = out_dir / "manifest.json"
    if mpath.exists():
        manifest = json.loads(mpath.read_text("utf-8"))
        for ds in manifest.get("datasets", []):
            if ds.get("level") == level:
                ds.pop("unassigned", None)
                if unmatched:
                    ds["unassigned"] = unmatched
        mpath.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print("      now run: python scripts/finalize_geojson.py data/earth/" + iso3)


def build_geoboundaries(iso3: str, entry: dict) -> list[dict]:
    out_dir = DATA / iso3
    out_dir.mkdir(parents=True, exist_ok=True)
    results = []

    print("  ADM1")
    adm1_result, adm1_path = build_gb_adm1(iso3, out_dir)
    if adm1_result:
        results.append(adm1_result)
        # The municipal split joins on ADM1's shapeISO, so documented upstream
        # errors (a duplicated or mistyped code) must be corrected before it.
        assert adm1_path is not None
        fixed = apply_shapeiso_fixes(adm1_path, iso3, "ADM1")
        if fixed:
            print(f"      {fixed} shapeISO value(s) corrected from shapeiso_fixes.json")
    else:
        print("      not available under a permissive licence")

    level = entry.get("municipal_level")
    if level and level != "ADM1":
        print(f"  {level} (municipal)")
        muni = build_gb_municipal(iso3, entry, out_dir, adm1_path)
        if muni:
            results.append(muni)
        else:
            print("      not available under a permissive licence")

    return results


# build_chile takes no arguments (one country, hard-wired sources); main()
# special-cases it. Every other builder is called as builder(iso3, entry).
BUILDERS: dict[str, Callable[..., list[dict]]] = {
    "ide-chile": build_chile,
    "geoboundaries": build_geoboundaries,
}


CONTINENTS = {
    "americas": {
        "Northern America",
        "Central America",
        "Caribbean",
        "South America",
    }
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
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
    args = ap.parse_args()

    if args.continent:
        regions = CONTINENTS[args.continent]
        targets = sorted(k for k, v in COUNTRIES.items() if v.get("m49_region") in regions)
    elif args.iso3:
        targets = [c.upper() for c in args.iso3]
    else:
        ap.error("pass ISO 3166-1 alpha-3 codes or --continent")

    built, skipped, failed = [], [], []
    retrieved = dt.date.today().isoformat()

    if args.resplit:
        for iso3 in targets:
            entry = COUNTRIES.get(iso3)
            if not entry:
                raise SystemExit(f"{iso3}: not in scripts/countries.json")
            resplit_municipal(iso3, entry)
        return 0

    for iso3 in targets:
        entry = COUNTRIES.get(iso3)
        if not entry:
            raise SystemExit(f"{iso3}: not in scripts/countries.json")

        if args.skip_existing and (DATA / iso3).exists():
            skipped.append(iso3)
            continue

        print(f"\n{iso3} — {entry['name']['en']} ({entry.get('source')})")
        try:
            results = []
            adm0 = build_adm0(iso3, entry)
            if adm0:
                results.append(adm0)

            builder = BUILDERS.get(entry.get("source"))
            if builder is build_chile:
                results += build_chile()
            elif builder:
                results += builder(iso3, entry)

            if results:
                built.append(iso3)
                _record_simplification(iso3, results, retrieved)
                # Ids, hierarchy, shapeISO corrections, bbox, canonical layout.
                from finalize_geojson import Country  # local: it imports this module

                country = Country(DATA / iso3)
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
    print(
        "\nNow run: node scripts/make_previews.mjs"
        " && python scripts/build_manifest.py data/earth/*/"
        " && python scripts/build_index.py"
    )
    # A non-zero exit is what lets a shell loop or CI notice the failures.
    return 1 if failed else 0


_GB_CATALOGUE: dict[tuple[str, str], dict] | None = None


def gb_metadata(iso3: str, level: str) -> dict:
    """Upstream licence and vintage for one geoBoundaries dataset.

    Licences differ *per level*, not per country — Argentina's ADM1 is
    CC BY 2.5 while its ADM2 is CC BY 3.0 IGO — so this has to be recorded on
    the dataset, not on the manifest as a whole.
    """
    global _GB_CATALOGUE
    if _GB_CATALOGUE is None:
        cat = CACHE / "geoboundaries-all.json"
        _GB_CATALOGUE = {}
        if cat.exists():
            for rec in json.loads(cat.read_text("utf-8")):
                _GB_CATALOGUE[(rec.get("boundaryISO"), rec.get("boundaryType"))] = rec
    return _GB_CATALOGUE.get((iso3, level), {})


SOURCE_INFO = {
    "geoboundaries": {
        "name": "geoBoundaries (gbOpen)",
        "url": "https://www.geoboundaries.org/",
    },
    "natural-earth": {
        "name": "Natural Earth 10m Admin 0",
        "url": "https://www.naturalearthdata.com/",
        "license": "public-domain",
    },
    "ide-chile": {
        "name": "IDE Chile / SUBDERE — División Política Administrativa 2023",
        "url": "https://www.geoportal.cl/",
        "license": "CC-BY-4.0",
    },
}


def _record_simplification(iso3: str, results: list[dict], retrieved: str) -> None:
    """Write identity, per-dataset provenance and the applied tolerance.

    build_manifest.py preserves everything outside `datasets`, and carries
    forward the per-dataset keys it does not compute itself.
    """
    entry = COUNTRIES[iso3]
    mpath = DATA / iso3 / "manifest.json"
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


if __name__ == "__main__":
    raise SystemExit(main())
