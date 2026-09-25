from __future__ import annotations

import subprocess
import sys

from wgj import __version__, cli


def test_help_and_version(capsys) -> None:  # type: ignore[no-untyped-def]
    assert cli.main([]) == 0
    out = capsys.readouterr().out
    assert "commands:" in out and "validate" in out
    assert cli.main(["--version"]) == 0
    assert __version__ in capsys.readouterr().out


def test_unknown_command(capsys) -> None:  # type: ignore[no-untyped-def]
    assert cli.main(["frobnicate"]) == 2
    assert "unknown command" in capsys.readouterr().err


def test_module_entry_point() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "wgj", "index", "--help"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0 and "usage:" in proc.stdout
