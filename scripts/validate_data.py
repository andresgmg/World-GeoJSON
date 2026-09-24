"""Compatibility entry point: use `wgj validate` (pipeline/, `pip install -e ./pipeline[pipeline]`).

Kept for one release so existing commands and docs links keep working.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "pipeline" / "src"))

from wgj.validate import main

if __name__ == "__main__":
    raise SystemExit(main())
