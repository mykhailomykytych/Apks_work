#!/usr/bin/env bash
# CI build script for Linux and macOS.
# Installs dependencies, builds, runs unit tests and produces the executable bin/hello.
set -euo pipefail

cd "$(dirname "$0")/.."

echo "== Environment"
node --version
npm --version

echo "== Install dependencies"
npm ci

echo "== Build"
npm run build

echo "== Unit tests"
npm test

echo "== Package executable"
npm run package

echo "== Run executable"
./bin/hello

echo "== CI finished successfully"
