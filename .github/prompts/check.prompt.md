---
agent: build-engineer
description: Read-only verification of agent files, project structure, build, tests and the CI workflow. Does not modify the project.
---

# Command: check

This command **must not modify any tracked file**. It only reads files and runs
build/tests whose output goes to git-ignored directories.

## Preconditions
- Dependencies are installed (`node_modules/` exists); otherwise run `npm ci` first
  and say so in the report.

## Actions
1. Run `npm run check` (`node scripts/check.mjs`). It verifies:
   - the agent manifest (role, rules, forbidden actions, completion criteria);
   - every skill has purpose, inputs, outputs, steps, verification, example, errors;
   - every command has preconditions, actions, expected files, verification, error message;
   - `init` references the commands in the correct order;
   - project files, npm scripts, test `BasicAddition`, `.gitignore`;
   - workflow: triggers, matrix of three OSes, only CI scripts, no secrets, one job;
   - no build output or secrets are tracked by Git;
   - `npm run build`, `npm test` and the application output.
2. Run `git status --short` and confirm that no tracked file changed.
3. Report the summary line `N/M checks passed` and every failed check.

## Expected files
None are created or changed.

## Verification
Exit code of `npm run check` is 0 and the output ends with `CHECK PASSED`.

## Error message
`check FAILED: <K> of <M> checks failed:` followed by the list printed by
`scripts/check.mjs` (`- <check name>: <reason>`). Do not try to fix anything
inside this command; suggest which command (`create-project`, `create-build`,
`create-actions`) should be rerun.
