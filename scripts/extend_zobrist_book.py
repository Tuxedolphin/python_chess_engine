"""
Extends the zobrist-keyed opening_book.py with Stockfish so every plausible
line is covered for the first MAX_PLY plies, for the bot as either colour.

Walks the opening tree twice (bot as white, bot as black):
- at bot-to-move nodes, keep the existing book reply if present, otherwise
  add Stockfish's best move at REPLY_DEPTH;
- at opponent-to-move nodes, branch into every move whose child position is
  already in the book (course/legacy lines) plus Stockfish's top multipv
  moves within WINDOW_CP of best. Multipv width decays with ply.

Transpositions are deduped by zobrist key. Progress is checkpointed to
OUTPUT_PY_FILE every 50 added entries, so the run survives interruption
with a usable book and can be resumed (existing entries are kept).

Run under the pypy venv (needs python-chess AND the engine):
    buildvenv/bin/python scripts/extend_zobrist_book.py [max_ply]
"""

import json
import os
import sys
import time

import chess
import chess.engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python_chess.chess_logic import GameState
from uci import apply_uci_move

MAX_PLY = 12
REPLY_DEPTH = 22
EXPAND_DEPTH = 16
WINDOW_CP = 50
OUTPUT_PY_FILE = "opening_book.py"


def multipv_width(ply: int) -> int:
    if ply < 4:
        return 4
    if ply < 8:
        return 3
    return 2


def select_candidates(scored, observed, window_cp):
    """
    scored: [(uci, cp_from_mover_pov)] from multipv, best first.
    observed: opponent moves whose child position the book already covers.
    Returns the union of observed moves and multipv moves within window.
    """
    picked = set(observed)
    if scored:
        best = scored[0][1]
        for uci, cp in scored:
            if best - cp <= window_cp:
                picked.add(uci)
    return picked


def zobrist_of(path):
    state = GameState()
    for uci in path:
        apply_uci_move(state, uci)
    return str(state.zobrist_key())


def main():
    max_ply = int(sys.argv[1]) if len(sys.argv) > 1 else MAX_PLY

    from opening_book import BOOK

    book = dict(BOOK)
    sf = chess.engine.SimpleEngine.popen_uci("stockfish")
    sf.configure({"Threads": 4, "Hash": 512})

    added = 0
    start = time.time()
    visited = set()

    def save():
        with open(OUTPUT_PY_FILE, "w") as f:
            f.write("BOOK = ")
            f.write(json.dumps(book, indent=4, sort_keys=True))
            f.write("\n")

    def walk(path, bot_is_white):
        nonlocal added
        if len(path) >= max_ply:
            return
        board = chess.Board()
        for uci in path:
            board.push(chess.Move.from_uci(uci))
        if board.is_game_over():
            return
        key = zobrist_of(path)
        if (key, bot_is_white) in visited:
            return
        visited.add((key, bot_is_white))

        bot_to_move = board.turn == (chess.WHITE if bot_is_white else chess.BLACK)
        if bot_to_move:
            reply = book.get(key)
            if reply is None or chess.Move.from_uci(reply) not in board.legal_moves:
                info = sf.analyse(board, chess.engine.Limit(depth=REPLY_DEPTH))
                reply = info["pv"][0].uci()
                book[key] = reply
                added += 1
                if added % 10 == 0:
                    rate = added / max(time.time() - start, 1)
                    print(f"added {added} (ply {len(path)}, {rate:.2f}/s)", flush=True)
                if added % 50 == 0:
                    save()
            walk(path + [reply], bot_is_white)
        else:
            observed = set()
            for move in board.legal_moves:
                board.push(move)
                child_key = zobrist_of(path + [move.uci()])
                if child_key in book:
                    observed.add(move.uci())
                board.pop()
            infos = sf.analyse(
                board,
                chess.engine.Limit(depth=EXPAND_DEPTH),
                multipv=multipv_width(len(path)),
            )
            scored = [
                (pv["pv"][0].uci(), pv["score"].pov(board.turn).score(mate_score=10000))
                for pv in infos
                if pv.get("pv")
            ]
            for uci in select_candidates(scored, observed, WINDOW_CP):
                walk(path + [uci], bot_is_white)

    for bot_is_white in (True, False):
        colour = "white" if bot_is_white else "black"
        print(f"=== extending, bot as {colour}, to ply {max_ply} ===", flush=True)
        walk([], bot_is_white)
        save()

    sf.quit()
    save()
    print(f"Done: {added} entries added, book now {len(book)}; "
          f"{(time.time() - start) / 60:.1f} min")


if __name__ == "__main__":
    main()
