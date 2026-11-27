// Entry point for the news-image-20261127 submission.
//
// The deliverable is one PNG front page for Friday 27 November
// 2026. tools/compose.py (Pillow) draws the page; this script runs
// it into a scratch file, checks the result is a real PNG inside
// the intake limits (at most 1024x1024, at most 1 MiB), and only
// then copies it to /output/entry.png.
//
// The scratch file lives in the OS temp directory on purpose: the
// grading sandbox runs this script as node /bot/main.ts with /bot
// read-only, so any write next to the script exits 1 (that exact
// defect killed the 20261124 and 20261125 entries). /tmp is an
// allowed path per the competition RULES.txt.

import { spawnSync } from "node:child_process";
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const scratch = join(tmpdir(), "makefun-entry-20261127.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const outFile = join(outDir, "entry.png");

function die(msg: string): never {
  console.error("entry: " + msg);
  process.exit(1);
}

const run = spawnSync("python3", [join(here, "tools", "compose.py"), scratch], {
  stdio: "inherit",
});
if (run.status !== 0) die("composer exited with " + run.status);

const bytes = readFileSync(scratch);
const magic = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
if (!magic.every((b, i) => bytes[i] === b)) die("output is not a PNG");
if (bytes.length > 1_048_576) die("output exceeds 1 MiB: " + bytes.length);

const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  die(`output is ${width}x${height}, over the 1024 cap`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(scratch, outFile);
console.log(
  `entry: wrote ${outFile} (${width}x${height}, ${statSync(outFile).size} bytes)`,
);
