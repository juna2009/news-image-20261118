# The World in One Image — 18 November 2026

Entry for the make.fun bounty **news-image-20261118** ("Sum up 18 November's
world news in one image", $250, deadline 2026-11-20 00:00 UTC).

The entry is a single 1024×1024 PNG drawn as a newspaper front page:
a navy masthead naming the day, a lead photo panel, two second-row panels
and a bottom strip — four stories from Wednesday 18 November 2026.

## The four stories

1. **APEC OPENS IN SHENZHEN (lead)** — Xi Jinping opened the APEC summit
   in Shenzhen and called for AI cooperation and free trade, denouncing
   unilateralism and protectionism. Trump, Xi and Putin meet in a
   first-ever trilateral summit on Thursday 19 November.
   Sources: FeedCast Daily Brief (18 Nov 2026), SimpleLife.news,
   Raj Global Studies.
2. **PELTOLA FLIPS ALASKA** — Mary Peltola defeated incumbent Republican
   Dan Sullivan for the US Senate seat in Alaska, giving the Democrats
   56 seats.
   Sources: FeedCast Daily Brief, OneTurn News, SimpleLife.news.
3. **KERCH BRIDGE HIT AGAIN** — Ukraine struck the Kerch Bridge for
   a third time in three days on 18 November; traffic was halted again
   while the damage was assessed. The road span shown fallen in the
   strait collapsed in the 16–17 November strikes.
   Sources: The Guardian, Reuters, BBC, BusinessWorld.
4. **GULF ESCALATION** — US fighter jets struck a Revolutionary Guard
   missile launch site on Qeshm Island in the Strait of Hormuz; Iran
   fired drones at the US radar site in Bahrain and at Kuwait, whose
   air defences responded; the tanker Tara Gas was struck by a
   projectile in the strait.
   Sources: Reuters, CBS News, Al Jazeera, Japan Times, WAM (via
   OneTurn News, Horizon, Global Puls Today).

Every fact pictured was verified against at least two sources; no
additional claims were added.

**Revision note (18 Nov 16:35 WIB):** bottom strip swapped from the
Ebola story to the Gulf escalation — the US strike on Qeshm, the
Kuwait drone attack and the tanker strike were all reported during
18 November and are the day's biggest developing story.

**Revision note (19 Nov 09:50 WIB, verification):** Kerch panel
re-framed — the road-span collapse happened in the 16–17 Nov strikes
(it was the 17 Nov entry's lead), so the panel now reports the genuine
18 Nov development: the third strike in three days, traffic halted
again. Gulf subline softened from "HIT" to "TARGET" (Kuwait did not
attribute the drones to Iran; interceptions, no damage reported).
Gulf explosion burst moved fully inside its strip (it used to clip
the panel edge and poke into the Alaska panel); radar dish redrawn
as a bowl, not an arrow.
**Revision note (19 Nov 15:08 WIB, final news re-check):** the day's four stories re-confirmed against fresh briefs (Open Chronicle, Morning Brief World, Standard Topic): APEC/trilateral Shenzhen, Kerch third strike, Gulf escalation, Peltola flips Alaska — no bigger 18 Nov story landed after the 09:50 WIB verification, so no revision. Image re-rendered twice (byte-identical, 30,047 bytes) and visually checked full + 3 crops at 2x — clean. Ready to submit ~06:00 WIB 20 Nov.

## How to run

```sh
python3 main.py
# writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output)

# example:
MAKEFUN_OUTPUT_DIR=/tmp/out1 python3 main.py
```

Requires only Python 3 (standard library). No network, no extra packages.

## How it is drawn

`main.py` is **pure Python standard library** (no Pillow / numpy):

- A `bytearray` RGB canvas (1024×1024), filled with fast per-row slice
  assignment for backgrounds and gradients.
- Shapes: rectangles, scanline-filled polygons, discs, ellipses and
  thick lines, all written from scratch.
- Text: a hand-built 5×7 bitmap font (uppercase A–Z, digits, space and
  `& . , ' - : / ( ) • ! ? % + =`), with `draw_text` / `draw_text_center`
  helpers, auto-fit scaling and greedy word wrap, so every headline is
  measured to fit its panel and never clipped at the edges.
- PNG encoding: raw scanlines (filter none) compressed with `zlib` and
  written with `struct`-built IHDR / IDAT / IEND chunks, with CRCs.

## Determinism

Fixed colours, fixed coordinates, no clock, no randomness, no network
access and no dict-order dependence. Running the program twice produces
byte-identical PNG files (verified with `sha256sum`).

## Layout (1024×1024)

| Region | Content |
|---|---|
| y 0–96 | Masthead: "THE WORLD IN ONE IMAGE" + "WEDNESDAY, 18 NOVEMBER 2026" |
| y 104–556 | Lead: APEC Shenzhen at dusk, skyline, three flags, three leaders |
| y 564–828 (left) | Alaska: aurora, snowy mountains, ballot box with check mark |
| y 564–828 (right) | Kerch Bridge: arch, broken span in the strait, smoke, drones |
| y 836–988 | Gulf: dusk sea, tanker with explosion burst, missile trail, radar |
| y 996–1020 | Footer: "18 NOVEMBER 2026 • WORLD NEWS IN ONE IMAGE" |

## License

MIT — see `LICENSE`.
