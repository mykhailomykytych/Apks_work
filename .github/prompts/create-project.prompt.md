---
agent: build-engineer
description: Create the initial Hello World project using skill project-scaffold.
---

# Command: create-project

Inputs: `language=${input:language:TypeScript}`, `projectName=${input:projectName:hello-world}`.

## Preconditions
- `git-init` has succeeded (`.gitignore` exists).

## Actions
1. Read `.github/skills/project-scaffold/SKILL.md` and follow its **Steps** with the inputs above.
2. Create only the files listed in the skill's **Outputs**; leave existing
   identical files unchanged.
3. Print the list of `created` / `updated` / `unchanged` files.

## Expected files
`src/hello.ts`, `src/greeting.ts`, `src/math.ts`, `.gitignore`, `.gitattributes`,
directories `tests/`, `scripts/`, `docs/`.

## Verification
- All expected files exist.
- `src/hello.ts` calls `console.log(greeting())`.
- `git check-ignore dist bin` prints both names.

## Error message
`create-project FAILED: <E-SCAFFOLD-... code>: <details>. Fix: <suggestion>`.
