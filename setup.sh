#!/usr/bin/env bash
# Setup the repository.

# Stop on errors
set -e

cd "$(dirname "$0")"

if command -v uv >/dev/null 2>&1; then
    uv sync --all-extras
    uv run pre-commit install
else
    python3 -m venv venv
    source venv/bin/activate
    python3 -m pip install ".[requirements, requirements-test, requirements-dev]"
    pre-commit install
fi
