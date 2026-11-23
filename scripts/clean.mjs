// Removes git-ignored build output only (dist/, build/, bin/, coverage/).
import { rmSync } from "node:fs";

for (const dir of ["dist", "build", "bin", "coverage"]) {
  rmSync(dir, { recursive: true, force: true });
  console.log(`[clean] removed ${dir}/`);
}
