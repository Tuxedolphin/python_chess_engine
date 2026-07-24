# Testing Notes

Engine changes are validated with self-play matches (fastchess) and rating
matches against strength-limited Stockfish. Matches run with colours swapped
per opening pair, openings from `scripts/openings.epd`.

## Results so far

| Change | Match | Result | Decision |
|---|---|---|---|
| TT depth tolerance (accept entries 2 ply shallower) | 20 games, 2s/move | −127 ± 81 Elo | rejected, removed |
| Aggressive time (remaining/12 vs /20, pre-eval) | 20 games, 5+3 | −17 ± 159 (flat) | kept /12 |
| Positional eval vs PeSTO-only | 30 games, 2s/move | +95 ± 119, LOS 96% | merged |
| vs Stockfish `UCI_Elo` 1320, 20s/move | 30 games | 30–0 | floor only |
| vs Stockfish 1700, 20s/move | 20 games | 82.5% raw / 71% clean | perf ≈ 1854–1969 |
| vs Stockfish 2000, 20s/move (clean, all mates) | 20 games | 70% | perf ≈ 2147 |
| Knight outposts + bad bishop (vs deployed bundle) | 30 games, 2s/move | +23 ± 149 (flat) | kept |
| Timing bundle (ramp, stability discount, 6× gate, mate-stop) | 20 games, 5+3 | −53 ± 138 (flat, LOS 21%) | kept — motivated by live-game clock pathologies, not Elo |

Combined Stockfish ladder estimate: **~2,050–2,100 at 20s/move** (M3, PyPy).

## Queued experiments

Run each overnight; one at a time, Mac plugged in + `caffeinate -is`.

0. **A/B queue (2026-07-24), overnight candidates — real `tc=300+3`, ≥20
   games each, per the timing convention:**
   - *Piece-count time budget* (remaining/10 + taper below 14 pieces,
     shipped 2026-07-24 with the EGTB rationale) vs the old flat
     remaining/12 build. First priority — it shipped unvalidated.
   - *Depth gate on hard budget* (shipped 2026-07-24, also unvalidated —
     A/B together with or after the budget change). Motivating game
     y7yKc0KB: after 8.O-O the old gate stopped at depth 4 and played
     8...O-O-O (+171cp Stockfish); new gate reaches depth 5 and plays
     8...e5 (+87cp). Use that position as the smoke check.
   - *Zobrist-keyed opening book* — shipped 2026-07-24
     (scripts/build_zobrist_book.py, 24,419 entries; Black vs 1.e4 switched
     from Scandinavian to Werle 1.e4 e5 when the Scandi PGN couldn't be
     re-downloaded). A/B vs the history-keyed 26,675-entry build
     (opening_book.py at git tag/commit "feat: added 1.c4 e5 repertoire").
     Stockfish extension of remaining coverage gaps deferred until after
     that A/B.
   - *Opening book: Scandinavian 3...Qd6 vs Werle 1.e4 e5* as Black.
     Werle PGN kept in repo root (dump format — needs the converter in a
     variant of scripts/build_repertoire_book.py). Build a second
     opening_book variant, A/B the two books.
   - *challenge_timeout 1 vs 5+ min*: 1-min set live 2026-07-24 for
     observation; decide keep/revert from a few days of matchmaking
     behaviour (declines, rate limits), not Elo.
   - *Legacy-book overrides*: measure whether curated d4/Scandi/Slav lines
     outperform the old c4 machine book head-to-head (old book build vs
     new, same engine).

1. **Stockfish ladder, 2300 rung — partially played, resume pending.**
   With the extended 14,762-entry book, combined so far: **1 win, 10 losses,
   2 draws** (2/13 = 15%; PGNs /tmp/elo_2300_extbook.pgn +
   /tmp/elo_2300_extbook_resume.pgn), stopped twice to free the CPU.
   ~7 games remain for the planned 20; keep combining tallies — never
   discard a partial block, that would bias the estimate. 15% vs 2300
   implies perf ≈ 2000; consistent with the ~2,050–2,100 estimate once
   error bars (±~150 at n=13) are applied. The 2200 rung (not yet started)
   is queued after.
   (An earlier 6-game start with the old 4,702-entry book, 2-4, was
   discarded when the book changed mid-ladder.) Command (engine 20s/move,
   Stockfish on a real clock so it cannot forfeit on movetime):

   ```
   fastchess -engine cmd=/opt/homebrew/bin/pypy3.11 args=uci.py dir=. name=python_chess_engine st=20 \
     -engine cmd=stockfish name=stockfish-2300 option.UCI_LimitStrength=true option.UCI_Elo=2300 tc=300+3 \
     -openings file=scripts/openings.epd format=epd order=random \
     -rounds 9 -games 2 -concurrency 2 -recover -pgnout file=/tmp/elo_2300_extbook_resume.pgn
   ```

   If combined score > 40%, also run a 2200 rung to tighten the estimate.

2. **Optional**: the timing bundle came back −53 ± 138 (flat, LOS 21%) —
   kept for its clock-safety motivation, but if the sign nags, isolate the
   stability stop-fraction 0.35 vs 0.5 with a 20-game 5+3 self-play match
   (control: archive at
   `~/Projects/engine-baselines/deployed-2026-07-04-morning/uci.py`).

3. **Eval increment: c-pawn-blocking knight penalty** — unvalidated solo
   (shipped inside the outposts bundle after the A/B ran). First suspect if
   tonight's results regress; isolate with the same st=2 command shape as
   the outposts test if needed.

## Opening book

- 2026-07-04: book rebuilt from lichess + chess.com (≥2100) games,
  2,233 → 4,702 entries, MAX_BOOK_PLY 20. Stockfish audit (depth-14 screen,
  depth-18 confirm, 30cp threshold) replaced 357 entries.
- 2026-07-04: Stockfish extension (`scripts/extend_book_with_stockfish.py`,
  run on the VPS) added 10,060 entries — book now 14,762, covering every
  plausible line to ply 12 (bot replies from depth-18 Stockfish, opponent
  branches from observed moves + multipv within 50cp). All entries
  legality-checked; deployed to the live bot the same day.

## Conventions

- Never conclude from < 20 games unless the result is lopsided (LOS > 95%).
- Fixed `st=` matches isolate eval/search changes; real `tc=` matches are for
  time-management changes.
- Performance rating from a score s vs anchor A: `A + 400·log10(s/(1−s))`;
  exclude games decided by opponent movetime forfeits.
