---
agent: build-engineer
description: Check the Git repository, create or update .gitignore and show the Git state (no commits, no pushes).
---

# Command: git-init

## Preconditions
- `git` is installed (`git --version`).
- The workspace root is the repository root.

## Actions
1. Run `git rev-parse --is-inside-work-tree`. If it fails, run `git init -b develop`
   (only in an empty, non-git folder) and tell the user.
2. Show the current branch: `git branch --show-current`.
3. Create `.gitignore` from the template of skill `project-scaffold`
   (`.github/skills/project-scaffold/SKILL.md`). If it exists, append only
   missing lines; never duplicate lines.
4. Create `.gitattributes` (`* text=auto eol=lf`, `*.bat text eol=crlf`) if missing.
5. Show `git status --short`.

Do not commit, push, change remotes or rewrite history.

## Expected files
- `.gitignore` (contains `node_modules/`, `dist/`, `build/`, `bin/`, `.env`)
- `.gitattributes`

## Verification
```bash
git rev-parse --is-inside-work-tree   # true
git check-ignore node_modules dist build bin
git status --short
```

## Error message
`git-init FAILED: <step>: <command output>. Fix: <suggestion>` — for example
`git-init FAILED: step 1: not a git repository and folder is not empty. Fix: clone the repository or run git init manually.`
