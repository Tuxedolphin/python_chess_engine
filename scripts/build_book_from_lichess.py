"""
Builds an opening book from your own lichess history, in the
{moves_prefix: reply_move} format used by uci.py's BOOK dict.

Usage:
    python build_book_from_lichess.py

Requires: pip install requests chess
"""

import io
import json
from collections import defaultdict, Counter

import requests
import chess.pgn

USERNAME = "Tuxedolphin"
CHESSCOM_USERNAME = "tuxedolphin"
CHESSCOM_MIN_RATING = 2100
PERF_TYPES = "bullet,blitz,rapid"
MAX_BOOK_PLY = 20
MIN_TIMES_SEEN = 2
MIN_WIN_RATE = 0.45
OUTPUT_PY_FILE = "opening_book.py"


def fetch_games():
    url = f"https://lichess.org/api/games/user/{USERNAME}"
    params = {
        "perfType": PERF_TYPES,
        "opening": "true",
        "rated": "true",
    }
    headers = {"Accept": "application/x-chess-pgn"}

    print(f"Fetching all of {USERNAME}'s rated {PERF_TYPES} games...")
    resp = requests.get(url, params=params, headers=headers)
    resp.raise_for_status()
    return resp.text


def fetch_chesscom_games():
    if not CHESSCOM_USERNAME:
        return ""

    headers = {"User-Agent": f"opening-book-builder ({CHESSCOM_USERNAME})"}
    archives = requests.get(
        f"https://api.chess.com/pub/player/{CHESSCOM_USERNAME}/games/archives",
        headers=headers,
    ).json()["archives"]

    print(f"Fetching {len(archives)} monthly archives from chess.com...")
    pgns = []
    for url in archives:
        for game in requests.get(url, headers=headers).json().get("games", []):
            if (
                game.get("rules") != "chess"
                or not game.get("rated")
                or game.get("time_class") not in ("bullet", "blitz", "rapid")
                or "pgn" not in game
            ):
                continue

            white = game.get("white", {})
            black = game.get("black", {})
            if white.get("username", "").lower() == CHESSCOM_USERNAME.lower():
                my_rating = white.get("rating", 0)
            else:
                my_rating = black.get("rating", 0)

            if my_rating >= CHESSCOM_MIN_RATING:
                pgns.append(game["pgn"])
    return "\n\n".join(pgns)


def build_book(pgn_text: str):
    counts = defaultdict(Counter)
    scores = defaultdict(Counter)
    game_count = 0
    pgn_io = io.StringIO(pgn_text)

    while True:
        game = chess.pgn.read_game(pgn_io)
        if game is None:
            break
        game_count += 1

        white = game.headers.get("White", "")
        result = game.headers.get("Result", "*")
        i_am_white = white.lower() == USERNAME.lower()

        if result == "1-0":
            my_score = 1.0 if i_am_white else 0.0
        elif result == "0-1":
            my_score = 0.0 if i_am_white else 1.0
        elif result == "1/2-1/2":
            my_score = 0.5
        else:
            continue

        moves_so_far = []
        for ply_index, move in enumerate(game.mainline_moves()):
            if ply_index >= MAX_BOOK_PLY:
                break
            is_my_move = (ply_index % 2 == 0) == i_am_white
            key = " ".join(moves_so_far)
            if is_my_move:
                counts[key][move.uci()] += 1
                scores[key][move.uci()] += my_score
            moves_so_far.append(move.uci())

    print(f"Parsed {game_count} games.")
    return counts, scores


def collapse_book(counts, scores):
    result = {}
    for key, counter in counts.items():
        for move, count in counter.most_common():
            if count < MIN_TIMES_SEEN:
                break
            win_rate = scores[key][move] / count
            if win_rate >= MIN_WIN_RATE:
                result[key] = move
                break
    return result


def main():
    pgn_text = fetch_games() + "\n\n" + fetch_chesscom_games()
    counts, scores = build_book(pgn_text)
    final_book = collapse_book(counts, scores)

    print(f"\nBuilt a book with {len(final_book)} entries "
          f"(min {MIN_TIMES_SEEN} occurrences, win rate >= {MIN_WIN_RATE}).\n")

    with open(OUTPUT_PY_FILE, "w") as f:
        f.write("BOOK = ")
        f.write(json.dumps(final_book, indent=4))
        f.write("\n")

    print(f"Wrote {OUTPUT_PY_FILE} — place it next to uci.py.")

    for k, v in sorted(final_book.items(), key=lambda item: len(item[0]))[:10]:
        print(f"  {k!r:40s} -> {v}")


if __name__ == "__main__":
    main()
