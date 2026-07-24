"""
Audits opening_book.py with Stockfish: any book reply that is more than
THRESHOLD_CP worse than Stockfish's best move gets replaced by that move.

Usage:
    python scripts/validate_book.py
"""

import sys
import chess
import chess.engine

sys.path.insert(0, ".")
from opening_book import BOOK

SCREEN_DEPTH = 14
CONFIRM_DEPTH = 18
THRESHOLD_CP = 30
OUTPUT_PY_FILE = "opening_book.py"


def main():
    sf = chess.engine.SimpleEngine.popen_uci("stockfish")
    screen = chess.engine.Limit(depth=SCREEN_DEPTH)
    confirm = chess.engine.Limit(depth=CONFIRM_DEPTH)
    updated = {}
    replaced = []

    def score_of(board, limit, move=None):
        kwargs = {"root_moves": [chess.Move.from_uci(move)]} if move else {}
        info = sf.analyse(board, limit, **kwargs)
        return (
            info["score"].pov(board.turn).score(mate_score=10000),
            info["pv"][0].uci() if info.get("pv") else None,
        )

    for index, (key, reply) in enumerate(sorted(BOOK.items()), 1):
        board = chess.Board()
        for uci in key.split():
            board.push_uci(uci)

        best_score, best_move = score_of(board, screen)

        if best_move == reply:
            updated[key] = reply
        else:
            reply_score, _ = score_of(board, screen, reply)

            if best_score - reply_score > THRESHOLD_CP:
                deep_best_score, deep_best_move = score_of(board, confirm)
                deep_reply_score, _ = score_of(board, confirm, reply)

                if (
                    deep_best_move != reply
                    and deep_best_score - deep_reply_score > THRESHOLD_CP
                ):
                    updated[key] = deep_best_move
                    replaced.append(
                        (key, reply, deep_best_move, deep_best_score - deep_reply_score)
                    )
                else:
                    updated[key] = reply
            else:
                updated[key] = reply

        if index % 200 == 0:
            print(f"{index}/{len(BOOK)} checked, {len(replaced)} replaced", flush=True)

    sf.quit()

    import json
    with open(OUTPUT_PY_FILE, "w") as f:
        f.write("BOOK = ")
        f.write(json.dumps(updated, indent=4))
        f.write("\n")

    print(f"\nDone: {len(replaced)} of {len(BOOK)} entries replaced "
          f"(> {THRESHOLD_CP}cp worse, confirmed at depth {CONFIRM_DEPTH}).")
    for key, old, new, loss in replaced[:15]:
        print(f"  [{key or 'start'}] {old} -> {new} (saved {loss}cp)")


if __name__ == "__main__":
    main()
