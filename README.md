# The World in One Day — 27 November 2026

Entry for the make.fun competition
[`news-image-20261127`](https://make.fun/bounty/news-image-20261127):
sum up 27 November's world news in one image.

## The page

A single 1024×1024 front page, drawn entirely in code with Pillow —
no photographs, no outside assets. 36 stories, all of which happened
or were first reported on Friday 27 November 2026:

- **Masthead + standfirst** — Friday 27 November 2026.
- **Region bar** — Americas 10 · Asia 10 · Europe 9 · Middle East 3 ·
  Oceania 3 · Global 1.
- **The day in numbers** — 724,000 without power · 400 flights
  cancelled · 65 seats a side in a hung House · 164 rescued in Delhi ·
  2.9% Tokyo inflation · 248 files in the USAID dump.
- **13 drawn cards** — Wellington (NZ hung at 65–65), New York
  (Thanksgiving storm), New Delhi (cyber-slavery bust), Hormuz,
  Kyiv, Tokyo, Buenos Aires, Berlin, Brussels, Minneapolis, Seoul,
  Christchurch, Geneva — each with a small spot illustration.
- **World map** with numbered pins 1–13 matching the cards.
- **23 more stories** in the briefs block.
- **DATE CHECK box** — the Thursday stories the wires repeated today
  (Kuwait drone deaths, UK migration 77,000, ECB chief, Ibiza tanker,
  Florida flood aid, Macy's parade) are listed as NOT FRIDAY, so the
  page only claims Friday's news.

## How it runs

```
node main.ts
```

`main.ts` runs `tools/compose.py` into a scratch file in the OS temp
directory, checks the result is a PNG within the intake limits
(≤1024×1024, ≤1 MiB), and copies it to `$MAKEFUN_OUTPUT_DIR`
(default `/output`). The scratch file deliberately does **not** go
next to the script: the grading sandbox runs this as `node
/bot/main.ts` with `/bot` read-only, and writing beside the script
exits 1 — that exact defect rejected the 20261124 and 20261125
entries. Output is deterministic: two runs produce byte-identical
PNGs (sha256 `a24087a910e02497a5101ab35fdd4cff9eb650e3904bb2c8a25d4bbc1e961f57`).

## Files

- `main.ts` — entry point, runs the composer and validates the PNG.
- `tools/compose.py` — draws the whole page with Pillow.
- `tools/worldmap_data.py` — schematic continent outlines + islands.
- `entry.png` — the rendered front page (1024×1024, 203,322 bytes).
