"""Finalize committed GeoJSON: stable ids, hierarchy, shapeISO fixes, bbox.

    python scripts/finalize_geojson.py data/earth/CHL
    python scripts/finalize_geojson.py data/earth/*/
    python scripts/finalize_geojson.py --check data/earth/*/   # CI: exit 1 if stale

This is the last step of the pipeline before previews and manifests, and it
is pure Python: no mapshaper, no network. It reads the country's full-
resolution files (combined level files and split parts), and rewrites them so
that every feature carries the data contract documented in
docs/reference/properties.md:

- `id`            Feature-level, `{ISO3}:{LEVEL}:{key}`. The key is the real,
                  unique `shapeISO` when there is one; otherwise a name-based
                  key (`{adm1ISO}.{slug}` below the first level, `{slug}` at
                  it). Manual keys live in scripts/id_overrides.json.
- `shapeISO`      Upstream errors corrected from scripts/shapeiso_fixes.json;
                  an opaque geoBoundaries id (equal to `src_shape_id`) is
                  cleared to "" rather than passed off as a code.
- `adm1ISO`       On every feature below ADM1 when the country publishes an
                  ADM1 (taken from the split parts, whose file name is the
                  parent's key).
- `parentISO`     The parent's key at the previous published level.
- `parentID`      The parent's feature id. Omitted for `unassigned` features
                  and where no parent level is published.
- `bbox`          Recomputed from the coordinates (mapshaper wrote the
                  pre-simplification extent in a few files).

Output is canonical — one feature per line, compact separators, coordinates
formatted with at most six decimals — so running this twice is a no-op and CI
can check that committed data is finalized (`--check`).

Previews are NOT touched here: make_previews.mjs regenerates them from the
finalized files and mapshaper carries the feature id through.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_data import COUNTRIES, slug

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"
SCRIPTS = REPO / "scripts"

LEVELS = ["ADM0", "ADM1", "ADM2", "ADM3", "ADM4"]
STANDARD = ("shapeName", "shapeISO", "shapeGroup", "shapeType")
HIERARCHY = ("adm1ISO", "parentISO", "parentID")
UNASSIGNED = "unassigned"


def _registry(name: str) -> dict:
    data = json.loads((SCRIPTS / name).read_text("utf-8"))
    return {k: v for k, v in data.items() if not k.startswith("$")}


# ---------------------------------------------------------------------------
# canonical serialisation
# ---------------------------------------------------------------------------


def fmt_number(v: float | int) -> str:
    """Coordinates: at most six decimals, no exponent, no trailing zeros."""
    if isinstance(v, bool):  # pragma: no cover - never a coordinate
        raise TypeError("bool is not a coordinate")
    if isinstance(v, int):
        return str(v)
    s = f"{v:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def fmt_coords(c: object) -> str:
    if isinstance(c, list):
        return "[" + ",".join(fmt_coords(x) for x in c) + "]"
    if isinstance(c, (int, float)):
        return fmt_number(c)
    raise TypeError(f"unexpected value in coordinates: {c!r}")


def fmt_geometry(g: dict) -> str:
    return (
        "{" + f'"type":{json.dumps(g["type"])},"coordinates":{fmt_coords(g["coordinates"])}' + "}"
    )


def fmt_feature(f: dict) -> str:
    props = json.dumps(f["properties"], ensure_ascii=False, separators=(",", ":"))
    fid = json.dumps(f["id"], ensure_ascii=False)
    return (
        '{"type":"Feature","id":'
        + fid
        + ',"properties":'
        + props
        + ',"geometry":'
        + fmt_geometry(f["geometry"])
        + "}"
    )


def bbox_of(features: Iterable[dict]) -> list[float]:
    minx = miny = float("inf")
    maxx = maxy = float("-inf")

    def walk(c: object) -> None:
        nonlocal minx, miny, maxx, maxy
        if isinstance(c, list) and c and isinstance(c[0], (int, float)):
            x, y = float(c[0]), float(c[1])
            minx, maxx = min(minx, x), max(maxx, x)
            miny, maxy = min(miny, y), max(maxy, y)
        elif isinstance(c, list):
            for item in c:
                walk(item)

    for f in features:
        walk(f["geometry"]["coordinates"])
    return [round(v, 6) for v in (minx, miny, maxx, maxy)]


def serialise(features: list[dict]) -> bytes:
    bbox = "[" + ",".join(fmt_number(v) for v in bbox_of(features)) + "]"
    body = ",\n".join(fmt_feature(f) for f in features)
    return (
        '{"type":"FeatureCollection","bbox":' + bbox + ',"features":[\n' + body + "\n]}"
    ).encode("utf-8")


def load(path: Path) -> list[dict]:
    data = json.loads(path.read_text("utf-8"))
    if data.get("type") != "FeatureCollection":
        raise SystemExit(f"{path}: not a FeatureCollection")
    return list(data.get("features") or [])


# ---------------------------------------------------------------------------
# keys and hierarchy
# ---------------------------------------------------------------------------


def ident(props: dict) -> str:
    """What identifies a feature across the combined file and its part."""
    return props.get("src_shape_id") or props.get("shapeISO") or props["shapeName"]


def apply_fixes(props: dict, fixes: dict[str, str]) -> None:
    if "*" in fixes:
        props["shapeISO"] = fixes["*"]
    src = props.get("src_shape_id")
    if src and src in fixes:
        props["shapeISO"] = fixes[src]
    # An opaque upstream id is not a code. Leave the slot honestly empty.
    if props.get("shapeISO") and props["shapeISO"] == props.get("src_shape_id"):
        props["shapeISO"] = ""


def real_code(props: dict) -> str | None:
    code = props.get("shapeISO") or ""
    if not code or code == props.get("src_shape_id"):
        return None
    return code


def assign_keys(
    iso3: str,
    level: str,
    feats: list[dict],
    adm1_of: dict[str, str] | None,
    overrides: dict[str, str],
) -> tuple[dict[str, str], list[str]]:
    """ident -> key for one level. Returns (keys, warnings)."""
    warnings: list[str] = []
    codes = Counter(c for c in (real_code(f["properties"]) for f in feats) if c)
    keys: dict[str, str] = {}
    slug_owners: dict[str, list[str]] = {}

    for f in feats:
        p = f["properties"]
        i = ident(p)
        if i in overrides:
            key = overrides[i]
        elif level == "ADM0":
            key = p["shapeGroup"]
        else:
            code = real_code(p)
            if code and codes[code] == 1:
                key = code
            else:
                base = slug(p["shapeName"])
                if adm1_of is not None:
                    base = f"{adm1_of.get(i, UNASSIGNED)}.{base}"
                key = base
                slug_owners.setdefault(base, []).append(i)
                if code:
                    warnings.append(
                        f"{iso3} {level}: shapeISO '{code}' is not unique; "
                        f"'{p['shapeName']}' keyed as '{key}'"
                    )
        keys[i] = key

    # Name-based keys can collide (Colombia has three Albanias). Disambiguate
    # deterministically by upstream id; the suffixes are stable for a given
    # upstream vintage and are reported so they can be pinned in
    # id_overrides.json if a better key exists.
    for base, owners in slug_owners.items():
        if len(owners) < 2:
            continue
        for n, i in enumerate(sorted(owners), start=1):
            if n > 1:
                keys[i] = f"{base}-{n}"
        warnings.append(f"{iso3} {level}: {len(owners)} features share the key '{base}'")

    dupes = {k for k, c in Counter(keys.values()).items() if c > 1}
    if dupes:
        detail = "; ".join(
            f"'{k}': " + ", ".join(sorted(i for i, kk in keys.items() if kk == k)) for k in dupes
        )
        raise SystemExit(
            f"{iso3} {level}: feature keys collide ({detail}). "
            f"Resolve in scripts/id_overrides.json."
        )
    return keys, warnings


def rebuild_props(
    p: dict,
    *,
    adm1: str | None,
    parent_iso: str | None,
    parent_id: str | None,
) -> dict:
    out = {k: p[k] for k in STANDARD}
    if adm1 is not None:
        out["adm1ISO"] = adm1
    if parent_iso is not None:
        out["parentISO"] = parent_iso
    if parent_id is not None:
        out["parentID"] = parent_id
    for k, v in p.items():
        if k not in STANDARD and k not in HIERARCHY:
            out[k] = v
    return out


# ---------------------------------------------------------------------------
# per-country driver
# ---------------------------------------------------------------------------


class Country:
    def __init__(self, d: Path) -> None:
        self.dir = d
        self.iso3 = d.name
        self.fixes = _registry("shapeiso_fixes.json").get(self.iso3, {})
        self.overrides = _registry("id_overrides.json").get(self.iso3, {})
        self.warnings: list[str] = []
        self.outputs: dict[Path, bytes] = {}

    def levels(self) -> list[str]:
        present = []
        for lvl in LEVELS:
            if (self.dir / f"{self.iso3}_{lvl}.geojson").exists() or any(
                (self.dir / lvl).glob("*.geojson")
            ):
                present.append(lvl)
        return present

    def finalize(self) -> None:
        present = self.levels()
        keys_by_level: dict[str, set[str]] = {}
        for n, level in enumerate(present):
            parent_level = present[n - 1] if n else None
            keys_by_level[level] = self._finalize_level(
                level, parent_level, "ADM1" in present, keys_by_level
            )

    def _load_level(self, level: str) -> tuple[Path, list[dict] | None, dict[Path, list[dict]]]:
        combined_path = self.dir / f"{self.iso3}_{level}.geojson"
        combined = load(combined_path) if combined_path.exists() else None
        parts = {
            p: load(p) for p in sorted((self.dir / level).glob("*.geojson"), key=lambda p: p.name)
        }
        return combined_path, combined, parts

    def _finalize_level(
        self,
        level: str,
        parent_level: str | None,
        has_adm1: bool,
        keys_by_level: dict[str, set[str]],
    ) -> set[str]:
        """Rewrite one level's files; return the set of keys it defines."""
        combined_path, combined, parts = self._load_level(level)

        # Fixes first, on every copy, so idents and codes agree.
        level_fixes = self.fixes.get(level, {})
        for f in [*(combined or []), *(f for fs in parts.values() for f in fs)]:
            apply_fixes(f["properties"], level_fixes)

        # Which ADM1 does each feature belong to? The split part's file name
        # is the parent's key; the combined file may lack the field.
        adm1_of: dict[str, str] | None = None
        if has_adm1 and level not in ("ADM0", "ADM1"):
            adm1_of = {}
            for p, fs in parts.items():
                for f in fs:
                    adm1_of[ident(f["properties"])] = p.stem
            if not parts:
                # Not split (nothing to split by upstream, or a level above
                # the municipal tier): fall back to what the file carries.
                for f in combined or []:
                    pr = f["properties"]
                    code = pr.get("adm1ISO") or (
                        pr.get("parentISO") if parent_level == "ADM1" else None
                    )
                    if code:
                        adm1_of[ident(pr)] = code

        all_parts = [f for fs in parts.values() for f in fs]
        canonical = combined if combined is not None else all_parts
        if combined is not None and parts:
            in_combined = {ident(f["properties"]) for f in combined}
            in_parts = [ident(f["properties"]) for fs in parts.values() for f in fs]
            missing = set(in_parts) - in_combined
            if missing or len(in_parts) != len(in_combined):
                raise SystemExit(
                    f"{self.iso3} {level}: combined file and parts disagree "
                    f"({len(in_combined)} vs {len(in_parts)} features; "
                    f"{len(missing)} only in parts)"
                )

        keys, warns = assign_keys(
            self.iso3, level, canonical, adm1_of, self.overrides.get(level, {})
        )
        self.warnings.extend(warns)

        def hierarchy(p: dict) -> tuple[str | None, str | None, str | None]:
            """(adm1ISO, parentISO, parentID) for one feature."""
            if level == "ADM0":
                return None, None, None
            i = ident(p)
            adm1 = adm1_of.get(i) if adm1_of is not None else None
            if parent_level is None:
                return adm1, None, None
            if parent_level == "ADM0":
                parent_key: str | None = self.iso3
            elif parent_level == "ADM1":
                parent_key = adm1
            else:
                # Chile ADM3 -> ADM2: the province code already on the feature.
                parent_key = p.get("parentISO")
            if not parent_key or parent_key == UNASSIGNED:
                return adm1, None, None
            if parent_key not in keys_by_level[parent_level]:
                raise SystemExit(
                    f"{self.iso3} {level}: '{p['shapeName']}' points at parent "
                    f"'{parent_key}' which is not a {parent_level} key. "
                    f"Re-split the level (build_data.py --resplit {self.iso3})."
                )
            return adm1, parent_key, f"{self.iso3}:{parent_level}:{parent_key}"

        def finalize_features(feats: list[dict]) -> list[dict]:
            out = []
            for f in feats:
                p = f["properties"]
                adm1, parent_iso, parent_id = hierarchy(p)
                out.append(
                    {
                        "id": f"{self.iso3}:{level}:{keys[ident(p)]}",
                        "properties": rebuild_props(
                            p, adm1=adm1, parent_iso=parent_iso, parent_id=parent_id
                        ),
                        "geometry": f["geometry"],
                    }
                )
            return out

        if combined is not None:
            self.outputs[combined_path] = serialise(finalize_features(combined))
        for p, fs in parts.items():
            self.outputs[p] = serialise(finalize_features(fs))
        return set(keys.values())

    def stale(self) -> list[Path]:
        return [p for p, b in self.outputs.items() if p.read_bytes() != b]

    def write(self) -> int:
        changed = 0
        for p in self.stale():
            p.write_bytes(self.outputs[p])
            changed += 1
        return changed


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("dirs", nargs="+", type=Path, help="country directories")
    ap.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 if any file is not already finalized",
    )
    args = ap.parse_args(argv)

    stale_total = 0
    for raw in args.dirs:
        d = raw.resolve()
        if not d.is_dir():
            ap.error(f"{raw}: not a directory")
        if d.name not in COUNTRIES and not (d / "manifest.json").exists():
            ap.error(f"{raw}: not a country directory")

        c = Country(d)
        c.finalize()
        for w in c.warnings:
            print(f"  ! {w}")
        stale = c.stale()
        if args.check:
            for p in stale:
                shown = p.relative_to(REPO).as_posix() if p.is_relative_to(REPO) else p.as_posix()
                print(f"::error::{shown} is not finalized")
            stale_total += len(stale)
            print(f"{c.iso3}: {len(c.outputs)} file(s), {len(stale)} stale")
        else:
            n = c.write()
            print(f"{c.iso3}: {len(c.outputs)} file(s), {n} rewritten")

    if args.check and stale_total:
        print(f"\n{stale_total} file(s) need `python scripts/finalize_geojson.py`")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
