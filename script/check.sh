#!/bin/sh
set -eu
cd "$(dirname "$0")/.."

uv lock --check
uv run --locked ruff check .
uv run --locked ruff format --check .
uv run --locked mypy axis
uv run --locked pytest tests --doctest-modules

pnpm --dir web install --frozen-lockfile
pnpm --dir web lint
pnpm --dir web format:check
pnpm --dir web test
pnpm --dir web test:e2e

uv run --locked python script/check_cli_install.py
