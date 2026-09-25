"""geoBoundaries gbOpen — first-level and municipal tiers, permissive licences only."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

from wgj.geojson_io import feature_count
from wgj.mapshaper import js_expr, run_mapshaper
from wgj.paths import CACHE, earth
from wgj.registry import shapeiso_fixes
from wgj.simplify import SIZE_BUDGET, simplify

GB_ALL_URL = "https://www.geoboundaries.org/api/current/gbOpen/ALL/ALL/"
GB_CATALOGUE_FILE = CACHE / "geoboundaries-all.json"


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
                    # An empty shapeISO stays empty. wgj.finalize derives
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
    wgj/tables/shapeiso_fixes.json must already be applied to it (see
    resplit_municipal, and wgj.finalize for the rules).
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
    """Apply the registry's shapeISO corrections to one committed file in place.

    Used before a join that keys on ADM1's `shapeISO`; the full contract
    (ids, hierarchy, canonical layout) is applied afterwards by
    wgj.finalize.
    """
    from wgj.finalize import apply_fixes

    level_fixes = shapeiso_fixes().get(iso3, {}).get(level, {})
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

        wgj build --resplit USA MEX ECU

    For when the ADM1 keys change (a shapeISO correction, or a duplicate code
    resolved) and the municipal parts must follow, but a full rebuild from
    .cache/sources is not wanted: upstream may have moved on, and every
    checksum would churn.
    """
    level = entry.get("municipal_level")
    out_dir = earth() / iso3
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

    # Keep the manifest's `unassigned` honest; `wgj manifest` carries it
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
    print("      now run: wgj finalize data/earth/" + iso3)


def build_geoboundaries(iso3: str, entry: dict) -> list[dict]:
    out_dir = earth() / iso3
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
