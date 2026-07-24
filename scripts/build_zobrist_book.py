"""
Builds a zobrist-position-keyed opening_book.py from book_sources/.

Keys are str(GameState.zobrist_key()) so transpositions hit the same entry
regardless of move order. Must therefore run under an interpreter that has
BOTH python-chess and the engine (Python >= 3.10), e.g. a pypy3.11 venv:

    pypy3.11 -m venv buildvenv && buildvenv/bin/pip install chess
    buildvenv/bin/python scripts/build_zobrist_book.py
"""

import json
import os
import re
import sys

import chess

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from python_chess.chess_logic import GameState
from scripts.build_repertoire_book import (
    SKIP_HEADER_RE,
    collect_entries,
    filter_entries,
    resolve_conflicts,
)
from uci import apply_uci_move

OUTPUT_PY_FILE = "opening_book.py"
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# (path, our_color_is_white, first_move_filter, dump_format)
SOURCES = (
    ("book_sources/white_d4_shankland_p1.pgn", True, None, False),
    ("book_sources/white_d4_shankland_p2.pgn", True, None, False),
    ("book_sources/white_d4_shankland_p3.pgn", True, None, False),
    ("book_sources/black_d4_slav.pgn", False, None, False),
    ("book_sources/black_e4_werle.pgn", False, "e2e4", True),
    ("book_sources/black_c4_english.pgn", False, "c2c4", False),
)


def load_dump_entries(handle, our_color_is_white):
    """
    Parses the nonstandard Chessable dump format (one move per line, Black
    moves numbered like White's, startpos FEN header on every game) into the
    same {history_key: {reply: count}} shape collect_entries produces.
    Games are linear; opponent branching comes from sibling games.
    """
    text = handle.read()
    entries = {}

    for block in re.split(r"(?=^\[Event )", text, flags=re.M):
        if not block.strip().startswith("[Event"):
            continue
        headers = dict(re.findall(r'^\[(\w+) "(.*)"\]', block, flags=re.M))
        fen = headers.get("FEN")
        if fen and fen.strip() != START_FEN:
            continue
        header_text = f'{headers.get("White", "")} {headers.get("Black", "")}'
        if SKIP_HEADER_RE.search(header_text):
            continue

        body = re.sub(r"^\[.*\]$", "", block, flags=re.M)
        body = re.sub(r"\{[^}]*\}", " ", body)
        while "(" in body:  # strip commentary variations, innermost first
            body, changed = re.subn(r"\([^()]*\)", " ", body)
            if not changed:
                break
        tokens = re.findall(r"\d+\.(?:\.\.)?\s*([A-Za-z][\w\-+=#]*)", body)

        board = chess.Board()
        history = []
        for san in tokens:
            try:
                move = board.parse_san(san)
            except ValueError:
                break
            uci = move.uci()
            our_move = board.turn == (chess.WHITE if our_color_is_white else chess.BLACK)
            if our_move:
                key = " ".join(history)
                replies = entries.setdefault(key, {})
                replies[uci] = replies.get(uci, 0) + 1
            board.push(move)
            history.append(uci)

    return entries


def history_to_zobrist(history_book):
    """Converts {move-history: reply} to {str(zobrist): reply} via the engine."""
    result = {}
    for key, reply in history_book.items():
        state = GameState()
        for uci in key.split():
            apply_uci_move(state, uci)
        result[str(state.zobrist_key())] = reply
    return result


def main():
    for path, _, _, _ in SOURCES:
        if not os.path.exists(path):
            sys.exit(f"Missing source {path} — re-download before rebuilding.")

    combined = {}
    for path, our_color_is_white, first_move, dump in SOURCES:
        with open(path, encoding="utf-8", errors="replace") as handle:
            loader = load_dump_entries if dump else collect_entries
            entries = filter_entries(loader(handle, our_color_is_white), first_move)
        for key, replies in entries.items():
            target = combined.setdefault(key, {})
            for reply, count in replies.items():
                target[reply] = target.get(reply, 0) + count
        print(f"{path}: {len(entries)} positions")

    repertoire = resolve_conflicts(combined)

    # Legality check on history form (independent replay via python-chess).
    bad = []
    for key, reply in repertoire.items():
        board = chess.Board()
        try:
            for uci in key.split():
                board.push(chess.Move.from_uci(uci))
            if chess.Move.from_uci(reply) not in board.legal_moves:
                bad.append(key)
        except (ValueError, AssertionError):
            bad.append(key)
    for key in bad:
        del repertoire[key]
    print(f"Repertoire: {len(repertoire)} entries ({len(bad)} illegal removed)")

    from legacy_opening_book import BOOK as LEGACY_BOOK

    legacy_z = history_to_zobrist(LEGACY_BOOK)
    repertoire_z = history_to_zobrist(repertoire)
    merged = dict(legacy_z)
    merged.update(repertoire_z)
    print(
        f"Zobrist book: {len(merged)} entries "
        f"({len(repertoire_z)} repertoire, {len(merged) - len(repertoire_z)} legacy-only)"
    )

    with open(OUTPUT_PY_FILE, "w") as f:
        f.write("BOOK = ")
        f.write(json.dumps(merged, indent=4, sort_keys=True))
        f.write("\n")
    print(f"Wrote {OUTPUT_PY_FILE}")


if __name__ == "__main__":
    main()
