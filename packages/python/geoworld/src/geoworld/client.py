"""The client: a pinned data version, an index, files fetched on demand."""

from __future__ import annotations

import hashlib
import json
import os
import re
import unicodedata
import warnings
from collections.abc import Iterator
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from ._http import fetch_bytes
from .cache import DiskCache, default_cache_dir
from .errors import (
    ChecksumMismatch,
    InvalidFeatureId,
    NoCombinedFile,
    NoPreview,
    NotSplit,
    UnknownCountry,
    UnknownFeature,
    UnknownLevel,
    UnknownPart,
    UnsupportedSchema,
)
from .types import (
    BBox,
    Country,
    CountrySummary,
    Dataset,
    Feature,
    FeatureCollection,
    FeatureId,
    Index,
    Part,
)

if TYPE_CHECKING:
    import geopandas

__version__ = "0.1.0"

SUPPORTED_SCHEMA_VERSION = 1
"""The newest ``index.schema_version`` this client understands."""

DEFAULT_DATA_VERSION = "1.0.0"
"""The data release used when none is given."""

DEFAULT_BASE_URL = "https://raw.githubusercontent.com/andresgmg/World-GeoJSON"
"""Files are read from ``{DEFAULT_BASE_URL}/v{version}/{path}`` unless ``base_url`` is given."""

INDEX_PATH = "data/index.json"

FEATURE_ID = re.compile(r"^([A-Z]{3}):(ADM[0-4]|QUAD):(\S+)$")


def parse_id(feature_id: str) -> FeatureId:
    """Split ``"CHL:ADM3:01402"`` into its territory, level and key."""
    match = FEATURE_ID.match(feature_id)
    if not match:
        raise InvalidFeatureId(f"not a feature id ({{ISO3}}:{{LEVEL}}:{{key}}): {feature_id!r}")
    return {"iso3": match[1], "level": match[2], "key": match[3]}


def normalise(text: str) -> str:
    """Accent- and case-insensitive form used by :meth:`GeoWorld.search`.

    Mirrors the JavaScript client exactly (NFKD, drop marks, lower-case,
    collapse whitespace) so both find the same features.
    """
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in decomposed if not unicodedata.category(ch).startswith("M"))
    return " ".join(stripped.lower().split())


def summarise(country: Country) -> CountrySummary:
    """The index entry without its datasets, plus totals across them."""
    datasets = country["datasets"]
    return {
        "iso_a3": country["iso_a3"],
        "iso_a2": country.get("iso_a2"),
        "name": country["name"],
        "m49_region": country.get("m49_region"),
        "status": country["status"],
        "license": country["license"],
        "licenses": list(country["licenses"]),
        "levels": list(country["levels"]),
        "municipal_level": country["municipal_level"],
        "datasets": len(datasets),
        "features": sum(d["features"] for d in datasets),
        "bytes": sum(d["bytes"] for d in datasets),
    }


