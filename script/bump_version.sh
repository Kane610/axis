#!/usr/bin/env bash
# Update dependencies, bump the release version, and open a validated pull request.
set -eu

if ! command -v uv >/dev/null 2>&1; then
    printf '%s\n' "uv is required. Run ./script/setup.sh first." >&2
    exit 1
fi

SCRIPT_DIR="$(CDPATH= cd "$(dirname "$0")" && pwd)"
exec uv run --script "$SCRIPT_DIR/_maintenance.py" --bump-version "$@"
