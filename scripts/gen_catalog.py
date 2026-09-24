"""Compatibility shim: the MkDocs hook now lives in pipeline/mkdocs_hook.py (wgj.catalog)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline" / "src"))

from wgj.catalog import on_config, on_files, on_page_markdown

__all__ = ["on_config", "on_files", "on_page_markdown"]