class GeoWorld:
    """Read one version of the World GeoJSON data.

    Args:
        version: A data release tag without the ``v`` (``"1.0.0"``), or ``"main"``
            to follow the branch (warns; nothing is cached on disk).
        base_url: Where the repository tree is served from. Defaults to
            ``raw.githubusercontent.com`` at the release tag; any static host
            or ``file://`` directory with the same layout works.
        cache_dir: Directory for downloaded files (``<cache_dir>/<version>/<path>``).
            Defaults to the platform cache directory; see
            :func:`geoworld.cache.default_cache_dir`.
        cache: ``False`` keeps files in memory only.
        verify: Check every download and cached file against the ``sha256`` in
            the index. Previews are not hashed upstream and are not checked.
        timeout: Seconds per request.

    Objects returned by ``get``, ``get_part``, ``preview`` and ``index`` are
    cached in memory and shared between calls: copy them before mutating.
    """

    def __init__(
        self,
        version: str = DEFAULT_DATA_VERSION,
        *,
        base_url: str | None = None,
        cache_dir: str | os.PathLike[str] | None = None,
        cache: bool = True,
        verify: bool = True,
        timeout: float = 30.0,
        user_agent: str | None = None,
    ) -> None:
        self.version = str(version)
        if base_url is None:
            ref = "main" if self.version == "main" else f"v{self.version}"
            base_url = f"{DEFAULT_BASE_URL}/{ref}"
        self.base_url = base_url.rstrip("/")
        self.verify = verify
        self.timeout = timeout
        self.user_agent = user_agent or (
            f"geoworld/{__version__} (+https://github.com/andresgmg/World-GeoJSON)"
        )
        if self.version == "main":
            warnings.warn(
                "GeoWorld(version='main') follows a moving branch: results change between "
                "runs and nothing is cached on disk. Pin a release, e.g. GeoWorld('1.0.0').",
                stacklevel=2,
            )
            cache = False
        root = Path(cache_dir) if cache_dir is not None else default_cache_dir()
        self._disk: DiskCache | None = DiskCache(root, self.version) if cache else None
        self._memory: dict[str, Any] = {}
        self._index: Index | None = None

    def __repr__(self) -> str:
        return f"GeoWorld(version={self.version!r}, base_url={self.base_url!r})"

    # -- transport ----------------------------------------------------------

    @property
    def cache_dir(self) -> Path | None:
        """Where this version's files are cached, or ``None`` when caching is off."""
        return self._disk.dir if self._disk else None

    def url_for(self, path: str) -> str:
        """Absolute URL of a repository path such as ``data/index.json``."""
        return f"{self.base_url}/{path}"

    def _read(self, path: str, sha256: str | None = None) -> bytes:
        expected = sha256 if self.verify else None
        if self._disk is not None:
            cached = self._disk.get(path)
            if cached is not None:
                if expected is None or hashlib.sha256(cached).hexdigest() == expected:
                    return cached
                self._disk.delete(path)
        data = fetch_bytes(self.url_for(path), timeout=self.timeout, user_agent=self.user_agent)
        if expected is not None:
            actual = hashlib.sha256(data).hexdigest()
            if actual != expected:
                raise ChecksumMismatch(path, expected, actual)
        if self._disk is not None:
            self._disk.put(path, data)
        return data

    def _load(self, path: str, sha256: str | None = None) -> Any:
        if path not in self._memory:
            self._memory[path] = json.loads(self._read(path, sha256))
        return self._memory[path]

    def clear_cache(self, *, disk: bool = True) -> None:
        """Forget everything held in memory and, by default, on disk for this version."""
        self._memory.clear()
        self._index = None
        if disk and self._disk is not None:
            self._disk.clear()

    # -- index --------------------------------------------------------------

    def index(self) -> Index:
        """``data/index.json`` for this version, fetched once."""
        if self._index is None:
            raw = self._load(INDEX_PATH)
            found = raw.get("schema_version") if isinstance(raw, dict) else None
            if not isinstance(found, int) or found > SUPPORTED_SCHEMA_VERSION:
                raise UnsupportedSchema(found, SUPPORTED_SCHEMA_VERSION)
            self._index = cast(Index, raw)
        return self._index

    def countries(self) -> list[CountrySummary]:
        """Every territory in the index, without the per-dataset detail."""
        return [summarise(c) for c in self.index()["countries"]]

    def country(self, iso3: str) -> Country:
        """The full index entry of one territory."""
        code = iso3.upper()
        for country in self.index()["countries"]:
            if country["iso_a3"] == code:
                return country
        raise UnknownCountry(code)

    def levels(self, iso3: str) -> list[str]:
        """Published levels, lowest number first (``["ADM0", "ADM1", …]``)."""
        return list(self.country(iso3)["levels"])

    def dataset(self, iso3: str, level: str) -> Dataset:
        """The index entry of one level of one territory."""
        country = self.country(iso3)
        wanted = level.upper()
        for dataset in country["datasets"]:
            if dataset["level"] == wanted:
                return dataset
        raise UnknownLevel(country["iso_a3"], wanted, list(country["levels"]))

    def bbox(self, iso3: str, level: str) -> BBox:
        """``[west, south, east, north]`` of a level, from the index (no download)."""
        return list(self.dataset(iso3, level)["bbox"])

    def parts(self, iso3: str, level: str) -> list[str]:
        """Part codes of a split level, in index order."""
        return [part["code"] for part in self._parts(iso3, level)]

    def url(self, iso3: str, level: str, part: str | None = None, *, preview: bool = False) -> str:
        """URL of a level's file, one of its parts, or its preview (no download)."""
        dataset = self.dataset(iso3, level)
        if preview:
            if part is not None:
                raise ValueError("previews cover whole levels; give either part or preview")
            return self.url_for(self._preview_path(dataset, iso3))
        if part is not None:
            return self.url_for(self._part(iso3, level, part)["path"])
        if "path" not in dataset:
            raise NoCombinedFile(iso3.upper(), dataset["level"])
        return self.url_for(dataset["path"])

    # -- files --------------------------------------------------------------

    def get(self, iso3: str, level: str) -> FeatureCollection:
        """The full-resolution FeatureCollection of a level."""
        dataset = self.dataset(iso3, level)
        if "path" not in dataset:
            raise NoCombinedFile(iso3.upper(), dataset["level"])
        return cast(FeatureCollection, self._load(dataset["path"], dataset.get("sha256")))

    def get_part(self, iso3: str, level: str, code: str) -> FeatureCollection:
        """One part of a split level (``code`` is the ADM1 key, or ``"unassigned"``)."""
        part = self._part(iso3, level, code)
        return cast(FeatureCollection, self._load(part["path"], part["sha256"]))

    def iter_parts(self, iso3: str, level: str) -> Iterator[tuple[str, FeatureCollection]]:
        """``(code, FeatureCollection)`` for every part of a split level, in index order."""
        for part in self._parts(iso3, level):
            yield part["code"], cast(FeatureCollection, self._load(part["path"], part["sha256"]))

    def preview(self, iso3: str, level: str) -> FeatureCollection:
        """The simplified preview of a level (≤ 2 MB; name, code and type properties only)."""
        dataset = self.dataset(iso3, level)
        return cast(FeatureCollection, self._load(self._preview_path(dataset, iso3)))

    def features(self, iso3: str, level: str) -> Iterator[Feature]:
        """Every feature of a level, from the combined file or across its parts."""
        dataset = self.dataset(iso3, level)
        if "path" in dataset:
            yield from self.get(iso3, level)["features"]
        else:
            for _code, collection in self.iter_parts(iso3, level):
                yield from collection["features"]

    # -- navigation ---------------------------------------------------------

    def find(self, feature_id: str) -> Feature:
        """The feature with this id, downloading only what is needed to reach it."""
        parsed = parse_id(feature_id)
        dataset = self.dataset(parsed["iso3"], parsed["level"])
        parts = dataset.get("parts")
        if parts:
            # Municipal keys are "{adm1 key}.{slug}" when the upstream has no
            # code, and that adm1 key names the part: one small file instead
            # of the combined one.
            prefix = parsed["key"].split(".", 1)[0]
            for part in parts:
                if part["code"] == prefix:
                    collection = self.get_part(parsed["iso3"], parsed["level"], prefix)
                    found = self._match_id(collection, feature_id)
                    if found is not None:
                        return found
                    break
        for feature in self.features(parsed["iso3"], parsed["level"]):
            if feature.get("id") == feature_id:
                return feature
        raise UnknownFeature(feature_id)

    def parent(self, feature_id: str) -> Feature | None:
        """The feature named by ``parentID``, or ``None`` at the top level."""
        parent_id = self.find(feature_id)["properties"].get("parentID")
        return self.find(parent_id) if parent_id else None

    def children(self, feature_id: str) -> list[Feature]:
        """Features of the next published level whose ``parentID`` is this id."""
        parsed = parse_id(feature_id)
        country = self.country(parsed["iso3"])
        levels = country["levels"]
        if parsed["level"] not in levels:
            raise UnknownLevel(country["iso_a3"], parsed["level"], list(levels))
        position = levels.index(parsed["level"]) + 1
        if position >= len(levels):
            return []
        child_level = levels[position]
        dataset = self.dataset(parsed["iso3"], child_level)
        candidates: Iterator[Feature]
        if parsed["level"] == "ADM1" and any(
            part["code"] == parsed["key"] for part in dataset.get("parts", [])
        ):
            # A split level's parts are keyed by ADM1: the children all live in one part.
            candidates = iter(self.get_part(parsed["iso3"], child_level, parsed["key"])["features"])
        else:
            candidates = self.features(parsed["iso3"], child_level)
        return [f for f in candidates if f["properties"].get("parentID") == feature_id]

    def search(self, text: str, iso3: str, level: str | None = None) -> list[Feature]:
        """Features whose ``shapeName`` contains ``text`` (accent- and case-insensitive)
        or whose ``shapeISO`` equals it, in one territory and, optionally, one level."""
        query = normalise(text)
        if not query:
            return []
        levels = [level.upper()] if level else self.levels(iso3)
        hits: list[Feature] = []
        for each in levels:
            for feature in self.features(iso3, each):
                props = feature["properties"]
                name = normalise(str(props.get("shapeName", "")))
                code = normalise(str(props.get("shapeISO", "")))
                if query in name or (code and code == query):
                    hits.append(feature)
        return hits

    # -- extras -------------------------------------------------------------

    def to_geopandas(
        self, iso3: str, level: str, *, part: str | None = None
    ) -> geopandas.GeoDataFrame:
        """A GeoDataFrame (EPSG:4326) with the feature ``id`` as its first column.

        Needs the ``geopandas`` extra: ``pip install geoworld[geopandas]``.
        A level published as parts only is concatenated unless ``part`` is given.
        """
        try:
            import geopandas as gpd
        except ImportError as exc:  # pragma: no cover - exercised only without the extra
            message = "to_geopandas() needs geopandas: pip install geoworld[geopandas]"
            raise ImportError(message) from exc
        if part is not None:
            features = self.get_part(iso3, level, part)["features"]
        else:
            features = list(self.features(iso3, level))
        frame = gpd.GeoDataFrame.from_features(features, crs="EPSG:4326")
        frame.insert(0, "id", [feature.get("id") for feature in features])
        return frame

    # -- helpers ------------------------------------------------------------

    def _parts(self, iso3: str, level: str) -> list[Part]:
        dataset = self.dataset(iso3, level)
        parts = dataset.get("parts")
        if not parts:
            raise NotSplit(iso3.upper(), dataset["level"])
        return parts

    def _part(self, iso3: str, level: str, code: str) -> Part:
        parts = self._parts(iso3, level)
        for part in parts:
            if part["code"] == code:
                return part
        folded = code.casefold()
        for part in parts:
            if part["code"].casefold() == folded:
                return part
        raise UnknownPart(iso3.upper(), level.upper(), code)

    @staticmethod
    def _preview_path(dataset: Dataset, iso3: str) -> str:
        path = dataset.get("preview")
        if not path:
            raise NoPreview(iso3.upper(), dataset["level"])
        return path

    @staticmethod
    def _match_id(collection: FeatureCollection, feature_id: str) -> Feature | None:
        for feature in collection["features"]:
            if feature.get("id") == feature_id:
                return feature
        return None
