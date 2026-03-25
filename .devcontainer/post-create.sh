#!/bin/bash
set -e

pip install uv

cd src/api && uv sync && cd ../..
cd src/web && npm ci && cd ../..

npx playwright install-deps
npx playwright install

# Install Aspire orchestrator
curl -sSL https://aspire.dev/install.sh | bash

pip install mkdocs mkdocs-material

source ~/.bashrc
