from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import pytest

from wgj import finalize as fz
from wgj.geojson_io import bbox_of, serialise

ID_RE = re.compile(r"^[A-Z]{3}:(ADM[0-4]|QUAD):\S+$")


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
            ids.setdefault(f["id"].split(":")[1], set()).add(f["id"])
            if "parentID" in f["properties"]:
                parents.append((f["id"], f["properties"]["parentID"]))
    return ids, parents


@pytest.mark.parametrize("code", ["ABW", "BRB", "DOM"])
def test_finalize_is_idempotent_and_consistent(code: str, data_copy: Path) -> None:
    d = data_copy / "earth" / code
    c = fz.Country(d)
    c.finalize()
    assert c.stale() == [], "committed fixtures must already be finalized"

    ids, parents = _ids_and_parents(d)
    for level, level_ids in ids.items():
        assert all(ID_RE.match(i) for i in level_ids), level
    for child, parent in parents:
        assert parent in ids[parent.split(":")[1]], (child, parent)
    for p in d.rglob("*.geojson"):
        if "preview" in p.parts:
            continue
        data = json.loads(p.read_text("utf-8"))
        assert data["bbox"] == bbox_of(data["features"]), p.name
        assert p.read_bytes() == serialise(data["features"]), "not canonical"


def test_split_level_hierarchy(dom: Path) -> None:
    adm1 = {f["id"] for f in json.loads((dom / "DOM_ADM1.geojson").read_text("utf-8"))["features"]}
    for part in (dom / "ADM2").glob("*.geojson"):
        for f in json.loads(part.read_text("utf-8"))["features"]:
            p = f["properties"]
            assert p["adm1ISO"] == part.stem
            assert p["parentISO"] == part.stem
            assert p["parentID"] == f"DOM:ADM1:{part.stem}" and p["parentID"] in adm1
            assert p["shapeISO"] == "", "geoBoundaries municipal codes are opaque -> cleared"
            assert list(p)[:7] == [
                "shapeName",
                "shapeISO",
                "shapeGroup",
                "shapeType",
                "adm1ISO",
                "parentISO",
                "parentID",
            ]
    for f in json.loads((dom / "DOM_ADM1.geojson").read_text("utf-8"))["features"]:
        assert "adm1ISO" not in f["properties"]
        assert f["properties"]["parentID"] == "DOM:ADM0:DOM"


def test_check_mode_reports_stale_files(data_copy: Path) -> None:
    d = data_copy / "earth" / "ABW"
    path = d / "ABW_ADM0.geojson"
    path.write_text(json.dumps(json.loads(path.read_text("utf-8")), indent=2), "utf-8")
    assert fz.main(["--check", str(d)]) == 1
    assert fz.main([str(d)]) == 0
    assert fz.main(["--check", str(d)]) == 0


def test_shapeiso_correction_flows_into_ids_and_parts(data_copy: Path) -> None:
    """A corrected ADM1 code becomes the key, and the id of the unit."""
    d = data_copy / "earth" / "BRB"
    fixes = {"BRB": {"ADM1": {"*": ""}}}  # pretend Barbados' codes were opaque
    c = fz.Country(d)
    c.fixes = fixes["BRB"]
    c.finalize()
    c.write()
    ids = [f["id"] for f in json.loads((d / "BRB_ADM1.geojson").read_text("utf-8"))["features"]]
    assert all(":" in i and i.split(":")[2] == i.split(":")[2].lower() for i in ids), ids
    shutil.rmtree(d)
