#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")/.."
npm ci
npm run build:public-site
exec python3 main.py
