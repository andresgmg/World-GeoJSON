from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

import finalize_geojson as fz

ID_RE = re.compile(r"^[A-Z]{3}:(ADM[0-4]|QUAD):\S+$")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (-70, "-70"),
        (12.4, "12.4"),
        (12.577582, "12.577582"),
        (0.000001, "0.000001"),
        (0.00001, "0.00001"),  # json.dumps would write 1e-05
        (-0.0000001, "0"),
        (0.0, "0"),
    ],
)
def test_fmt_number(value: float, expected: str) -> None:
    assert fz.fmt_number(value) == expected


def test_apply_fixes() -> None:
    p = {"shapeISO": "52423323B51867153498623", "src_shape_id": "52423323B51867153498623"}
    fz.apply_fixes(p, {})
    assert p["shapeISO"] == "", "an opaque upstream id is not a code"

    p = {"shapeISO": "SU-SD", "src_shape_id": "X1"}
    fz.apply_fixes(p, {"X1": "US-SD"})
    assert p["shapeISO"] == "US-SD"

    p = {"shapeISO": "BZ-BZ", "src_shape_id": "X2"}
    fz.apply_fixes(p, {"*": ""})
    assert p["shapeISO"] == ""


def _feat(name: str, iso: str = "", src: str | None = None) -> dict:
    props = {"shapeName": name, "shapeISO": iso, "shapeGroup": "XXX", "shapeType": "ADM2"}
    if src:
        props["src_shape_id"] = src
    return {"properties": props, "geometry": {"type": "Polygon", "coordinates": []}}


def test_assign_keys_prefers_real_unique_codes_then_names() -> None:
    feats = [
        _feat("Alpha", "XX-A", "1"),
        _feat("Beta", "XX-B", "2"),
        _feat("Gamma", "", "3"),
        _feat("Delta", "XX-D", "4"),
        _feat("Delta Two", "XX-D", "5"),  # duplicated code -> name key
    ]
    adm1_of = {"1": "XX-1", "2": "XX-1", "3": "XX-2", "4": "XX-2", "5": "XX-2"}
    keys, warnings = fz.assign_keys("XXX", "ADM2", feats, adm1_of, {})
    assert keys == {
        "1": "XX-A",
        "2": "XX-B",
        "3": "XX-2.gamma",
        "4": "XX-2.delta",
        "5": "XX-2.delta-two",
    }
    assert any("not unique" in w for w in warnings)


def test_assign_keys_disambiguates_name_collisions_deterministically() -> None:
    feats = [_feat("Toledo", "", "b"), _feat("Toledo", "", "a"), _feat("Toledo", "", "c")]
    keys, warnings = fz.assign_keys("COL", "ADM2", feats, None, {})
    assert keys == {"a": "toledo", "b": "toledo-2", "c": "toledo-3"}
    assert any("share the key" in w for w in warnings)


def test_assign_keys_honours_overrides_and_rejects_collisions() -> None:
    feats = [_feat("One", "", "1"), _feat("Two", "", "2")]
    keys, _ = fz.assign_keys("XXX", "ADM1", feats, None, {"2": "custom"})
    assert keys["2"] == "custom"
    with pytest.raises(SystemExit, match="collide"):
        fz.assign_keys("XXX", "ADM1", feats, None, {"2": "one"})


def _ids_and_parents(d: Path) -> tuple[dict[str, set[str]], list[tuple[str, str]]]:
    ids: dict[str, set[str]] = {}
    parents: list[tuple[str, str]] = []
    for p in d.rglob("*.geojson"):
        if "preview" in p.parts:
            continue
        for f in json.loads(p.read_text("utf-8"))["features"]:
            level = f["id"].split(":")[1]
            ids.setdefault(level, set()).add(f["id"])
            if "parentID" in f["properties"]:
                parents.append((f["id"], f["properties"]["parentID"]))
    return ids, parents


@pytest.mark.parametrize("code", ["ABW", "BRB", "DOM"])
def test_finalize_is_idempotent_and_consistent(code: str, tmp_path: Path) -> None:
    src = fz.DATA / "earth" / code
    if not (src / "manifest.json").exists():
        pytest.skip(f"{code} not checked out")
    d = tmp_path / code
    shutil.copytree(src, d)

    c = fz.Country(d)
    c.finalize()
    c.write()

    again = fz.Country(d)
    again.finalize()
    assert again.stale() == [], "a second run must change nothing"

    ids, parents = _ids_and_parents(d)
    for level, level_ids in ids.items():
        assert all(ID_RE.match(i) for i in level_ids), level
    for child, parent in parents:
        assert parent in ids[parent.split(":")[1]], (child, parent)

    for p in d.rglob("*.geojson"):
        if "preview" in p.parts:
            continue
        data = json.loads(p.read_text("utf-8"))
        assert data["bbox"] == fz.bbox_of(data["features"]), p.name
        assert p.read_bytes() == fz.serialise(data["features"]), "not canonical"


def test_split_level_hierarchy(dom: Path, tmp_path: Path) -> None:
    d = tmp_path / "DOM"
    shutil.copytree(dom, d)
    c = fz.Country(d)
    c.finalize()
    c.write()

    combined = json.loads((d / "DOM_ADM2.geojson").read_text("utf-8"))["features"]
    by_id = {f["id"]: f for f in combined}
    for part in (d / "ADM2").glob("*.geojson"):
        for f in json.loads(part.read_text("utf-8"))["features"]:
            assert f["properties"]["adm1ISO"] == part.stem
            assert by_id[f["id"]]["properties"] == f["properties"], "combined must match its part"
            if part.stem != "unassigned":
                assert f["properties"]["parentISO"] == part.stem
                assert f["properties"]["parentID"] == f"DOM:ADM1:{part.stem}"
    adm1 = json.loads((d / "DOM_ADM1.geojson").read_text("utf-8"))["features"]
    for f in adm1:
        assert "adm1ISO" not in f["properties"]
        assert f["properties"]["parentID"] == "DOM:ADM0:DOM"


def test_check_mode_reports_stale_files(abw: Path, tmp_path: Path) -> None:
    d = tmp_path / "ABW"
    shutil.copytree(abw, d)
    path = d / "ABW_ADM0.geojson"
    data = json.loads(path.read_text("utf-8"))
    path.write_text(json.dumps(data, indent=2), "utf-8")  # valid but not canonical
    assert fz.main(["--check", str(d)]) == 1
    assert fz.main([str(d)]) == 0
    assert fz.main(["--check", str(d)]) == 0
