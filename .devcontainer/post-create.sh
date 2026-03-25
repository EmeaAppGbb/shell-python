#!/bin/bash
set -e

pip install uv

cd src/api && uv sync && cd ../..
cd src/web && npm ci && cd ../..

npx playwright install-deps
npx playwright install

pip install mkdocs mkdocs-material
