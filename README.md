# Лабораторна робота №1 — AI-агент для автоматизації розробки та CI/CD

| | |
|---|---|
| **Студент** | Микитич Михайло Васильович |
| **Група** | КІ-407 |
| **Варіант** | 6 (номер у списку 12): TypeScript · npm scripts · Vitest |

[![CI](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)

## Опис
Репозиторій містить AI-агента **build-engineer** для GitHub Copilot (VS Code),
який генерує, складає, тестує та налаштовує CI для кросплатформного
TypeScript-проєкту `Hello World`.

- Гілка `develop` — лише агент (manifest, skills, commands) та документація.
- Гілка `feature/lab1-hello-world` — повний результат роботи агента: вихідний код,
  тести, система складання, CI-скрипти та GitHub Actions.

## Структура агента
| Елемент | Файл |
|---|---|
| Agent manifest | `.github/agents/build-engineer.agent.md` |
| Skill `project-scaffold` | `.github/skills/project-scaffold/SKILL.md` |
| Skill `build-and-test` | `.github/skills/build-and-test/SKILL.md` |
| Skill `github-actions` | `.github/skills/github-actions/SKILL.md` |
| Commands | `.github/prompts/{git-init,create-project,create-build,create-actions,check}.prompt.md` |
| Orchestrator | `.github/prompts/init.prompt.md` |

## Запуск агента (коротко)
1. Відкрити репозиторій у VS Code з увімкненим GitHub Copilot.
2. Відкрити Copilot Chat, обрати агента **build-engineer**.
3. Ввести `/init` і дочекатися звіту `init COMPLETED`.

Детально — у [docs/usage.md](docs/usage.md). Архітектура — у
[docs/architecture.md](docs/architecture.md). Журнал роботи з AI —
[docs/ai-log.md](docs/ai-log.md).

## Запуск зібраного проєкту
```bash
npm ci
npm run build
npm start              # Hello, World!
npm test               # Vitest, включно з BasicAddition
npm run package        # створює виконуваний файл bin/hello (bin\hello.exe)
./bin/hello            # Hello, World!
```
Повний CI-сценарій локально: `./scripts/ci.sh` (Linux/macOS) або `scripts\ci.bat` (Windows).
