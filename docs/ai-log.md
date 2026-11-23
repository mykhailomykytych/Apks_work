# Журнал взаємодії з AI

Формат запису: дата · інструмент · запит · важлива відповідь · помилка/рішення.

## Сесія 1 — проєктування агента
| # | Запит | Результат / рішення |
|---|---|---|
| 1 | Проаналізувати методичку ЛР1 і визначити структуру агента для варіанту 6 (TypeScript, npm, Vitest) | Обрано формат GitHub Copilot: `.github/agents`, `.github/prompts`, `.github/skills`. 3 skills, 5 commands + orchestrator `init` |
| 2 | Створити manifest `build-engineer.agent.md` | Додано роль, параметри варіанту, межі відповідальності, правила, заборонені дії, критерії завершення |
| 3 | Створити skills з розділами «When to use / Inputs / Outputs / Steps / Verification / Example / Typical errors» | Шаблони файлів вбудовано в skills для відтворюваності результату |
| 4 | Створити commands з розділами «Preconditions / Actions / Expected files / Verification / Error message» | `init` викликає команди строго у порядку `git-init → create-project → create-build → create-actions → check` |

## Сесія 2 — генерація проєкту
| # | Запит | Результат / рішення |
|---|---|---|
| 5 | `npm install` з `vitest@^4.1.0` | **Помилка:** `npm error Cannot read properties of null (reading 'edgesOut')` (баг npm 10.9 при розв'язанні peer-залежностей Vitest 4). **Рішення:** використати `vitest@^3.2.4`; помилку описано у skill `build-and-test` як `E-BUILD-NPM-EDGES`, щоб агент не повторював її |
| 6 | Отримати виконуваний файл `hello` для TypeScript | Використано Node.js Single Executable Applications (`scripts/package.mjs` + `postject`); на macOS — зняття і повторне ad-hoc підписання |
| 7 | `ci.yml` має лише викликати скрипти збірки | Логіку винесено в `scripts/ci.sh` / `scripts/ci.bat`, workflow містить лише checkout, setup-node, виклик скрипта та завантаження артефакту |
| 8 | Команда `check` повинна бути детермінованою і не змінювати проєкт | Створено `scripts/check.mjs` (тільки читання файлів + build/test у git-ignored каталоги) |

## Сесія 3 — запуск агента в Copilot
> Заповнюється під час запуску `/init` у VS Code Copilot: скопіювати запити,
> ключові відповіді, помилки та виправлення.

| # | Запит | Результат / рішення |
|---|---|---|
| 9 | `/init` | … |
| 10 | `/check` після навмисного зламу `src/math.ts` | … |

## Докази перевірки
- Локально: `npm run check` → `CHECK PASSED`.
- GitHub Actions: посилання на успішний запуск для ubuntu/windows/macos — …
