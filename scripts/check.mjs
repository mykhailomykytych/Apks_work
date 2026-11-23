// Read-only verification used by the `check` command.
// It never modifies tracked files: it only reads them and runs build/tests,
// whose output goes to git-ignored directories (dist/, build/, bin/).
//
// Usage:
//   node scripts/check.mjs            full check (structure + build + tests)
//   node scripts/check.mjs --static   structure only (no build, no tests)
import { execSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";

const staticOnly = process.argv.includes("--static");
const results = [];

function check(name, fn) {
  try {
    const detail = fn();
    if (detail === false) throw new Error("condition is false");
    results.push({ name, ok: true });
    console.log(`  PASS  ${name}`);
  } catch (err) {
    const message = String(err.message).split("\n")[0];
    results.push({ name, ok: false, error: message });
    console.log(`  FAIL  ${name}\n        -> ${message}`);
  }
}

function read(path) {
  if (!existsSync(path)) throw new Error(`missing file ${path}`);
  return readFileSync(path, "utf8");
}

function mustContain(path, needles) {
  const text = read(path);
  const missing = needles.filter((n) => !text.includes(n));
  if (missing.length) throw new Error(`${path} does not contain: ${missing.join(", ")}`);
}

const AGENT = ".github/agents/build-engineer.agent.md";
const SKILLS = ["project-scaffold", "build-and-test", "github-actions"];
const COMMANDS = ["git-init", "create-project", "create-build", "create-actions", "check", "init"];
const SKILL_SECTIONS = ["## When to use", "## Inputs", "## Outputs", "## Steps", "## Verification", "## Example", "## Typical errors"];
const COMMAND_SECTIONS = ["## Preconditions", "## Actions", "## Expected files", "## Verification", "## Error message"];

console.log("== Agent");
check("manifest exists", () => read(AGENT));
check("manifest has role, rules, forbidden actions, completion criteria", () =>
  mustContain(AGENT, ["## Role", "## Rules for working with files", "## Forbidden actions", "## Completion criteria"]),
);
for (const s of SKILLS) {
  check(`skill ${s} has purpose, inputs, outputs, verification`, () =>
    mustContain(`.github/skills/${s}/SKILL.md`, [`name: ${s}`, ...SKILL_SECTIONS]),
  );
}
for (const c of COMMANDS) {
  check(`command ${c} is defined`, () =>
    mustContain(`.github/prompts/${c}.prompt.md`, ["agent: build-engineer", "description:", ...COMMAND_SECTIONS]),
  );
}
check("init runs commands in the correct order", () => {
  const text = read(".github/prompts/init.prompt.md");
  const order = ["git-init", "create-project", "create-build", "create-actions", "check"].map((c) =>
    text.indexOf(`/${c}`),
  );
  if (order.some((i) => i < 0)) throw new Error("init does not reference all commands as /<command>");
  for (let i = 1; i < order.length; i++) {
    if (order[i] < order[i - 1]) throw new Error("commands are referenced out of order");
  }
});

console.log("== Project structure");
for (const f of [
  "README.md",
  ".gitignore",
  "package.json",
  "tsconfig.json",
  "vitest.config.ts",
  "src/hello.ts",
  "src/math.ts",
  "tests/math.test.ts",
  "scripts/ci.sh",
  "scripts/ci.bat",
  "scripts/package.mjs",
  "docs/architecture.md",
  "docs/usage.md",
  "docs/ai-log.md",
]) {
  check(`file ${f}`, () => read(f));
}
check("package.json has build/test/package/check scripts", () => {
  const pkg = JSON.parse(read("package.json"));
  const missing = ["build", "test", "package", "check"].filter((s) => !pkg.scripts?.[s]);
  if (missing.length) throw new Error(`missing scripts: ${missing.join(", ")}`);
});
check("test BasicAddition exists", () => mustContain("tests/math.test.ts", ['"BasicAddition"']));
check(".gitignore excludes build output and secrets", () =>
  mustContain(".gitignore", ["node_modules/", "dist/", "build/", "bin/", ".env"]),
);

console.log("== GitHub Actions workflow");
const WF = ".github/workflows/ci.yml";
check("workflow has push and pull_request triggers", () => mustContain(WF, ["push:", "pull_request:", "develop", "master"]));
check("workflow matrix has Windows, Linux and macOS", () =>
  mustContain(WF, ["matrix:", "ubuntu-latest", "windows-latest", "macos-latest"]),
);
check("workflow only calls CI scripts", () => mustContain(WF, ["scripts/ci.sh", "scripts\\ci.bat"]));
check("workflow has no secrets and does not hide failures", () => {
  const text = read(WF);
  for (const bad of ["secrets.", "continue-on-error: true", "|| true"]) {
    if (text.includes(bad)) throw new Error(`forbidden pattern "${bad}"`);
  }
});
check("workflow has exactly one job", () => {
  const text = read(WF);
  const jobs = text.split("\njobs:\n")[1] ?? "";
  const names = jobs.split("\n").filter((l) => /^  [A-Za-z0-9_-]+:\s*$/.test(l));
  if (names.length !== 1) throw new Error(`expected 1 job, found ${names.length}`);
});

console.log("== Git");
check("no build output or secrets tracked by git", () => {
  let files;
  try {
    files = execSync("git ls-files", { encoding: "utf8" }).split("\n");
  } catch {
    throw new Error("not a git repository");
  }
  const bad = files.filter((f) => /^(node_modules|dist|build|bin|coverage)\//.test(f) || /(^|\/)\.env/.test(f));
  if (bad.length) throw new Error(`tracked: ${bad.slice(0, 5).join(", ")}`);
});

if (!staticOnly) {
  console.log("== Build and tests");
  check("npm run build", () => execSync("npm run build", { stdio: "pipe" }));
  check("npm test (Vitest)", () => {
    const out = execSync("npm test", { encoding: "utf8", stdio: "pipe" });
    if (!out.includes("BasicAddition")) throw new Error("BasicAddition was not executed");
  });
  check("application prints Hello, World!", () => {
    const out = execSync("node dist/hello.js", { encoding: "utf8" }).trim();
    if (out !== "Hello, World!") throw new Error(`unexpected output "${out}"`);
  });
}

const failed = results.filter((r) => !r.ok);
console.log(`\n== Summary: ${results.length - failed.length}/${results.length} checks passed`);
if (failed.length) {
  console.log("CHECK FAILED:");
  for (const f of failed) console.log(`  - ${f.name}: ${f.error}`);
  process.exit(1);
}
console.log("CHECK PASSED");
