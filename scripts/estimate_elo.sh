#!/bin/sh
set -e
cd "$(dirname "$0")/.."
ROUNDS="${ROUNDS:-15}"
DEPTH="${DEPTH:-3}"
LEVELS="${LEVELS:-1320 1400 1500}"
PY="${PYTHON:-python3}"
if ! "$PY" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))' 2>/dev/null; then
    PY=/opt/homebrew/bin/python3
fi
mkdir -p elo_results
for elo in $LEVELS; do
    fastchess \
        -engine cmd="$PY" args=uci.py dir=. name=python_chess_engine depth="$DEPTH" \
        -engine cmd=stockfish name="stockfish-$elo" \
            option.UCI_LimitStrength=true option.UCI_Elo="$elo" st=0.5 \
        -openings file=scripts/openings.epd format=epd order=random \
        -rounds "$ROUNDS" -games 2 -concurrency 2 -recover \
        -pgnout file="elo_results/vs_stockfish_$elo.pgn" \
        | tee "elo_results/vs_stockfish_$elo.log"
done
grep -h "^Elo\|^Games" elo_results/*.log
