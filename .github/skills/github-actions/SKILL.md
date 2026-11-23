---
name: github-actions
description: Create cross-platform CI - scripts/ci.sh, scripts/ci.bat and .github/workflows/ci.yml with a Windows/Linux/macOS matrix that only calls those scripts. Use from the create-actions command.
---

# Skill: github-actions

## When to use
- After `build-and-test` succeeded locally, or
- the user runs `/create-actions`, or the `init` orchestrator reaches step 4.

## Inputs
| Input | Default | Description |
|-------|---------|-------------|
| `branches` | `develop`, `master`, `main` | Target branches for `push` and `pull_request` (`feature/**` is added to `push`) |
| `osMatrix` | `ubuntu-latest`, `windows-latest`, `macos-latest` | Runners of the single matrix job |
| `nodeVersion` | `22` | Node.js version for `actions/setup-node` |

## Outputs
| File | Purpose |
|------|---------|
| `scripts/ci.sh` | Linux/macOS: `npm ci` → build → tests → executable → run (`set -euo pipefail`) |
| `scripts/ci.bat` | Windows: the same steps, each `|| exit /b 1`, CRLF line endings |
| `.github/workflows/ci.yml` | One job `build-and-test`, OS matrix, checkout → Node setup → CI script → upload `bin/` as artifact `hello-<os>` |

The workflow contains **no build logic**: configuration, build and tests are
executed only by `ci.sh` / `ci.bat`, so the same scripts work locally and in CI.

## Steps
1. Create `scripts/ci.sh` and make it executable (`chmod +x`, and
   `git update-index --chmod=+x scripts/ci.sh` when the repo is used on Windows).
2. Create `scripts/ci.bat` with CRLF line endings (guaranteed by `.gitattributes`).
3. Create `.github/workflows/ci.yml` from the template. If a workflow already
   exists, replace only when its content differs and the user confirms —
   never add a second job or a second workflow file for the same purpose.
4. Run `scripts/ci.sh` locally (on Windows: `scripts\ci.bat`).
5. Run `node scripts/check.mjs --static` to validate the workflow structure.

## Templates
#### `scripts/ci.sh`
````bash
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
````

#### `scripts/ci.bat`
````bat
@echo off
rem CI build script for Windows.
rem Installs dependencies, builds, runs unit tests and produces the executable bin\hello.exe.
setlocal
cd /d "%~dp0\.."

echo == Environment
call node --version || exit /b 1
call npm --version || exit /b 1

echo == Install dependencies
call npm ci || exit /b 1

echo == Build
call npm run build || exit /b 1

echo == Unit tests
call npm test || exit /b 1

echo == Package executable
call npm run package || exit /b 1

echo == Run executable
bin\hello.exe || exit /b 1

echo == CI finished successfully
endlocal
````

#### `.github/workflows/ci.yml`
````yaml
name: CI

on:
  push:
    branches: [develop, master, main, "feature/**"]
  pull_request:
    branches: [develop, master, main]

permissions:
  contents: read

jobs:
  build-and-test:
    name: Build and test (${{ matrix.os }})
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm

      - name: Configure, build and test (Linux/macOS)
        if: runner.os != 'Windows'
        shell: bash
        run: ./scripts/ci.sh

      - name: Configure, build and test (Windows)
        if: runner.os == 'Windows'
        shell: cmd
        run: scripts\ci.bat

      - name: Upload executable
        uses: actions/upload-artifact@v4
        with:
          name: hello-${{ matrix.os }}
          path: bin/
          if-no-files-found: error
````


## Verification
- `./scripts/ci.sh` ends with `== CI finished successfully`.
- `node scripts/check.mjs --static` passes all "GitHub Actions workflow" checks:
  triggers, three OSes, only CI scripts, no `secrets.`, no `continue-on-error`,
  exactly one job.
- After push: the Actions tab shows 3 green jobs
  `Build and test (ubuntu-latest|windows-latest|macos-latest)` and 3 artifacts
  `hello-<os>` containing the executable.

## Example
Input: default values.  
Expected job log tail (each OS):
```text
== Run executable
Hello, World!
== CI finished successfully
```

## Typical errors
| Code | Situation | Action |
|------|-----------|--------|
| `E-CI-PERM` | Linux job: `./scripts/ci.sh: Permission denied` | File was committed without the executable bit: `git update-index --chmod=+x scripts/ci.sh`. |
| `E-CI-CRLF` | `ci.sh` fails with `$'\r': command not found` | Line endings are CRLF; `.gitattributes` must contain `* text=auto eol=lf`. |
| `E-CI-LOCK` | `npm ci` → `package-lock.json` missing/out of sync | Run `npm install` locally and commit `package-lock.json`. |
| `E-CI-OS` | Matrix lacks an OS | Restore all three runners; `check` fails until fixed. |
