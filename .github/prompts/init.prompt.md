---
agent: build-engineer
description: Orchestrator - runs git-init, create-project, create-build, create-actions and check in order and stops at the first error.
---

# Command: init (orchestrator)

Inputs: `language=${input:language:TypeScript}`, `projectName=${input:projectName:hello-world}`.

## Preconditions
- `git`, Node.js >= 22 and npm are installed.
- The agent files exist: `.github/agents/build-engineer.agent.md`,
  `.github/skills/*/SKILL.md`, `.github/prompts/*.prompt.md`.

## Actions
Execute the following commands **strictly in this order**. Each step is
performed by reading the corresponding prompt file and following it exactly.

| # | Command | Prompt file | Passes to the next step |
|---|---------|-------------|-------------------------|
| 1 | `/git-init` | `.github/prompts/git-init.prompt.md` | repository is valid, `.gitignore` ready |
| 2 | `/create-project` | `.github/prompts/create-project.prompt.md` | `language`, `projectName`, list of source files |
| 3 | `/create-build` | `.github/prompts/create-build.prompt.md` | `package.json` scripts, test results |
| 4 | `/create-actions` | `.github/prompts/create-actions.prompt.md` | CI scripts and workflow path |
| 5 | `/check` | `.github/prompts/check.prompt.md` | final verdict |

Rules:
1. Before each step print `== init: step <n>/5 <command>`.
2. After each step print its verification result. If verification fails,
   **stop immediately**, do not run the remaining steps, and print the error
   message of that command.
3. The orchestrator is idempotent: files that already match the skill
   templates are left unchanged, so a second `init` run must end with no
   changes in `git status --short`.
4. Never report success if step 5 (`/check`) did not print `CHECK PASSED`.

## Expected files
Everything listed in the "Expected files" sections of the five commands.

## Verification
- `npm run check` → `CHECK PASSED`.
- `git status --short` lists only intended new/changed source files
  (no `node_modules/`, `dist/`, `build/`, `bin/`).

## Error message
`init STOPPED at step <n>/5 (<command>): <error message of the command>.`
Final report on success:
`init COMPLETED: 5/5 steps passed, check: CHECK PASSED, executable: bin/hello`.
