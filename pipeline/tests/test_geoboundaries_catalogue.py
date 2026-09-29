"""The geoBoundaries catalogue is built from the pinned metadata CSV, offline here."""

from __future__ import annotations

from wgj.sources import geoboundaries as gb
from wgj.sources.natural_earth import ne_code

CSV = (
    "boundaryID,boundaryName,boundaryISO,boundaryYearRepresented,boundaryType,"
    "boundarySource,boundaryLicense,admUnitCount\n"
    "FRA-ADM1-1,France,FRA,2022,ADM1,IGN,Licence Ouverte / Open Licence (Etalab),13\n"
    "DEU-ADM1-1,Germany,DEU,2021,ADM1,BKG,Data license Germany - Attribution - Version 2.0,16\n"
    "AUT-ADM1-1,Austria,AUT,2017,ADM1,OpenStreetMap,Open Data Commons Open Database License 1.0,\n"
    ",,,,,,,\n"
)


def test_catalogue_records_carry_licence_units_and_a_pinned_media_url() -> None:
    records = gb.catalogue_from_csv(CSV, ref="abc123")
    assert [(r["boundaryISO"], r["boundaryType"]) for r in records] == [
        ("FRA", "ADM1"),
        ("DEU", "ADM1"),
        ("AUT", "ADM1"),
    ]
    fra, deu, aut = records
    assert fra["admUnitCount"] == 13
    assert aut["admUnitCount"] is None  # blank upstream
    assert deu["boundarySource"] == "BKG"
    assert fra["gjDownloadURL"] == (
        "https://media.githubusercontent.com/media/wmgeolab/geoBoundaries/abc123/"
        "releaseData/gbOpen/FRA/ADM1/geoBoundaries-FRA-ADM1.geojson"
    )


def test_the_default_ref_is_a_pinned_commit() -> None:
    assert len(gb.GB_REF) == 40 and all(c in "0123456789abcdef" for c in gb.GB_REF)
    assert gb.GB_REF in gb.GB_META_URL
    assert gb.GB_REF in gb.gb_download_url("CHL", "ADM1")


def test_natural_earth_aliases() -> None:
    assert ne_code("XKX") == "KOS"
    assert ne_code("FRA") == "FRA"
