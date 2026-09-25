from __future__ import annotations

from pathlib import Path

import pytest

from geoworld.cache import DiskCache, default_cache_dir, is_safe_path


def test_default_cache_dir_env_override(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("GEOWORLD_CACHE", str(tmp_path / "custom"))
    assert default_cache_dir() == tmp_path / "custom"


def test_default_cache_dir_per_platform(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("GEOWORLD_CACHE", raising=False)
    monkeypatch.setattr("geoworld.cache.sys.platform", "linux")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "xdg"))
    assert default_cache_dir() == tmp_path / "xdg" / "geoworld"
    monkeypatch.delenv("XDG_CACHE_HOME")
    assert default_cache_dir() == Path.home() / ".cache" / "geoworld"
    monkeypatch.setattr("geoworld.cache.sys.platform", "darwin")
    assert default_cache_dir() == Path.home() / "Library" / "Caches" / "geoworld"
    monkeypatch.setattr("geoworld.cache.sys.platform", "win32")
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path / "local"))
    assert default_cache_dir() == tmp_path / "local" / "geoworld"


@pytest.mark.parametrize(
    ("path", "ok"),
    [
        ("data/index.json", True),
        ("data/earth/DOM/DOM_ADM1.geojson", True),
        ("data/earth/DOM/ADM2/DO-01.geojson", True),
        ("data/earth/DOM/preview/DOM_ADM1.preview.geojson", True),
        ("data/earth/DOM/../../etc/passwd", False),
        ("/etc/passwd", False),
        ("data/earth/DOM/x.txt", False),
        ("schemas/index.schema.json", False),
    ],
)
def test_safe_paths(path: str, ok: bool) -> None:
    assert is_safe_path(path) is ok


def test_disk_cache_put_get_delete_clear(tmp_path: Path) -> None:
    cache = DiskCache(tmp_path, "1.0.0")
    assert cache.get("data/index.json") is None
    cache.put("data/index.json", b"{}")
    assert cache.get("data/index.json") == b"{}"
    assert cache.path_for("data/index.json") == tmp_path / "1.0.0" / "data" / "index.json"
    assert not list((tmp_path / "1.0.0" / "data").glob(".tmp-*"))
    cache.delete("data/index.json")
    cache.delete("data/index.json")  # idempotent
    assert cache.get("data/index.json") is None
    cache.put("data/earth/ABW/ABW_ADM0.geojson", b"x")
    cache.clear()
    assert not cache.dir.exists()
    with pytest.raises(ValueError, match="unexpected path"):
        cache.put("../escape.json", b"")
