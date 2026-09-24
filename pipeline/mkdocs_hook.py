"""MkDocs hook shim: `hooks: [pipeline/mkdocs_hook.py]` in mkdocs.yml.

MkDocs loads hooks by file path, so this file puts the package on sys.path
and re-exports wgj.catalog's hooks. No install step is needed to build the
docs; the catalog code has no dependencies beyond the standard library.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from wgj.catalog import on_config, on_files, on_page_markdown

__all__ = ["on_config", "on_files", "on_page_markdown"]
