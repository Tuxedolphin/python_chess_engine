"""
Extends opening_book.py with Stockfish so the book covers every plausible
line for the first MAX_PLY plies (6 moves), for the bot as either colour.

The book maps a move-sequence prefix to the bot's reply. Gaps appear when an
opponent plays a move never seen in the source games. This script walks the
opening tree twice (bot as white, bot as black):

- at bot-to-move nodes, keep the existing book reply if present, otherwise
  add Stockfish's best move at REPLY_DEPTH;
- at opponent-to-move nodes, branch into the moves worth covering: every
  opponent move already present in the book (those lines exist in real games)
  plus Stockfish's top multipv moves within WINDOW_CP of the best. The
  multipv width decays with depth to keep the tree small.

Progress is checkpointed to OUTPUT_PY_FILE every 50 added entries, so the
run can be watched and survives interruption with a usable book.

Usage (run from the repository root, ~2-6 h depending on machine):
    python3 scripts/extend_book_with_stockfish.py
"""

import json
import sys

import chess
import chess.engine

sys.path.insert(0, ".")
from opening_book import BOOK

MAX_PLY = 12
REPLY_DEPTH = 18
EXPAND_DEPTH = 12
WINDOW_CP = 50
OUTPUT_PY_FILE = "opening_book.py"


def multipv_width(ply: int) -> int:
    if ply < 4:
        return 4
    if ply < 8:
        return 3
    return 2


def main():
    sf = chess.engine.SimpleEngine.popen_uci("stockfish")
    sf.configure({"Threads": 2, "Hash": 256})

    updated = dict(BOOK)
    added = 0

    observed_next = {}
    for key in BOOK:
        moves = key.split()
        for i in range(len(moves)):
            prefix = " ".join(moves[:i])
            observed_next.setdefault(prefix, set()).add(moves[i])

    def checkpoint():
        with open(OUTPUT_PY_FILE, "w") as f:
            f.write("BOOK = ")
            f.write(json.dumps(updated, indent=4))
            f.write("\n")

    def best_reply(board):
        info = sf.analyse(board, chess.engine.Limit(depth=REPLY_DEPTH))
        return info["pv"][0].uci()

    def opponent_candidates(board, key):
        candidates = set(observed_next.get(key, set()))
        infos = sf.analyse(
            board,
            chess.engine.Limit(depth=EXPAND_DEPTH),
            multipv=multipv_width(board.ply()),
        )
        best = infos[0]["score"].pov(board.turn).score(mate_score=10000)
        for info in infos:
            score = info["score"].pov(board.turn).score(mate_score=10000)
            if best - score <= WINDOW_CP and info.get("pv"):
                candidates.add(info["pv"][0].uci())
        return candidates

    def cover(key, board, bot_to_move):
        nonlocal added
        if board.ply() >= MAX_PLY or board.is_game_over():
            return

        if bot_to_move:
            reply = updated.get(key)
            if reply is None or chess.Move.from_uci(reply) not in board.legal_moves:
                reply = best_reply(board)
                updated[key] = reply
                added += 1
                if added % 50 == 0:
                    checkpoint()
                    print(f"{added} entries added (ply {board.ply()})", flush=True)
            board.push_uci(reply)
            cover(f"{key} {reply}".strip(), board, False)
            board.pop()
        else:
            for uci in sorted(opponent_candidates(board, key)):
                board.push_uci(uci)
                cover(f"{key} {uci}".strip(), board, True)
                board.pop()

    for bot_is_white in (True, False):
        print(f"Covering tree with bot as {'white' if bot_is_white else 'black'}",
              flush=True)
        cover("", chess.Board(), bot_is_white)

    checkpoint()
    sf.quit()
    print(f"\nDone: {added} entries added, book now {len(updated)} entries.")


if __name__ == "__main__":
    main()
