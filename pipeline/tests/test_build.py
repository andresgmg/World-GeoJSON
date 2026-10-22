from __future__ import annotations

from pathlib import Path

import pytest

from wgj import build


def _failing_adm0(root: Path):  # type: ignore[no-untyped-def]
    def adm0(iso3: str, entry: dict) -> dict:
        out = root / iso3
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{iso3}_ADM0.geojson").write_text("{}", "utf-8")
        raise RuntimeError("mapshaper: boom")

    return adm0


def test_failed_first_build_leaves_no_directory(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Otherwise the next --skip-existing run takes the half-built country for done."""
    monkeypatch.setattr(build, "earth", lambda: tmp_path)
    monkeypatch.setattr(build, "build_adm0", _failing_adm0(tmp_path))
    assert build.main(["ABW"]) == 1
    assert not (tmp_path / "ABW").exists()


def test_failed_rebuild_keeps_the_existing_directory(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    (tmp_path / "ABW").mkdir()
    (tmp_path / "ABW" / "manifest.json").write_text("{}", "utf-8")
    monkeypatch.setattr(build, "earth", lambda: tmp_path)
    monkeypatch.setattr(build, "build_adm0", _failing_adm0(tmp_path))
    assert build.main(["ABW"]) == 1
    assert (tmp_path / "ABW" / "manifest.json").exists()


def test_aborted_first_build_leaves_no_directory(tmp_path: Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """finalize raises SystemExit on an id collision; the directory still goes."""

    def adm0(iso3: str, entry: dict) -> dict:
        (tmp_path / iso3).mkdir(parents=True)
        raise SystemExit("ABW ADM0: feature keys collide")

    monkeypatch.setattr(build, "earth", lambda: tmp_path)
    monkeypatch.setattr(build, "build_adm0", adm0)
    with pytest.raises(SystemExit, match="collide"):
        build.main(["ABW"])
    assert not (tmp_path / "ABW").exists()
