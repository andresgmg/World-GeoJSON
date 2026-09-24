from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from geoworld import (
    DEFAULT_BASE_URL,
    DEFAULT_DATA_VERSION,
    ChecksumMismatch,
    DownloadError,
    GeoWorld,
    InvalidFeatureId,
    NoCombinedFile,
    NoPreview,
    NotSplit,
    UnknownCountry,
    UnknownFeature,
    UnknownLevel,
    UnknownPart,
    UnsupportedSchema,
    normalise,
    parse_id,
)


def test_default_urls() -> None:
    world = GeoWorld(cache=False)
    assert world.version == DEFAULT_DATA_VERSION
    assert world.base_url == f"{DEFAULT_BASE_URL}/v{DEFAULT_DATA_VERSION}"
    assert world.url_for("data/index.json").endswith("/v1.0.0/data/index.json")
    assert GeoWorld("2.3.4", cache=False).base_url.endswith("/v2.3.4")
    assert (
        GeoWorld(base_url="https://cdn.example/wg/", cache=False).base_url
        == "https://cdn.example/wg"
    )


def test_main_warns_and_disables_disk_cache(tmp_path: Path) -> None:
    with pytest.warns(UserWarning, match="moving branch"):
        world = GeoWorld("main", cache_dir=tmp_path)
    assert world.base_url.endswith("/main")
    assert world.cache_dir is None


def test_index_and_summaries(world: GeoWorld) -> None:
    index = world.index()
    assert index["schema_version"] == 1
    assert index["totals"]["countries"] == 3
    assert index is world.index()  # fetched once
    summaries = world.countries()
    assert [c["iso_a3"] for c in summaries] == ["ABW", "BRB", "DOM"]
    dom = next(c for c in summaries if c["iso_a3"] == "DOM")
    assert dom["features"] == 1 + 32 + 11
    assert dom["datasets"] == 3
    assert "datasets" in world.country("DOM")
    assert world.country("dom")["iso_a3"] == "DOM"
    assert world.levels("DOM") == ["ADM0", "ADM1", "ADM2"]
    assert world.dataset("DOM", "adm1")["level"] == "ADM1"
    assert world.bbox("ABW", "ADM0") == [-70.062408, 12.41767, -69.87682, 12.632148]
    assert world.parts("DOM", "ADM2") == ["DO-01", "DO-02"]


def test_lookups_fail_loudly(world: GeoWorld) -> None:
    with pytest.raises(UnknownCountry, match="XXX"):
        world.country("XXX")
    with pytest.raises(UnknownLevel, match="ABW has no ADM1; available: ADM0"):
        world.get("ABW", "ADM1")
    with pytest.raises(NotSplit):
        world.parts("DOM", "ADM1")
    with pytest.raises(UnknownPart):
        world.get_part("DOM", "ADM2", "DO-99")
    with pytest.raises(NoPreview):
        world.preview("DOM", "ADM2")
    with pytest.raises(UnknownFeature):
        world.find("DOM:ADM1:DO-99")
    with pytest.raises(InvalidFeatureId):
        world.find("not an id")
    with pytest.raises(ValueError, match="either part or preview"):
        world.url("DOM", "ADM1", "x", preview=True)


def test_urls(world: GeoWorld, fixtures: Path) -> None:
    base = fixtures.as_uri()
    assert world.url("DOM", "ADM1") == f"{base}/data/earth/DOM/DOM_ADM1.geojson"
    assert world.url("DOM", "ADM2", "DO-01") == f"{base}/data/earth/DOM/ADM2/DO-01.geojson"
    assert world.url("DOM", "ADM2", "do-01").endswith("/DO-01.geojson")
    assert world.url("DOM", "ADM1", preview=True).endswith("/preview/DOM_ADM1.preview.geojson")


def test_get_and_parts(world: GeoWorld) -> None:
    adm0 = world.get("ABW", "ADM0")
    assert adm0["type"] == "FeatureCollection"
    assert adm0["features"][0]["id"] == "ABW:ADM0:ABW"
    assert adm0 is world.get("ABW", "ADM0")  # memory-cached
    part = world.get_part("DOM", "ADM2", "DO-01")
    assert [f["id"] for f in part["features"]] == ["DOM:ADM2:DO-01.distrito-nacional"]
    codes = [code for code, _fc in world.iter_parts("DOM", "ADM2")]
    assert codes == ["DO-01", "DO-02"]
    assert sum(1 for _ in world.features("DOM", "ADM2")) == 11
    assert len(world.preview("BRB", "ADM1")["features"]) == 11
    assert set(world.preview("BRB", "ADM1")["features"][0]["properties"]) == {
        "shapeName",
        "shapeISO",
        "shapeType",
    }


def test_split_level_without_combined_file(world: GeoWorld) -> None:
    """Brazil ADM2 has parts and no path; the fixture simulates it by editing the index."""
    dataset = world.dataset("DOM", "ADM2")
    dataset.pop("path", None)  # DOM ADM2 fixture has no combined file already
    with pytest.raises(NoCombinedFile, match="iter_parts"):
        world.get("DOM", "ADM2")
    with pytest.raises(NoCombinedFile):
        world.url("DOM", "ADM2")
    assert [f["id"] for f in world.features("DOM", "ADM2")][:2] == [
        "DOM:ADM2:DO-01.distrito-nacional",
        "DOM:ADM2:DO-02.azua-de-compostela",
    ]


