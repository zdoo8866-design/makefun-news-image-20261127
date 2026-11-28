// Runner for the make.fun news-image entry (Friday 27 November 2026).
//
// The grader executes `node /bot/main.ts` with /bot mounted read-only, so
// this script must never write beside itself. All scratch work goes to the
// OS temp directory, and the finished page is copied to $MAKEFUN_OUTPUT_DIR
// (default /output).

import { execFileSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const scratch = join(tmpdir(), "makefun-entry-20261127.png");
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const target = join(outputDir, "entry.png");

// Re-render the page with the fresh compose.py. PYTHONDONTWRITEBYTECODE
// keeps Python from trying to drop __pycache__ next to the script.
execFileSync(
  "python3",
  [join(here, "tools", "compose.py"), scratch],
  {
    stdio: "inherit",
    env: { ...process.env, PYTHONDONTWRITEBYTECODE: "1" },
  },
);

if (!existsSync(scratch)) {
  throw new Error(`compose.py did not produce ${scratch}`);
}

mkdirSync(outputDir, { recursive: true });
copyFileSync(scratch, target);
console.log(`wrote ${target}`);
