---
agent: build-engineer
description: Create scripts/ci.sh, scripts/ci.bat and the GitHub Actions workflow using skill github-actions.
---

# Command: create-actions

## Preconditions
- `create-build` has succeeded (`npm test` passes locally).

## Actions
1. Read `.github/skills/github-actions/SKILL.md` and follow its **Steps**.
2. Create `scripts/ci.sh` (executable), `scripts/ci.bat` (CRLF),
   `.github/workflows/ci.yml` (one job, matrix of three OSes, calls only the CI scripts).
3. Run the CI script for the current OS locally.
4. Run `node scripts/check.mjs --static`.

Never put secrets in the workflow, never use `continue-on-error: true`.

## Expected files
`scripts/ci.sh`, `scripts/ci.bat`, `.github/workflows/ci.yml`.

## Verification
- Local CI script ends with `== CI finished successfully`.
- `node scripts/check.mjs --static` → `CHECK PASSED`.

## Error message
`create-actions FAILED: <E-CI-... code>: <details>. Fix: <suggestion>`.
