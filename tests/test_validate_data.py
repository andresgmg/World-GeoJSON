from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import validate_data


def test_committed_country_is_clean(abw: Path) -> None:
    report = validate_data.validate([abw])
    assert report.errors == []
    assert report.checked == 1


def test_reports_do_not_share_state(abw: Path) -> None:
    first = validate_data.validate([abw])
    second = validate_data.validate([abw])
    assert first is not second
    assert first.warnings == second.warnings


def _copy(src: Path, dst: Path) -> Path:
    shutil.copytree(src, dst)
    return dst


def test_copyleft_licence_is_an_error(abw: Path, tmp_path: Path) -> None:
    d = _copy(abw, tmp_path / "ABW")
    mpath = d / "manifest.json"
    manifest = json.loads(mpath.read_text("utf-8"))
    manifest["datasets"][0]["license"] = "ODbL-1.0"
    mpath.write_text(json.dumps(manifest), "utf-8")

    report = validate_data.validate([d])
    assert any("ODbL-1.0" in e and "allow-list" in e for e in report.errors)


def test_missing_preview_is_only_a_warning(abw: Path, tmp_path: Path) -> None:
    d = _copy(abw, tmp_path / "ABW")
    mpath = d / "manifest.json"
    manifest = json.loads(mpath.read_text("utf-8"))
    manifest["datasets"][0].pop("preview")
    mpath.write_text(json.dumps(manifest), "utf-8")

    report = validate_data.validate([d])
    assert report.ok
    assert any("no preview" in w for w in report.warnings)


def test_required_properties_checked_on_every_feature(brb: Path, tmp_path: Path) -> None:
    d = _copy(brb, tmp_path / "BRB")
    path = d / "BRB_ADM1.geojson"
    data = json.loads(path.read_text("utf-8"))
    assert len(data["features"]) > 1
    # Corrupt the LAST feature: the old check only looked at the first one.
    del data["features"][-1]["properties"]["shapeISO"]
    path.write_text(json.dumps(data), "utf-8")

    report = validate_data.validate([d])
    assert any("missing required properties" in e and "shapeISO" in e for e in report.errors)


def test_broken_manifest_is_reported_not_raised(abw: Path, tmp_path: Path) -> None:
    d = _copy(abw, tmp_path / "ABW")
    (d / "manifest.json").write_text("{not json", "utf-8")
    report = validate_data.validate([d])
    assert any("not valid JSON" in e for e in report.errors)


def test_help_does_not_run_the_validation(repo: Path) -> None:
    proc = subprocess.run(
        [sys.executable, str(repo / "scripts" / "validate_data.py"), "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    assert "usage:" in proc.stdout
    assert "checked" not in proc.stdout
