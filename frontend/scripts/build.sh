#!/bin/bash
set -euo pipefail

echo "Building frontend..."

npm run build

echo "Build complete: dist/"