def test_navigation(world: GeoWorld) -> None:
    province = world.find("DOM:ADM1:DO-01")
    assert province["properties"]["shapeName"] == "Distrito Nacional"
    assert world.parent("DOM:ADM0:DOM") is None
    assert world.parent("DOM:ADM1:DO-01")["id"] == "DOM:ADM0:DOM"  # type: ignore[index]
    municipality = world.find("DOM:ADM2:DO-02.estebania")
    assert municipality["properties"]["parentID"] == "DOM:ADM1:DO-02"
    assert world.parent("DOM:ADM2:DO-02.estebania")["id"] == "DOM:ADM1:DO-02"  # type: ignore[index]
    assert [f["id"] for f in world.children("DOM:ADM1:DO-01")] == [
        "DOM:ADM2:DO-01.distrito-nacional"
    ]
    assert len(world.children("DOM:ADM1:DO-02")) == 10
    assert world.children("DOM:ADM1:DO-05") == []  # no part for that province in the fixture
    assert len(world.children("DOM:ADM0:DOM")) == 32
    assert world.children("DOM:ADM2:DO-02.estebania") == []  # leaf level
    with pytest.raises(UnknownLevel):
        world.children("DOM:ADM3:x")


def test_find_reads_only_the_part_it_needs(world: GeoWorld) -> None:
    world.find("DOM:ADM2:DO-01.distrito-nacional")
    assert "data/earth/DOM/ADM2/DO-01.geojson" in world._memory
    assert "data/earth/DOM/ADM2/DO-02.geojson" not in world._memory


def test_search(world: GeoWorld) -> None:
    assert [f["id"] for f in world.search("santo", "DOM")] == ["DOM:ADM1:DO-32"]
    assert [f["id"] for f in world.search("Compostéla", "dom", "adm2")] == [
        "DOM:ADM2:DO-02.azua-de-compostela"
    ]
    assert [f["id"] for f in world.search("do-01", "DOM", "ADM1")] == ["DOM:ADM1:DO-01"]
    assert world.search("   ", "DOM") == []
    assert normalise("  Ñuñoa  DEL  Mar ") == "nunoa del mar"


def test_parse_id() -> None:
    assert parse_id("USA:ADM2:US-DE.new-castle") == {
        "iso3": "USA",
        "level": "ADM2",
        "key": "US-DE.new-castle",
    }
    with pytest.raises(InvalidFeatureId):
        parse_id("usa:ADM2:x")


def test_disk_cache_roundtrip_and_verification(world: GeoWorld, fixtures: Path) -> None:
    assert world.cache_dir is not None
    world.get("ABW", "ADM0")
    cached = world.cache_dir / "data" / "earth" / "ABW" / "ABW_ADM0.geojson"
    assert cached.read_bytes() == (fixtures / "data/earth/ABW/ABW_ADM0.geojson").read_bytes()
    # A second client reads from disk, and re-hashes what it reads.
    again = GeoWorld(base_url="https://unreachable.invalid", cache_dir=world.cache_dir.parent)
    assert again.get("ABW", "ADM0")["features"][0]["id"] == "ABW:ADM0:ABW"
    # Corrupt the cached file: it is discarded and refetched (here, unreachable).
    cached.write_bytes(b'{"type":"FeatureCollection","features":[]}')
    again.clear_cache(disk=False)
    with pytest.raises(DownloadError):
        again.get("ABW", "ADM0")
    assert not cached.exists()
    world.clear_cache()
    assert not world.cache_dir.exists()


def test_checksum_mismatch(world: GeoWorld) -> None:
    dataset = world.dataset("ABW", "ADM0")
    dataset["sha256"] = "0" * 64
    with pytest.raises(ChecksumMismatch, match="ABW_ADM0"):
        world.get("ABW", "ADM0")
    assert world.cache_dir is not None
    assert not (world.cache_dir / "data" / "earth" / "ABW" / "ABW_ADM0.geojson").exists()
    relaxed = GeoWorld(base_url=world.base_url, cache=False, verify=False)
    relaxed.dataset("ABW", "ADM0")["sha256"] = "0" * 64
    assert relaxed.get("ABW", "ADM0")["features"]


def test_unsupported_schema(tmp_path: Path) -> None:
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "index.json").write_text(
        json.dumps({"schema_version": 2, "bodies": [], "totals": {}, "countries": []})
    )
    world = GeoWorld(base_url=tmp_path.as_uri(), cache=False)
    with pytest.raises(UnsupportedSchema, match="upgrade geoworld"):
        world.index()


def test_download_error(tmp_path: Path) -> None:
    world = GeoWorld(base_url=tmp_path.as_uri(), cache=False)
    with pytest.raises(DownloadError, match=r"index\.json"):
        world.index()


def test_sha256_of_fixture_files_matches_index(world: GeoWorld, fixtures: Path) -> None:
    for country in world.index()["countries"]:
        for dataset in country["datasets"]:
            entries: list[tuple[str, str]] = []
            if "path" in dataset:
                entries.append((dataset["path"], dataset["sha256"]))
            entries += [(part["path"], part["sha256"]) for part in dataset.get("parts", [])]
            for path, expected in entries:
                digest = hashlib.sha256((fixtures / path).read_bytes()).hexdigest()
                assert digest == expected, path
