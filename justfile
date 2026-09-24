# Task runner for contributors. Install with `pip install rust-just` (or your
# package manager), then `just` to list recipes. Every recipe here is a plain
# command you can also run by hand.

set shell := ["bash", "-euo", "pipefail", "-c"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# List recipes.
default:
    @just --list

# Install the pipeline (editable), the dev toolchain and the pinned mapshaper.
setup:
    python -m pip install -r requirements-dev.txt
    npm ci

# Lint, format-check and type-check the pipeline package, its tests and the shims.
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

# Validate every dataset under data/ (add --checksums to re-hash every file).
validate *ARGS:
    wgj validate {{ARGS}}

# Apply the data contract to committed files (ids, hierarchy, bbox, layout).
finalize *DIRS:
    wgj finalize {{DIRS}}

# Regenerate previews for one or more country directories (default: all).
previews *DIRS:
    wgj previews {{DIRS}}

# Regenerate manifest.json for the given country directories.
manifest +DIRS:
    wgj manifest {{DIRS}}

# Regenerate data/index.json.
index:
    wgj index

# Everything CI checks about committed data: validation, finalize, index and manifest freshness.
check-data:
    wgj validate --checksums
    wgj finalize --check data/earth/*/
    wgj index --check
    wgj manifest data/earth/*/
    git diff --quiet -- 'data/**/manifest.json'

# Build the documentation site strictly (needs requirements-docs.txt).
docs:
    mkdocs build --strict

# Serve the documentation site locally.
serve:
    mkdocs serve

# Everything CI runs, in order.
ci: lint test check-data
