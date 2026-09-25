# Task runner for contributors. Install with `pip install rust-just` (or your
# package manager), then `just` to list recipes. Every recipe here is a plain
# command you can also run by hand.

set shell := ["bash", "-euo", "pipefail", "-c"]
set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

# List recipes.
default:
    @just --list

# Install the pipeline and the Python client (editable), the dev toolchain, the
# pinned mapshaper and the JavaScript client's TypeScript.
setup:
    python -m pip install -r requirements-dev.txt
    npm ci

# Lint, format-check and type-check every Python package, plus the TypeScript packages.
lint:
    ruff check .
    ruff format --check .
    mypy
    npm run lint

# Auto-format Python.
fmt:
    ruff format .
    ruff check --fix .

# Run the Python test suites (pipeline and client).
test *ARGS:
    pytest {{ARGS}}

# Run the tests of every JavaScript package (node:test, compiled first).
test-js:
    npm test

# Build every JavaScript package (ESM + CJS + types into packages/js/*/dist).
build-js:
    npm run build

# Build the JavaScript packages and serve the repository so examples/*.html run locally.
examples: build-js
    @echo "open http://localhost:8000/examples/"
    python -m http.server 8000

# Rewrite fixtures/expected/*.json from the Python client; both clients must then match it.
goldens:
    python packages/python/geoworld/tests/goldens.py

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
ci: lint test test-js check-data
