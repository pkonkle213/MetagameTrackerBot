#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."

python_bin="$(command -v python3 || command -v python)"
requirements_file="$(mktemp)"
trap 'rm -f "$requirements_file"' EXIT

uv export \
  --locked \
  --no-dev \
  --format requirements-txt \
  --no-emit-project \
  --output-file "$requirements_file"

uv pip install \
  --python "$python_bin" \
  --requirements "$requirements_file"
