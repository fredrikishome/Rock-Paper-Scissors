#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sten, Sax, Påse — Donald vs Oskar (KLASSISKT gränssnitt)
Enkel liststil: en rad per omgång, därefter slutstatistik.
För dashboard-version, se rps_cli.py.

Användning:
    python rps_cli_classic.py              # 100 omgångar
    python rps_cli_classic.py --rounds 20
    python rps_cli_classic.py --delay 0.1  # paus mellan omgångar
    python rps_cli_classic.py --seed 42    # reproducerbar match
"""

import argparse
import os
import random
import sys
import time

if os.name == "nt":
    os.system("")  # aktivera ANSI-färger i Windows-konsolen
for _stream in (sys.stdout, sys.stderr):
    _stream.reconfigure(encoding="utf-8", errors="replace")

MOVES = ["Sten", "Sax", "Påse"]
EMOJI = {"Sten": "✊", "Sax": "✌️", "Påse": "✋"}
BEATS = {"Sten": "Sax", "Sax": "Påse", "Påse": "Sten"}  # nyckeln slår värdet

RESET, BOLD, DIM, ITAL = "\033[0m", "\033[1m", "\033[2m", "\033[3m"
ORANGE, CYAN, GREY, GOLD = "\033[38;5;208m", "\033[36m", "\033[90m", "\033[33m"
GREEN, RED = "\033[32m", "\033[31m"


# --------------------------------------------------------------------------
# Agenterna
# --------------------------------------------------------------------------
class Agent:
    """Basagent: har ett namn och ett gränssnitt mot spelledaren."""

    def __init__(self, name: str, seed: int | None = None):
        self.name = name
        self.rng = random.Random(seed)
        self.score = 0
        self.history: list[str] = []   # egna drag
        self.results: list[str] = []   # "W", "L", "D"

    def choose_move(self) -> str:
        raise NotImplementedError

    def notify_result(self, my_move: str, result: str) -> None:
        """Spelledaren berättar utfallet EFTER att båda dragit."""
        self.history.append(my_move)
        self.results.append(result)
        if result == "W":
            self.score += 1


class Donald(Agent):
    """Donald: spelar totalt slumpt — oförutsägbar men utan plan."""

    def choose_move(self) -> str:
        return self.rng.choice(MOVES)


class Oskar(Agent):
    """Oskar: lär av mönstret. Om motståndaren upprepar ett drag två gånger
    i rad spår han nästa drag och spelar det som slår det — annars slumpt."""

    def __init__(self, name: str, opponent: Agent, seed: int | None = None):
        super().__init__(name, seed)
        self.opponent = opponent

    def choose_move(self) -> str:
        hist = self.opponent.history
        if len(hist) >= 2 and hist[-1] == hist[-2]:
            predicted = hist[-1]
            counter = next(m for m, b in BEATS.items() if b == predicted)
            return counter
        return self.rng.choice(MOVES)


# --------------------------------------------------------------------------
# Spelledaren
# --------------------------------------------------------------------------
class MatchReferee:
    """Håller reda på reglerna och meddelar agenterna utfallet."""

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
# CLI-utskrift
# --------------------------------------------------------------------------
def line(char="─", width=64):
    print(GREY + char * width + RESET)


def print_round(n, total, d_move, o_move, winner, d_score, o_score, draws):
    d_col, o_col = ORANGE, CYAN
    if winner == "Donald":
        verdict = f"{ORANGE}{BOLD}🏆 Donald vinner{RESET}"
    elif winner == "Oskar":
        verdict = f"{CYAN}{BOLD}🏆 Oskar vinner{RESET}"
    else:
        verdict = f"{GREY}🤝 Oavgjort{RESET}"
    print(
        f"  {GREY}Omgång {n:>3}/{total}{RESET}  "
        f"{d_col}{EMOJI[d_move]} {d_move:<5}{RESET} vs "
        f"{o_col}{EMOJI[o_move]} {o_move:<5}{RESET}  {verdict}   "
        f"{GREY}[{ORANGE}{d_score}{RESET}{GREY}–{CYAN}{o_score}{RESET}{GREY}] {RESET}"
    )


def print_stats(ref, rounds_played):
    a, b = ref.agent_a, ref.agent_b
    decisive = a.score + b.score
    line("═")
    print(f"{BOLD}  📊 SLUTSTATISTIK — {rounds_played} omgångar{RESET}")
    line()
    winner = a if a.score > b.score else b if b.score > a.score else None
    if winner:
        print(f"  {GOLD}{BOLD}🏆 Vinnare: {winner.name} ({a.score}–{b.score}){RESET}")
    else:
        print(f"  {GOLD}{BOLD}🤝 Matchen slutade oavgjort!{RESET}")
    print(f"  Oavgjorda omgångar: {ref.draws}  ({decisive} avgörande)")
    line()
    print(f"  {BOLD}Vunna matcher per val (bästa utfallet):{RESET}")
    best = max(MOVES, key=lambda m: ref.move_wins[m])
    for move in MOVES:
        w = ref.move_wins[move]
        share = w / decisive * 100 if decisive else 0
        bar = "█" * w
        col = {"Sten": GOLD, "Sax": CYAN, "Påse": ORANGE}[move]
        mark = f"  {GOLD}{BOLD}← BÄSTA UTFALLET{RESET}" if move == best else ""
        print(f"    {EMOJI[move]} {move:<6} {col}{bar:<{max(ref.move_wins.values())}}{RESET} {w:>3} st ({share:4.1f} %){mark}")
    line()
    for ag in (a, b):
        choices = {m: ag.history.count(m) for m in MOVES}
        dist = ", ".join(f"{EMOJI[m]} {c}" for m, c in choices.items())
        print(f"  {BOLD}{ag.name}s valfördelning:{RESET} {dist}")
    line("═")


def main():
    ap = argparse.ArgumentParser(description="Sten, Sax, Påse: Donald vs Oskar (klassisk stil)")
    ap.add_argument("--rounds", type=int, default=100)
    ap.add_argument("--delay", type=float, default=0.03, help="paus i sekunder mellan omgångar")
    ap.add_argument("--seed", type=int, default=None)
    args = ap.parse_args()

    donald = Donald("Donald", seed=args.seed)
    oskar = Oskar("Oskar", opponent=donald, seed=None if args.seed is None else args.seed + 1)
    ref = MatchReferee(donald, oskar)

    line("═")
    print(f"{BOLD}  ✊ ✌️ ✋  STEN, SAX, PÅSE — Donald 🧨 vs Oskar 🌊{RESET}")
    print(f"{DIM}  {args.rounds} omgångar · klassiskt gränssnitt{RESET}")
    line("═")

    for n in range(1, args.rounds + 1):
        d_move, o_move, winner = ref.play_round()
        print_round(n, args.rounds, d_move, o_move, winner,
                    donald.score, oskar.score, ref.draws)
        if args.delay > 0:
            time.sleep(args.delay)

    print()
    print_stats(ref, args.rounds)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{RED}Matchen avbröts.{RESET}")
        sys.exit(1)
