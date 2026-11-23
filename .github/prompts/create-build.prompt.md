---
agent: build-engineer
description: Create the build configuration, unit tests and executable packaging using skill build-and-test, then build and test.
---

# Command: create-build

## Preconditions
- `create-project` has succeeded (`src/hello.ts`, `src/math.ts` exist).
- Node.js >= 22 and npm are available (`node --version`, `npm --version`).

## Actions
1. Read `.github/skills/build-and-test/SKILL.md` and follow its **Steps**
   (`build-config` → `unit-tests` → `packaging` → `run`).
2. Merge into an existing `package.json` instead of overwriting it; do not
   duplicate scripts or dependencies.
3. Run `npm install`, `npm run build`, `npm test`, `npm run package`.
4. Run the executable `./bin/hello` (Windows: `bin\hello.exe`).

## Expected files
`package.json`, `package-lock.json`, `tsconfig.json`, `vitest.config.ts`,
`tests/math.test.ts`, `tests/greeting.test.ts`, `scripts/package.mjs`,
`scripts/clean.mjs`, `scripts/check.mjs`.
Ignored build output: `dist/hello.js`, `bin/hello[.exe]`.

## Verification
```bash
npm run build && npm test && npm run package && ./bin/hello
```
The output must contain `BasicAddition` (passed) and `Hello, World!`.

## Error message
`create-build FAILED: <E-BUILD-... / E-TEST-... code>: <command> exited with <code>. Output: <last lines>. Fix: <suggestion>`.
