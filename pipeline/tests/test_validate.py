from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from wgj import validate


def test_fixtures_are_clean(fixtures: Path) -> None:
    report = validate.validate(validate.discover(fixtures), checksums=True)
    assert report.errors == []
    assert report.checked == 3
    assert any("DOM ADM2: no preview" in w for w in report.warnings)


def test_real_data_is_clean(real_data: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WGJ_DATA", str(real_data))
    report = validate.validate([real_data / "earth" / "CHL"])
    assert report.errors == []


def test_reports_do_not_share_state(abw: Path) -> None:
    first, second = validate.validate([abw]), validate.validate([abw])
    assert first is not second and first.warnings == second.warnings


def test_copyleft_licence_is_an_error(data_copy: Path) -> None:
    mpath = data_copy / "earth" / "ABW" / "manifest.json"
    m = json.loads(mpath.read_text("utf-8"))
    m["datasets"][0]["license"] = "ODbL-1.0"
    mpath.write_text(json.dumps(m), "utf-8")
    report = validate.validate([mpath.parent])
    assert any("ODbL-1.0" in e and "is not one of" in e for e in report.errors)


def test_required_properties_checked_on_every_feature(data_copy: Path) -> None:
    path = data_copy / "earth" / "BRB" / "BRB_ADM1.geojson"
    data = json.loads(path.read_text("utf-8"))
    del data["features"][-1]["properties"]["shapeISO"]  # the LAST feature
    path.write_text(json.dumps(data), "utf-8")
    report = validate.validate([path.parent])
    assert any("'shapeISO' is a required property" in e for e in report.errors)


def test_dangling_parent_and_bad_bbox_are_errors(data_copy: Path) -> None:
    path = data_copy / "earth" / "DOM" / "ADM2" / "DO-01.geojson"
    data = json.loads(path.read_text("utf-8"))
    data["features"][0]["properties"]["parentID"] = "DOM:ADM1:DO-99"
    data["bbox"] = [0, 0, 1, 1]
    path.write_text(json.dumps(data), "utf-8")
    report = validate.validate([path.parents[1]])
    assert any("parentID targets do not exist" in e for e in report.errors)
    assert any("bbox" in e and "does not match" in e for e in report.errors)


def test_checksums_catch_a_modified_file(data_copy: Path) -> None:
    path = data_copy / "earth" / "ABW" / "ABW_ADM0.geojson"
    path.write_bytes(path.read_bytes().replace(b"Aruba", b"Arubb"))
    report = validate.validate([path.parent], checksums=True)
    assert any("sha256 does not match" in e for e in report.errors)


def test_broken_manifest_is_reported_not_raised(data_copy: Path) -> None:
    d = data_copy / "earth" / "ABW"
    (d / "manifest.json").write_text("{not json", "utf-8")
    report = validate.validate([d])
    assert any("not valid JSON" in e for e in report.errors)


def test_help_does_not_run_the_validation() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "wgj", "validate", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "usage:" in proc.stdout and "checked" not in proc.stdout
