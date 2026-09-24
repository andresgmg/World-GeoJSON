from __future__ import annotations

import json
from pathlib import Path

import validate_data


def test_all_committed_manifests_validate(abw: Path) -> None:
    v = validate_data.validator("manifest.schema.json")
    bad = {}
    for m in sorted(validate_data.DATA.glob("*/*/manifest.json")):
        errors = list(v.iter_errors(json.loads(m.read_text("utf-8"))))
        if errors:
            bad[m.parent.name] = validate_data._describe(errors[0])
    assert bad == {}


def test_registry_validates() -> None:
    doc = json.loads((validate_data.REPO / "scripts" / "countries.json").read_text("utf-8"))
    errors = list(validate_data.validator("countries.schema.json").iter_errors(doc))
    assert errors == [], [validate_data._describe(e) for e in errors[:5]]


def test_feature_schema_accepts_committed_features(brb: Path) -> None:
    v = validate_data.validator("feature.schema.json")
    data = json.loads((brb / "BRB_ADM1.geojson").read_text("utf-8"))
    for f in data["features"]:
        assert next(v.iter_errors(f), None) is None, f["id"]


def test_feature_schema_rejects_bad_features() -> None:
    v = validate_data.validator("feature.schema.json")
    good = {
        "type": "Feature",
        "id": "ABW:ADM0:ABW",
        "properties": {
            "shapeName": "Aruba",
            "shapeISO": "ABW",
            "shapeGroup": "ABW",
            "shapeType": "ADM0",
        },
        "geometry": {"type": "Polygon", "coordinates": []},
    }
    assert next(v.iter_errors(good), None) is None
    for mutate in (
        lambda f: f.pop("id"),
        lambda f: f.__setitem__("id", "aruba"),
        lambda f: f["properties"].__setitem__("shapeType", "ADM9"),
        lambda f: f["properties"].__setitem__("shapeID", "x"),  # not part of the contract
        lambda f: f["properties"].__setitem__("parentID", "not-an-id"),
    ):
        f = json.loads(json.dumps(good))
        mutate(f)
        assert next(v.iter_errors(f), None) is not None


def test_allow_list_comes_from_the_schema() -> None:
    assert "CC-BY-4.0" in validate_data.ALLOWED_LICENSES
    assert "ODbL-1.0" not in validate_data.ALLOWED_LICENSES
