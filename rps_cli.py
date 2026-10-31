#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sten, Sax, Påse — Donald vs Oskar
Dashboard-stilad CLI: två agenter som spelar medan du tittar på live.

Användning:
    python rps_cli.py                  # 100 omgångar, live-dashboard
    python rps_cli.py --rounds 20      # kortare match
    python rps_cli.py --delay 0        # utan paus mellan omgångar
    python rps_cli.py --seed 42        # reproducerbar match
    python rps_cli.py --final-only     # visa bara slutresultatet
"""

import argparse
import os
import random
import re
import sys
import time

if os.name == "nt":
    os.system("")  # aktivera ANSI-färger i Windows-konsolen
for _stream in (sys.stdout, sys.stderr):
    _stream.reconfigure(encoding="utf-8", errors="replace")

MOVES = ["Sten", "Sax", "Påse"]
EMOJI = {"Sten": "✊", "Sax": "✌️", "Påse": "✋"}
BEATS = {"Sten": "Sax", "Sax": "Påse", "Påse": "Sten"}  # nyckeln slår värdet

# --------------------------------------------------------------------------
# Färger (mörkblå dashboard-tema)
# --------------------------------------------------------------------------
RESET, BOLD, DIM, ITAL = "\033[0m", "\033[1m", "\033[2m", "\033[3m"
ORANGE = "\033[38;5;209m"
CYAN = "\033[96m"
BLUE = "\033[38;5;75m"
GREY = "\033[38;5;245m"
GOLD = "\033[33m"
GREEN = "\033[92m"
RED = "\033[91m"
BORDER_D = "\033[38;5;130m"   # varm orange-brun ram för Donald
BORDER_O = "\033[38;5;39m"    # cyan-blå ram för Oskar
BORDER_C = "\033[38;5;68m"    # stålblå ram för mitten
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _scan(s: str):
    """Yieldar (tecken, bredd) och hoppar över ANSI-sekvenser (bredd 0,
    men returnerade orörda i strömmen)."""
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\x1b":
            m = ANSI_RE.match(s, i)
            if m:
                yield (m.group(0), 0)
                i = m.end()
                continue
        o = ord(ch)
        if o == 0xFE0F:
            i += 1
            continue
        w = 2 if (0x2600 <= o <= 0x32FF or o >= 0x1F000) else 1
        yield (ch, w)
        i += 1


def vwidth(s: str) -> int:
    """Visuell bredd: emoji räknas som 2 tecken, ANSI-koder som 0."""
    return sum(w for _, w in _scan(s))


def pad(s: str, width: int) -> str:
    gap = width - vwidth(s)
    return s + (" " * gap if gap > 0 else "")


def clip(s: str, width: int) -> str:
    out, w = "", 0
    for ch, cw in _scan(s):
        if w + cw > width:
            break
        out += ch
        w += cw
    return out


# --------------------------------------------------------------------------
# Agenterna
# --------------------------------------------------------------------------
class Agent:
    def __init__(self, name: str, seed: int | None = None):
        self.name = name
        self.rng = random.Random(seed)
        self.score = 0
        self.history: list[str] = []
        self.results: list[str] = []  # "W", "L", "D"

    def choose_move(self) -> str:
        raise NotImplementedError

    def notify_result(self, my_move: str, result: str) -> None:
        self.history.append(my_move)
        self.results.append(result)
        if result == "W":
            self.score += 1


class Donald(Agent):
    """Donald: spelar totalt slumpt — oförutsägbar men utan plan."""

    def choose_move(self) -> str:
        return self.rng.choice(MOVES)


class Oskar(Agent):
    """Oskar: lär av mönstret. Upprepar motståndaren ett drag två gånger i rad
    spår han nästa drag och spelar det som slår det — annars slumpt."""

    def __init__(self, name: str, opponent: Agent, seed: int | None = None):
        super().__init__(name, seed)
        self.opponent = opponent

    def detect_repeat(self) -> str | None:
        hist = self.opponent.history
        if len(hist) >= 2 and hist[-1] == hist[-2]:
            return hist[-1]
        return None

    def choose_move(self) -> str:
        predicted = self.detect_repeat()
        if predicted:
            return next(m for m, b in BEATS.items() if b == predicted)
        return self.rng.choice(MOVES)


# --------------------------------------------------------------------------
# Spelledaren
# --------------------------------------------------------------------------
class MatchReferee:
    def __init__(self, agent_a: Agent, agent_b: Agent):
        self.agent_a = agent_a
        self.agent_b = agent_b
        self.draws = 0
        self.move_wins = {m: 0 for m in MOVES}

    def play_round(self) -> tuple[str, str, str]:
        move_a = self.agent_a.choose_move()
        move_b = self.agent_b.choose_move()

        if move_a == move_b:
            self.draws += 1
            winner = "Oavgjort"
            self.agent_a.notify_result(move_a, "D")
            self.agent_b.notify_result(move_b, "D")
        elif BEATS[move_a] == move_b:
            winner = self.agent_a.name
            self.move_wins[move_a] += 1
            self.agent_a.notify_result(move_a, "W")
            self.agent_b.notify_result(move_b, "L")
        else:
            winner = self.agent_b.name
            self.move_wins[move_b] += 1
            self.agent_a.notify_result(move_a, "L")
            self.agent_b.notify_result(move_b, "W")
        return move_a, move_b, winner


# --------------------------------------------------------------------------
# Dashboard-rendering
# --------------------------------------------------------------------------
WIDTH = 78
PANEL_W = 24
CENTER_W = 26
PANEL_H = 17  # antal innehållsrader


def panel(title: str, lines: list[str], width: int, height: int, border: str) -> list[str]:
    inner = width - 2
    title_s = f" {title} "
    rest = max(inner - vwidth(title_s) - 2, 0)
    rows = [border + "╭─" + BOLD + title_s + RESET + border + "─" * rest + "╮" + RESET]
    for i in range(height):
        content = lines[i] if i < len(lines) else ""
        rows.append(border + "│" + RESET + " " + pad(clip(content, inner - 2), inner - 2)
                    + " " + border + "│" + RESET)
    rows.append(border + "╰" + "─" * inner + "╯" + RESET)
    return rows


def merge_rows(a: list[str], b: list[str], c: list[str]) -> list[str]:
    return [x + "  " + y + "  " + z for x, y, z in zip(a, b, c)]


def donald_panel(d: Agent, last_round: int) -> list[str]:
    lines = [
        GREY + ITAL + "Strategi: ren slumpt" + RESET,
        "",
        BLUE + "import random" + RESET,
        BLUE + "def donald(n):" + RESET,
        BLUE + '  return random' + RESET,
        BLUE + '    .choice(MOVES)' + RESET,
        "",
        BOLD + "SENASTE DRAG:" + RESET,
    ]
    start = max(0, len(d.history) - 6)
    for i in range(start, len(d.history)):
        n = start + i + 1
        m = d.history[i]
        res = d.results[i]
        tag = (GREEN + "VINST" + RESET if res == "W"
               else RED + "FÖRLUST" + RESET if res == "L"
               else GREY + "LIKA" + RESET)
        lines.append(f"{GREY}r{n:03d}{RESET} {EMOJI[m]} {m:<6} {tag}")
    return lines


def oskar_panel(o: Oskar, last_round: int) -> list[str]:
    predicted = o.detect_repeat()
    counter = None
    if predicted:
        counter = next(m for m, b in BEATS.items() if b == predicted)

    decisive = o.score + sum(1 for r in o.results if r == "L")
    wins = o.score
    conf = round(wins / decisive * 100) if decisive else 0
    conf_bar = "█" * (conf // 10) + "░" * (10 - conf // 10)

    lines = [
        GREY + ITAL + "AI-läge: analyserar mönster" + RESET,
        "",
        CYAN + "Jag analyserar" + RESET,
        CYAN + "dina senaste drag" + RESET,
        CYAN + "och hittar mönster:" + RESET,
        "",
    ]
    if predicted:
        lines += [
            f"{GOLD}MÖNSTER ▸ du upprepar" + RESET,
            f"{GOLD}{EMOJI[predicted]} {predicted}{RESET}",
            f"{BOLD}MOTDRAG: {EMOJI[counter]} {counter}{RESET}",
        ]
    else:
        lines += [
            GREY + "Inget stabilt mönster" + RESET,
            GREY + "detekterat just nu." + RESET,
            GREY + "Slumpt-läge aktivt." + RESET,
        ]
    lines += [
        "",
        f"FÖRTROENDE {CYAN}{conf_bar}{RESET} {conf}%",
        GREEN + "AUTO-KORRIGERING: PÅ" + RESET,
    ]
    return lines


def center_panel(n: int, total: int, d: Agent, o: Agent, last: tuple | None,
                 move_wins: dict, draws: int) -> list[str]:
    lines = []
    if last:
        dm, om, winner = last
        lines.append(f"{GREY}OMGÅNG {n}/{total}{RESET}")
        lines.append("")
        lines.append(f"{ORANGE}{BOLD}{EMOJI[dm]} {dm:<6}{RESET}")
        lines.append(f"{GREY}   mot{RESET}")
        lines.append(f"{CYAN}{BOLD}{EMOJI[om]} {om:<6}{RESET}")
        lines.append("")
        if winner == "Donald":
            lines.append(f"{ORANGE}{BOLD}▸ DONALD +1{RESET}")
        elif winner == "Oskar":
            lines.append(f"{CYAN}{BOLD}▸ OSKAR +1{RESET}")
        else:
            lines.append(GREY + "▸ LIKA — ingen poäng" + RESET)
    else:
        lines += [GREY + "Väntar på första" + RESET, GREY + "omgången ..." + RESET]
    lines.append("")
    lines.append(BOLD + "── STÄLLNING ──" + RESET)
    lines.append(f"{ORANGE}{BOLD}{d.score:>3}{RESET} {GREY}·{RESET} "
                 f"{CYAN}{BOLD}{o.score:<3}{RESET}")
    lines.append("")
    lines.append(BOLD + "VINSTFLÖDE PER VAL" + RESET)
    mx = max(max(move_wins.values()), 1)
    for m in MOVES:
        w = move_wins[m]
        col = {"Sten": GOLD, "Sax": CYAN, "Påse": ORANGE}[m]
        bar = "█" * int(w / mx * 14) + "░" * (14 - int(w / mx * 14))
        lines.append(f"{EMOJI[m]} {m:<6}{col}{bar}{RESET} {w}")
    return lines


def header(total: int) -> list[str]:
    t1 = "Sten + Sax + Påse.  Agent + Agent."
    t2 = f"SPELAR TILLSAMMANS · {total} OMGÅNGAR"
    left = BOLD + "🧠 DONALD-GRÄNSSNITT +" + RESET
    right = BOLD + "🤖 OSKAR-AI-GRÄNSSNITT +" + RESET
    mid = WIDTH - vwidth(left) - vwidth(right) - 4
    return [
        BLUE + "═" * WIDTH + RESET,
        left + " " * max(mid, 2) + right,
        pad(clip(f"{BOLD}{t1}{RESET}", WIDTH), WIDTH),
        pad(clip(f"{GREY}{t2}{RESET}", WIDTH), WIDTH),
        BLUE + "═" * WIDTH + RESET,
    ]


def stat_boxes(n: int, d: Agent, o: Agent, draws: int, results: list[str]) -> list[str]:
    specs = [
        ("TOTALT", str(n), GOLD),
        ("DONALD", str(d.score), ORANGE),
        ("OSKAR", str(o.score), CYAN),
        ("OAVGJORT", str(draws), GREY),
    ]
    bw = (WIDTH - 3 * 2) // 4
    top = "  ".join(BLUE + "┌" + "─" * (bw - 2) + "┐" + RESET for _ in specs)
    mid_l, mid_r = [], []
    for title, val, col in specs:
        mid_l.append(BLUE + "│" + RESET + pad(GREY + title + RESET, bw - 2) + BLUE + "│" + RESET)
        mid_r.append(BLUE + "│" + RESET + pad(col + BOLD + val + RESET, bw - 2) + BLUE + "│" + RESET)
    bot = "  ".join(BLUE + "└" + "─" * (bw - 2) + "┘" + RESET for _ in specs)
    return [top, "  ".join(mid_l), "  ".join(mid_r), bot]


def trend_line(results: list[str]) -> str:
    out = GREY + "TREND (senaste 20):  " + RESET
    for r in results[-20:]:
        if r == "W":
            out += ORANGE + "▄" + RESET
        elif r == "L":
            out += CYAN + "▄" + RESET
        else:
            out += GREY + "▂" + RESET
    return out


def render_frame(n, total, d, o, last, move_wins, draws, results) -> str:
    rows = []
    rows += header(total)
    rows.append("")
    left = panel("DONALD · KOD", donald_panel(d, n), PANEL_W, PANEL_H, BORDER_D)
    center = panel("MATCHFLÖDE",
                   center_panel(n, total, d, o, last, move_wins, draws),
                   CENTER_W, PANEL_H, BORDER_C)
    right = panel("OSKAR · AI", oskar_panel(o, n), PANEL_W, PANEL_H, BORDER_O)
    rows += merge_rows(left, center, right)
    rows.append("")
    rows.append(trend_line(results))
    rows += stat_boxes(n, d, o, draws, results)
    return "\n".join(rows)


def final_summary(ref: MatchReferee, rounds_played: int) -> str:
    a, b = ref.agent_a, ref.agent_b
    decisive = a.score + b.score
    out = []
    out.append("═" * WIDTH)
    out.append(f"{BOLD}  📊 SLUTSTATISTIK — {rounds_played} omgångar{RESET}")
    out.append("─" * WIDTH)
    winner = a if a.score > b.score else b if b.score > a.score else None
    if winner:
        out.append(f"  {GOLD}{BOLD}🏆 Vinnare: {winner.name} ({a.score}–{b.score}){RESET}")
    else:
        out.append(f"  {GOLD}{BOLD}🤝 Matchen slutade oavgjort!{RESET}")
    out.append(f"  Oavgjorda omgångar: {ref.draws}  ({decisive} avgörande)")
    out.append("─" * WIDTH)
    best = max(MOVES, key=lambda m: ref.move_wins[m])
    for move in MOVES:
        w = ref.move_wins[move]
        share = w / decisive * 100 if decisive else 0
        mark = f"  {GOLD}{BOLD}← BÄSTA UTFALLET{RESET}" if move == best else ""
        out.append(f"    {EMOJI[move]} {move:<6} {w:>3} st ({share:4.1f} %){mark}")
    out.append("═" * WIDTH)
    return "\n".join(out)


# --------------------------------------------------------------------------
# Huvudloop
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Sten, Sax, Påse: Donald vs Oskar (dashboard)")
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--delay", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--final-only", action="store_true", help="rita bara slutdashboarden")
    args = ap.parse_args()

    donald = Donald("Donald", seed=args.seed)
    oskar = Oskar("Oskar", opponent=donald, seed=None if args.seed is None else args.seed + 1)
    ref = MatchReferee(donald, oskar)

    last = None
    if args.final_only:
        for n in range(1, args.rounds + 1):
            last = ref.play_round()
        print("\033[?1049h\033[H\033[J\033[?25l", end="")
        print(render_frame(args.rounds, args.rounds, donald, oskar, last,
                           ref.move_wins, ref.draws, donald.results))
        print("\033[?25h", end="")
        try:
            input(f"\n{GREY}Tryck Enter för att avsluta ...{RESET}")
        except EOFError:
            pass
        print("\033[?1049l", end="")
        print(final_summary(ref, args.rounds))
        return

    sys.stdout.write("\033[?1049h\033[H\033[J\033[?25l")  # alt-skärm, göm markör
    try:
        for n in range(1, args.rounds + 1):
            last = ref.play_round()
            frame = render_frame(n, args.rounds, donald, oskar, last,
                                 ref.move_wins, ref.draws, donald.results)
            sys.stdout.write("\033[H" + frame + "\n")
            sys.stdout.flush()
            if args.delay > 0:
                time.sleep(args.delay)
        time.sleep(max(args.delay, 0.2))
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\033[?25h\033[?1049l")  # återställ terminalen
        sys.stdout.flush()
    print(final_summary(ref, min(len(donald.history), args.rounds)))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Matchen avbröts.{RESET}")
        sys.exit(1)
