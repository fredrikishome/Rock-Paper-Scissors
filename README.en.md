# ✊ ✌️ ✋ Rock, Paper, Scissors — Agent + Agent (English)

Two autonomous agents — **Donald 🧨** and **Oskar 🌊** — play rock, paper,
scissors against each other, with live visualization in both the terminal
(CLI) and the browser. Swedish is the primary language; this document is the
English overview.

> 🇸🇪 Swedish README: [README.md](README.md)
> Full development history / prompt summary: [docs/PROMPT_HISTORY.md](docs/PROMPT_HISTORY.md)

## Contents

| File | Description |
|---|---|
| `rps_cli.py` | **Dashboard CLI** — live terminal interface with panels, AI commentary and stats |
| `rps_cli_classic.py` | **Classic CLI** — simple list style, one line per round |
| `index.html` | **Web dashboard** — standalone page (open in any browser) with an animated duel line |
| `data/match_100.json` | Reference data from a simulated 100-round match |
| `docs/PROMPT_HISTORY.md` | Collected prompt summary: how the project was built step by step |
| `.github/workflows/smoke.yml` | CI smoke tests (CLI on Linux + Windows, web data validation) |

## The agents

### Donald 🧨 — "The random player"
Plays uniformly at random. Unpredictable in theory — but since he never adapts,
his habits (e.g. repeated moves) can be exploited.

### Oskar 🌊 — "The pattern reader"
A simple adaptive strategy:
1. If the opponent has **played the same move twice in a row**, Oskar predicts
   the next move and plays whatever beats it.
2. Otherwise he plays at random.

In a 100-round match this gives Oskar a small but steady edge, and it skews
the "best move" statistics toward whatever counters Donald's favourite move.

## Getting started

```bash
# Dashboard CLI
python rps_cli.py                  # 100 rounds, live dashboard
python rps_cli.py --rounds 20 --delay 0.2 --seed 42
python rps_cli.py --final-only     # show only the final dashboard

# Classic CLI
python rps_cli_classic.py --rounds 100

# Web dashboard: just open index.html in a browser — no server needed
```

> Tip: run the CLI in Windows Terminal, PowerShell 7+, iTerm2 or another modern
> terminal for full color and emoji support. Requires Python 3.10+, no external packages.

## Web dashboard features

- **Duel line** between the agents: one glowing arrow is fired per round from
  the loser to the winner — the direction flips with every round
- **VS badge** shows who won the latest round (`D +1` / `O +1`, `=` on draws)
- **Hands** above each agent avatar show what they played
- **Balance marker** that slides toward the overall match leader
- AI panel with pattern detection (hit ✔ / miss ✘) and a confidence meter
- Statistics: win flow per move, 20-round trend strip, and which move was the
  **best outcome** (most rounds won)
- Controls: ▶/⏸ pause, ⟲ replay, speed 0.5×–4×

## Statistics methodology

After every match we report the final score, draws, each agent's move
distribution, and wins per move ("best outcome"). Important: in a symmetric
game no move is objectively better (theoretical 33.3 % each). A move
"winning" the stats in a single match is a sampling artifact driven by luck
and the opponent's move distribution — with enough rounds everything
converges toward 33/33/33.

## License

MIT — see [LICENSE](LICENSE).
