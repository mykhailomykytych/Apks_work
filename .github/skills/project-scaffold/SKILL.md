---
name: project-scaffold
description: Create the minimal Hello World project structure (sources, README, .gitignore) for a given language and project name. Use from the create-project command.
---

# Skill: project-scaffold

## When to use
- The repository has no application sources yet (`src/hello.ts` is missing), or
- the user runs `/create-project`, or the `init` orchestrator reaches step 2.

Do **not** use it to change build or CI configuration — that belongs to
`build-and-test` and `github-actions`.

## Inputs
| Input | Default | Description |
|-------|---------|-------------|
| `language` | `TypeScript` | Only TypeScript is supported by this agent (variant 6). Any other value → stop with an error. |
| `projectName` | `hello-world` | Used in `README.md` and `package.json` `name`. Lowercase, `[a-z0-9-]`. |

## Outputs
| File | Purpose |
|------|---------|
| `src/greeting.ts` | Pure function `greeting(name = "World")` returning `Hello, <name>!` |
| `src/hello.ts` | Entry point; prints `greeting()` |
| `src/math.ts` | Function `add(a, b)` used by the unit test `BasicAddition` |
| `README.md` | Project description; only a section is added if the file exists |
| `.gitignore` | Ignores `node_modules/`, `dist/`, `build/`, `bin/`, `coverage/`, logs, `.env*`, keys |
| `.gitattributes` | LF for all files, CRLF for `*.bat` |
| `tests/`, `scripts/`, `docs/` | Empty directories are created if missing |

## Steps
1. Validate inputs. If `language` is not `TypeScript` → error `E-SCAFFOLD-LANG`.
2. Create directories `src/`, `tests/`, `scripts/`, `docs/` if they do not exist.
3. For each file in **Templates** below: if the file does not exist, create it
   with exactly the template content. If it exists and already contains the
   template content, leave it untouched. If it exists with different content,
   show a diff and ask the user before changing it.
4. `.gitignore`: append only the lines from the template that are missing
   (never duplicate lines).
5. `README.md`: if it already exists, keep the user's content (name, group,
   variant) and only add missing sections.

## Templates
#### `src/greeting.ts`
````ts
/**
 * Builds the greeting printed by the application.
 */
export function greeting(name: string = "World"): string {
  return `Hello, ${name}!`;
}
````

#### `src/hello.ts`
````ts
import { greeting } from "./greeting";

/**
 * Entry point of the `hello` executable.
 * Prints "Hello, World!" to standard output.
 */
console.log(greeting());
````

#### `src/math.ts`
````ts
/**
 * Adds two numbers.
 * Used by the unit test `BasicAddition`.
 */
export function add(a: number, b: number): number {
  return a + b;
}
````

#### `.gitignore`
````gitignore
# Dependencies
node_modules/

# Build output
dist/
build/
bin/
*.blob
coverage/

# Logs and local run results
*.log
npm-debug.log*
.vitest/

# Secrets
.env
.env.*
*.pem
*.key

# OS / editor
.DS_Store
Thumbs.db
.vscode/*
!.vscode/extensions.json
````

#### `.gitattributes`
````text
* text=auto eol=lf
*.bat text eol=crlf
````


## Verification
- `src/hello.ts`, `src/greeting.ts`, `src/math.ts` exist.
- The run command is defined: `src/hello.ts` imports `./greeting` and calls
  `console.log(greeting())`; after `create-build`, `npm run build && npm start`
  prints `Hello, World!`.
- `git check-ignore node_modules dist bin build` prints all four names.

## Example
Input: `language=TypeScript`, `projectName=hello-world`  
Result:
```text
created src/greeting.ts
created src/hello.ts
created src/math.ts
updated .gitignore (+12 lines)
created .gitattributes
unchanged README.md (sections present)
```
Second run of the same input: every file is reported as `unchanged`.

## Typical errors
| Code | Situation | Action |
|------|-----------|--------|
| `E-SCAFFOLD-LANG` | `language=Python` was passed | Stop: "project-scaffold supports only TypeScript (variant 6)". |
| `E-SCAFFOLD-CONFLICT` | `src/hello.ts` exists with other content | Show diff, ask the user; do not overwrite silently. |
| `E-SCAFFOLD-GITIGNORE` | `git check-ignore dist` prints nothing | `.gitignore` was not saved or is in the wrong directory; recreate it in the repository root. |
