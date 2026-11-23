// Packages dist/hello.js into a standalone executable bin/hello (bin/hello.exe on Windows)
// using Node.js Single Executable Applications (SEA). Works on Linux, macOS and Windows.
import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync, writeFileSync, chmodSync } from "node:fs";
import { createRequire } from "node:module";
import { join } from "node:path";

const require = createRequire(import.meta.url);
const { inject } = require("postject");

const isWin = process.platform === "win32";
const isMac = process.platform === "darwin";
const bundle = join("dist", "hello.js");
const buildDir = "build";
const binDir = "bin";
const blob = join(buildDir, "sea-prep.blob");
const exe = join(binDir, isWin ? "hello.exe" : "hello");

function step(msg) {
  console.log(`[package] ${msg}`);
}

if (!existsSync(bundle)) {
  console.error(`[package] ERROR: ${bundle} not found. Run "npm run build" first.`);
  process.exit(1);
}

mkdirSync(buildDir, { recursive: true });
mkdirSync(binDir, { recursive: true });

const seaConfig = join(buildDir, "sea-config.json");
writeFileSync(
  seaConfig,
  JSON.stringify({ main: bundle, output: blob, disableExperimentalSEAWarning: true }, null, 2),
);

step("generating SEA blob");
execFileSync(process.execPath, ["--experimental-sea-config", seaConfig], { stdio: "inherit" });

step(`copying node runtime to ${exe}`);
copyFileSync(process.execPath, exe);
if (!isWin) chmodSync(exe, 0o755);

if (isMac) {
  step("removing macOS signature");
  execFileSync("codesign", ["--remove-signature", exe], { stdio: "inherit" });
}

step("injecting application blob");
await inject(exe, "NODE_SEA_BLOB", readFileSync(blob), {
  sentinelFuse: "NODE_SEA_FUSE_fce680ab2cc467b6e072b8b5df1996b2",
  machoSegmentName: isMac ? "NODE_SEA" : undefined,
});

if (isMac) {
  step("ad-hoc signing for macOS");
  execFileSync("codesign", ["--sign", "-", exe], { stdio: "inherit" });
}

step(`verifying ${exe}`);
const out = execFileSync(exe, { encoding: "utf8" }).trim();
if (out !== "Hello, World!") {
  console.error(`[package] ERROR: unexpected output: "${out}"`);
  process.exit(1);
}
step(`OK: ${exe} prints "${out}"`);
