"""
Builds opening_book.py from the curated repertoire PGNs in book_sources/.

Repertoire entries are keyed the same way uci.py builds its book_key: the
space-joined UCI move history from the starting position. For positions the
repertoire does not cover, the legacy machine-built book (kept in
legacy_opening_book.py) is used as a fallback.

Run from the repository root:
    python3 scripts/build_repertoire_book.py
"""

import json
import os
import re
import sys

import chess.pgn

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

OUTPUT_PY_FILE = "opening_book.py"

# (path, our_color_is_white)
SOURCES = (
    ("book_sources/white_d4_shankland_p1.pgn", True),
    ("book_sources/white_d4_shankland_p2.pgn", True),
    ("book_sources/white_d4_shankland_p3.pgn", True),
    ("book_sources/black_e4_scandinavian.pgn", False),
    ("book_sources/black_d4_slav.pgn", False),
)

# Chapters that hold complete games or exercises rather than repertoire lines.
SKIP_HEADER_RE = re.compile(
    r"model game|annotated game|exercise|introduction|tactic|thematic",
    re.IGNORECASE,
)


def collect_entries(handle, our_color_is_white):
    """Reads every game in a PGN stream and returns {key: {reply: count}}."""
    entries = {}

    while True:
        game = chess.pgn.read_game(handle)
        if game is None:
            break
        if game.headers.get("SetUp") == "1" or "FEN" in game.headers:
            continue
        header_text = f'{game.headers.get("White", "")} {game.headers.get("Black", "")}'
        if SKIP_HEADER_RE.search(header_text):
            continue
        _walk(game, [], our_color_is_white, entries)

    return entries


def _walk(node, moves_so_far, our_color_is_white, entries):
    our_move = (len(moves_so_far) % 2 == 0) == our_color_is_white

    if our_move:
        # Follow only the repertoire's chosen (mainline) reply.
        if not node.variations:
            return
        chosen = node.variations[0]
        uci = chosen.move.uci()
        if uci == "0000":  # null move: annotation device, not a real line
            return
        key = " ".join(moves_so_far)
        replies = entries.setdefault(key, {})
        replies[uci] = replies.get(uci, 0) + 1
        _walk(chosen, moves_so_far + [uci], our_color_is_white, entries)
    else:
        # Cover every opponent try.
        for child in node.variations:
            uci = child.move.uci()
            if uci == "0000":
                continue
            _walk(
                child,
                moves_so_far + [uci],
                our_color_is_white,
                entries,
            )


def resolve_conflicts(entries):
    """Picks the most frequent reply per key; first-seen wins ties."""
    book = {}
    for key, replies in entries.items():
        best_reply = None
        best_count = 0
        for reply, count in replies.items():
            if count > best_count:
                best_reply = reply
                best_count = count
        book[key] = best_reply
    return book


def main():
    combined = {}
    for path, our_color_is_white in SOURCES:
        with open(path, encoding="utf-8", errors="replace") as handle:
            entries = collect_entries(handle, our_color_is_white)
        for key, replies in entries.items():
            target = combined.setdefault(key, {})
            for reply, count in replies.items():
                target[reply] = target.get(reply, 0) + count
        print(f"{path}: {len(entries)} positions")

    repertoire = resolve_conflicts(combined)
    print(f"Repertoire: {len(repertoire)} entries")

    from legacy_opening_book import BOOK as LEGACY_BOOK

    merged = dict(LEGACY_BOOK)
    merged.update(repertoire)
    print(
        f"Merged with legacy book: {len(merged)} entries "
        f"({len(merged) - len(repertoire)} legacy-only)"
    )

    with open(OUTPUT_PY_FILE, "w") as f:
        f.write("BOOK = ")
        f.write(json.dumps(merged, indent=4, sort_keys=True))
        f.write("\n")

    print(f"Wrote {OUTPUT_PY_FILE}")


if __name__ == "__main__":
    main()
