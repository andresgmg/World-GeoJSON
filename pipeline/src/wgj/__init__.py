"""World GeoJSON pipeline.

The package behind the `wgj` command: it fetches upstream boundary data,
normalises and simplifies it with mapshaper, applies the data contract
(stable ids, hierarchy, corrections), writes previews, manifests and the
global index, validates everything against the JSON Schemas and renders the
documentation catalog. See docs/contributing/pipeline.md.
"""

__version__ = "0.1.0"
