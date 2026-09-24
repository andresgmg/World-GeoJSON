"""geoworld — a thin client for the World GeoJSON administrative boundaries.

    >>> from geoworld import GeoWorld
    >>> world = GeoWorld("1.0.0")
    >>> world.get("CHL", "ADM1")["features"][0]["id"]
    'CHL:ADM1:CL-CO'

Reads ``data/index.json`` from a pinned data release, downloads files on
demand, caches them on disk and verifies their ``sha256`` against the index.
Zero dependencies; ``pip install geoworld[geopandas]`` adds ``to_geopandas()``.
"""

from .cache import default_cache_dir
from .client import (
    DEFAULT_BASE_URL,
    DEFAULT_DATA_VERSION,
    SUPPORTED_SCHEMA_VERSION,
    GeoWorld,
    __version__,
    normalise,
    parse_id,
    summarise,
)
from .errors import (
    ChecksumMismatch,
    DownloadError,
    GeoWorldError,
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

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_DATA_VERSION",
    "SUPPORTED_SCHEMA_VERSION",
    "BBox",
    "ChecksumMismatch",
    "Country",
    "CountrySummary",
    "Dataset",
    "DownloadError",
    "Feature",
    "FeatureCollection",
    "FeatureId",
    "GeoWorld",
    "GeoWorldError",
    "Index",
    "InvalidFeatureId",
    "NoCombinedFile",
    "NoPreview",
    "NotSplit",
    "Part",
    "UnknownCountry",
    "UnknownFeature",
    "UnknownLevel",
    "UnknownPart",
    "UnsupportedSchema",
    "__version__",
    "default_cache_dir",
    "normalise",
    "parse_id",
    "summarise",
]
