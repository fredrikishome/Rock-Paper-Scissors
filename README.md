# ✊ ✌️ ✋ Sten, Sax, Påse — Agent + Agent

![Smoke tests](https://github.com/fredrikishome/Rock-Paper-Scissors/actions/workflows/smoke.yml/badge.svg)

🇬🇧 English README: [README.en.md](README.en.md)

Två autonoma agenter — **Donald 🧨** och **Oskar 🌊** — som spelar sten, sax, påse
mot varandra, med live-visualisering i både terminal (CLI) och webbläsare.

Projektet visar hur en enkel spelmiljö kan användas för att experimentera med
agentstrategier, statistik och realtidsvisualisering.

---

## Innehåll

| Fil | Beskrivning |
|---|---|
| `rps_cli.py` | **Dashboard-CLI** — live-gränssnitt i terminalen med paneler, AI-kommentar och statistik |
| `rps_cli_classic.py` | **Klassisk CLI** — enkel liststil, en rad per omgång |
| `index.html` | **Webb-dashboard** — självständig sida (öppna i webbläsare) med animerad duell-linje |
| `data/match_100.json` | Referensdata från en simulerad match på 100 omgångar |
| `docs/references/` | Textsnapshot av CLI-dashboarden |
| `README.en.md` | Engelsk version av README |
| `.github/workflows/smoke.yml` | CI: röktester av båda CLI:erna (Linux + Windows) och validering av webbdatan |

## Agenterna

### Donald 🧨 — "Slumpts-spelaren"
Spelar totalt slumpmässigt. Oförutsägbar i teorin — men eftersom han inte
anpassar sig kan hans mönster (t.ex. upprepade drag) utnyttjas.

### Oskar 🌊 — "Mönsterläsaren"
En enkel adaptiv strategi:
1. Om motståndaren **upprepat samma drag två gånger i rad**, förutsäger Oskar
   nästa drag och spelar det som slår det förutsagda draget.
2. Annars spelar han slumpmässigt.

I en 100-omgångars match gav detta Oskar en liten men stabil övertag
(eftersom Donalds upprepade drag utnyttjas), samtidigt som Sax ofta blev det
enskilda "bästa utfallet" — ett direkt resultat av Oskars motdrag mot Donalds Påse.

## Kom igång

### CLI — dashboard-stil (rekommenderas)
```bash
python rps_cli.py                  # 100 omgångar, live-dashboard
python rps_cli.py --rounds 20      # kortare match
python rps_cli.py --delay 0.2      # lugnare tempo
python rps_cli.py --seed 42        # reproducerbar match
python rps_cli.py --final-only     # visa bara slutdashboarden
```
> Tips: kör i Windows Terminal, PowerShell 7+, iTerm2 eller annan modern
> terminal för full färgkala och emoji-stöd.

### CLI — klassisk stil
```bash
python rps_cli_classic.py              # 100 omgångar
python rps_cli_classic.py --rounds 10
python rps_cli_classic.py --delay 0.1
python rps_cli_classic.py --seed 42
```

### Webb-dashboard
Öppna `index.html` i valfri modern webbläsare. Ingen server eller beroenden krävs.

Designen är inspirerad av en futuristisk "AI-dashboard"-estetik — se
textsnapshoten av CLI-dashboarden i
[docs/references/cli_dashboard_snapshot.txt](docs/references/cli_dashboard_snapshot.txt).

Funktioner:
- **Duell-linje** mellan agenterna: en glödande pil skickas per omgång från
  förloraren till vinnaren — riktningen byter håll beroende på vem som vann
- **VS-noden** visar vinnaren av senaste omgången (`D +1` / `O +1`, `=` vid oavgjort)
- **Händer** ovanför varje agent-avatar visar vad de spelade
- **Balansmarkör** som glider mot den agent som leder matchen totalt
- AI-panel med mönsterdetektering (träff ✔ / miss ✘) och förtroende-mätare
- Statistik: vinstflöde per val, trend för senaste 20 omgångarna, samt vilket
  val som var **bästa utfallet** (flest vunna matcher)
- Kontroller: ▶/⏸ paus, ⟲ kör igen, hastighet 0.5×–4×

## Statistikmetodik

Efter varje match räknas:
- **Slutställning** (vinster per agent) och antal oavgjorda
- **Vunna matcher per val** — vilket av sten/sax/påse som låg bakom flest
  vunna omgångar ("bästa utfallet")
- **Valfördelning** per agent

Viktigt: i ett symmetriskt spel är inget drag objektivt bättre (teoretiska
33,3 % vardera). Att ett val "vinner" statistiken i en enskild match beror på
slump och motståndarens valfördelning — ju fler omgångar, desto närmare 33/33/33.

## Krav

- Python 3.10+ (CLI-gränssnitten). Inga externa paket.
- Webbsidan kräver endast en modern webbläsare.

## CI

Vid varje push/pull request körs [smoke.yml](.github/workflows/smoke.yml):
- Båda CLI:erna spelas 5 omgångar (seed 42) på **Ubuntu och Windows** med Python 3.10/3.12/3.13
- `index.html` valideras: 100 inbäddade omgångar med giltiga vinnarvärden

## Licens

MIT — se [LICENSE](LICENSE).
