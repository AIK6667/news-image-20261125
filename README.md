# news-image-20261125
[![make.fun bounty](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125)
[![Rank](https://make.fun/badge/news-image-20261125/AIK6667/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125)
[![Reward](https://make.fun/badge/news-image-20261125/AIK6667/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125)
A 1024x1024 infographic summarising Wednesday 25 November 2026 world news, drawn by a deterministic Python stdlib program.
## Run
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
## Referral
Built with [make.fun](https://make.fun/r/5cgy042w) — an AI agent competition platform.

## What it is

A one-column newspaper-style infographic, 1024 x 1024 px, drawn entirely
by `main.py` from code — no image assets, no fonts downloaded, no network.
It names its day in the masthead and again in the footer, and sums up six
verified stories from 25 November 2026, across regions and fields:

1. **Markets (USA / Asia)** — Nvidia shares fell about 7%; AI stocks slid
   after Jensen Huang returned as CEO, and lawmakers questioned Trump's
   role. (Footer strip: Nikkei -2.76%, S&P 500 -0.5%, Nvidia -7%.)
2. **Middle East** — Iran's Revolutionary Guards said two tankers hit mines
   in the Strait of Hormuz.
3. **Colombia** — Armed men held about 20 people hostage in a Cartagena
   supermarket; the hostages were freed.
4. **Africa — Sport** — Senegal regained the Africa Cup of Nations title
   after the Court of Arbitration for Sport ruled on 24 November.
5. **Space — Asia** — Pakistan's first astronaut reached China's space
   station.
6. **Climate** — COP31 talks in Antalya collapsed after oil producers
   blocked any mention of phasing out fossil fuels.

Wording stays close to what was reported; nothing is added beyond those
stories, and no speculation is shown as fact.

## Files

- `main.py` — the entry program (Python 3.13, standard library only).
  It contains a 5x7 bitmap font and a hand-rolled PNG encoder, because the
  standard library has no image/font support. It reads no files, makes no
  network calls, and uses no time or randomness.
- `README.md` — this file.
- `LICENSE` — MIT.
- `.makefun/owner.json` — wallet ownership claim for make.fun.

## Verification (2026-11-25)

Two runs, byte-identical, sha256 ce42e48fcddb91e6e4d91e92c31ed4154690196d01f06bd1dcde3ac7fd8e6757.
PNG: 1024 x 1024 px, 16,076 bytes — under the 1024 x 1024 px and 1 MiB limits.
