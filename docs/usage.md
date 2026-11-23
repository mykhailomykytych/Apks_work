# Інструкція з використання

## Передумови
| Інструмент | Версія | Перевірка |
|---|---|---|
| Git | будь-яка актуальна | `git --version` |
| Node.js | 22 LTS або новіша | `node --version` |
| npm | 10+ | `npm --version` |
| VS Code + розширення GitHub Copilot (студентський план) | актуальна | Copilot Chat відповідає |

## 1. Запуск AI-агента
```bash
git clone <URL репозиторію>
cd <репозиторій>
git checkout develop
git checkout -b feature/lab1-hello-world
code .
```
У VS Code:
1. Відкрити **Copilot Chat** (`Ctrl+Alt+I`).
2. У випадаючому списку агентів обрати **build-engineer**
   (файл `.github/agents/build-engineer.agent.md`).
3. Запустити оркестратор: ввести `/init` і натиснути Enter.
   Copilot запитає `language` та `projectName` — залишити `TypeScript` і `hello-world`.
4. Підтверджувати запуск терміналу (`npm install`, `npm test` тощо), коли Copilot просить.
5. Очікуваний фінальний звіт:
   `init COMPLETED: 5/5 steps passed, check: CHECK PASSED, executable: bin/hello`.

Окремі команди можна запускати так само: `/git-init`, `/create-project`,
`/create-build`, `/create-actions`, `/check`.

> Якщо агент не з'являється у списку: VS Code → Settings → увімкнути
> `chat.promptFiles` та `chat.useAgentSkills`, перезапустити вікно.

## 2. Локальна перевірка
```bash
npm ci
npm run check          # read-only перевірка: агент, структура, build, тести, workflow
```
Очікуваний результат: `== Summary: N/N checks passed` та `CHECK PASSED`.

Тільки структура (без складання): `node scripts/check.mjs --static`.

## 3. Складання і запуск проєкту
```bash
npm run build          # dist/hello.js
npm start              # Hello, World!
npm test               # 3 тести, включно з BasicAddition
npm run package        # bin/hello (Linux/macOS) або bin\hello.exe (Windows)
./bin/hello            # Hello, World!
npm run clean          # видалити dist/, build/, bin/
```
Повний CI-сценарій:
```bash
./scripts/ci.sh        # Linux/macOS
scripts\ci.bat         # Windows
```

## 4. Демонстрація реакції на зламану перевірку
```bash
# зламати функцію
sed -i 's/a + b/a - b/' src/math.ts
npm run check          # FAIL npm test (Vitest) ... CHECK FAILED, exit code 1
git checkout -- src/math.ts
npm run check          # CHECK PASSED
```

## 5. GitHub Actions
Workflow `.github/workflows/ci.yml` запускається на `push` у `develop`,
`master`, `main`, `feature/**` і на `pull_request` у `develop`, `master`, `main`.
Результати: вкладка **Actions** → `CI` → 3 jobs (ubuntu, windows, macos),
артефакти `hello-<os>` з виконуваним файлом.
