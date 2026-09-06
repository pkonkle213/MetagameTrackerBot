#!/usr/bin/env bash
set -euo pipefail

# Reconcile the Python environment with the committed lockfile after task merges.
uv sync --frozen