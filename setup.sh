#!/usr/bin/env bash
# Setup the repository.

# Stop on errors
set -e

cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
    echo "uv is required for setup. Install uv from https://docs.astral.sh/uv/"
    exit 1
fi

uv sync --all-extras
uv run pre-commit install
