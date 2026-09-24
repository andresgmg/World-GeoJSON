# Task runner for contributors. Install with `pip install rust-just` (or your
# package manager), then `just` to list recipes. Every recipe here is a plain
# command you can also run by hand.

set shell := ["bash", "-euo", "pipefail", "-c"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# List recipes.
default:
    @just --list

# Install the Python dev toolchain and the pinned mapshaper.
setup:
    python -m pip install -r requirements-dev.txt
    npm ci

# Lint, format-check and type-check scripts/ and tests/.
lint:
    ruff check .
    ruff format --check .
    mypy

# Auto-format Python.
fmt:
    ruff format .
    ruff check --fix .

# Run the test suite.
test *ARGS:
    pytest {{ARGS}}

# Validate every dataset under data/.
validate *DIRS:
    python scripts/validate_data.py {{DIRS}}

# Regenerate previews for one or more country directories (default: all).
previews *DIRS:
    node scripts/make_previews.mjs {{DIRS}}

# Regenerate manifest.json for the given country directories.
manifest +DIRS:
    python scripts/build_manifest.py {{DIRS}}

# Fail if any committed manifest disagrees with a fresh regeneration.
check-manifests:
    python scripts/build_manifest.py data/earth/*/
    git diff --quiet -- 'data/**/manifest.json'

# Build the documentation site strictly (needs requirements-docs.txt).
docs:
    mkdocs build --strict

# Serve the documentation site locally.
serve:
    mkdocs serve

# Everything CI runs, in order.
ci: lint test validate check-manifests
