#!/usr/bin/env python3
"""
UCI adapter for the engine, so it can be plugged into standard chess tooling:
fastchess/cutechess-cli for rating matches, GUIs like Arena, and lichess-bot.

Usage:
    python3 uci.py

Supports: uci, isready, ucinewgame, setoption, position, go, stop, quit.
Search runs at a fixed depth (default 3, set with "setoption name Depth
value N" or "go depth N"); clock times are ignored.
"""

import contextlib
import io
import sys
import time

from python_chess import chess_ai
from python_chess.chess_ai import negamax_ai
from python_chess.chess_logic import CastleRights, DrawChecker, GameState, Move

try:
    from opening_book import BOOK
except ImportError:
    BOOK = {}

ENGINE_NAME = "python_chess_engine"
ENGINE_AUTHOR = "Zhuo Zhuzhen"

DEFAULT_DEPTH = 3
MAX_DEPTH = 12

FEN_TO_PIECE = {
    "P": "wp", "N": "wN", "B": "wB", "R": "wR", "Q": "wQ", "K": "wK",
    "p": "bp", "n": "bN", "b": "bB", "r": "bR", "q": "bQ", "k": "bK",
}

MATERIAL = {"Q": 9, "R": 5, "B": 3, "N": 3, "p": 1}


def square_to_coords(square: str) -> tuple[int, int]:
    return Move.ranks_to_rows[square[1]], Move.files_to_columns[square[0]]


def coords_to_square(row: int, column: int) -> str:
    return Move.columns_to_files[column] + Move.rows_to_ranks[row]


def move_to_uci(move: Move) -> str:
    uci = coords_to_square(move.start_row, move.start_column) + coords_to_square(
        move.end_row, move.end_column
    )
    if move.is_pawn_promotion:
        uci += "q"
    return uci


def game_state_from_fen(fen: str) -> GameState:
    placement, side, castling, en_passant, *rest = fen.split()
    halfmove_clock = int(rest[0]) if rest else 0

    game_state = GameState()
    game_state.board = [["" for _ in range(8)] for _ in range(8)]

    for row, rank in enumerate(placement.split("/")):
        column = 0
        for char in rank:
            if char.isdigit():
                column += int(char)
            else:
                game_state.board[row][column] = FEN_TO_PIECE[char]
                column += 1

    game_state.white_move = side == "w"

    game_state.white_material = game_state.black_material = 0
    for row in range(8):
        for column in range(8):
            piece = game_state.board[row][column]
            if piece == "wK":
                game_state.white_king_location = (row, column)
            elif piece == "bK":
                game_state.black_king_location = (row, column)
            elif piece:
                value = MATERIAL[piece[1]]
                if piece[0] == "w":
                    game_state.white_material += value
                else:
                    game_state.black_material += value

    game_state.current_castle_rights = CastleRights(
        "K" in castling, "k" in castling, "Q" in castling, "q" in castling
    )
    game_state.castle_rights_log = [game_state.current_castle_rights.copy()]

    game_state.en_passant_square = (
        square_to_coords(en_passant) if en_passant != "-" else ()
    )

    game_state.draw_log = [DrawChecker(game_state.board, halfmove_clock)]

    game_state.board_hash = game_state.compute_board_hash()
    game_state.board_hash_log = [game_state.board_hash]

    position_key = game_state.zobrist_key()
    game_state.position_key_log = [position_key]
    game_state.position_counts = {position_key: 1}
    game_state.en_passant_log = [game_state.en_passant_square]

    return game_state


def apply_uci_move(game_state: GameState, uci: str) -> None:
    start = square_to_coords(uci[:2])
    end = square_to_coords(uci[2:4])
    promotion = uci[4].upper() if len(uci) == 5 else "Q"

    for move in game_state.get_valid_moves():
        if move.start == start and move.end == end:
            game_state.make_move(move, promotion if move.is_pawn_promotion else "")
            return

    raise ValueError(f"Illegal move: {uci}")


def handle_position(game_state_holder: dict, tokens: list[str]) -> None:
    from_startpos = False

    if tokens and tokens[0] == "startpos":
        game_state = GameState()
        from_startpos = True
        tokens = tokens[1:]
    elif tokens and tokens[0] == "fen":
        fen = " ".join(tokens[1:7])
        game_state = game_state_from_fen(fen)
        tokens = tokens[7:]
    else:
        return

    played = []
    if tokens and tokens[0] == "moves":
        played = tokens[1:]
        for uci in played:
            apply_uci_move(game_state, uci)

    game_state_holder["state"] = game_state
    game_state_holder["book_key"] = " ".join(played) if from_startpos else None


def time_budget(game_state: GameState, params: dict) -> tuple[float, float] | None:
    if "movetime" in params:
        cap = params["movetime"] * 0.9 / 1000
        return cap, cap

    remaining = params.get("wtime" if game_state.white_move else "btime")
    if remaining is None:
        return None

    increment = params.get("winc" if game_state.white_move else "binc", 0)
    soft = (remaining / 10 + increment / 2) / 1000
    soft *= min(0.35 + len(game_state.move_log) * 0.025, 1.0)

    # Spend while the position is complex; taper as material comes off.
    # At <= 7 pieces the lichess tablebase plays for us (needs >= 10s on the
    # clock, so the saved time also protects that probe window).
    pieces = sum(1 for row in game_state.board for square in row if square)
    if pieces < 14:
        soft *= max(0.5, 0.5 + 0.5 * (pieces - 8) / 6)

    hard = min(soft * 2, remaining / 4 / 1000)
    return soft, hard


def handle_go(game_state_holder: dict, tokens: list[str], default_depth: int) -> str:
    game_state = game_state_holder["state"]

    book_key = game_state_holder.get("book_key")
    if book_key is not None:
        book_move = BOOK.get(book_key)
        if book_move:
            for move in game_state.get_valid_moves():
                if move_to_uci(move) == book_move:
                    print("info string book move", flush=True)
                    return f"bestmove {book_move}"

    params = {}
    for key in ("wtime", "btime", "winc", "binc", "movetime", "depth"):
        if key in tokens:
            params[key] = int(tokens[tokens.index(key) + 1])

    valid_moves = game_state.get_valid_moves()
    if not valid_moves:
        return "bestmove 0000"

    if len(valid_moves) == 1 and "depth" not in params:
        print("info string forced move", flush=True)
        return f"bestmove {move_to_uci(valid_moves[0])}"

    if "depth" in params:
        max_depth = params["depth"]
        budget = None
    else:
        budget = time_budget(game_state, params)
        max_depth = MAX_DEPTH if budget is not None else default_depth

    soft, hard = budget if budget is not None else (None, None)

    start = time.monotonic()
    best_move = None
    reached_depth = 0
    evaluation = 0.0

    move_log_length = len(game_state.move_log)
    previous_best = None
    previous_elapsed = 0.0

    for depth in range(1, max_depth + 1):
        if budget is None or depth == 1 or best_move is None:
            chess_ai.SEARCH_DEADLINE = None
        else:
            chess_ai.SEARCH_DEADLINE = start + hard

        try:
            with contextlib.redirect_stdout(io.StringIO()):
                move, _, evaluation = negamax_ai(game_state, valid_moves, depth)
        except chess_ai.SearchTimeout:
            while len(game_state.move_log) > move_log_length:
                game_state.undo_move()
            break

        best_move = move
        reached_depth = depth
        elapsed = time.monotonic() - start

        if evaluation >= chess_ai.MATE_SCORE:
            break

        if budget is not None:
            stop_fraction = 0.35 if move is previous_best else 0.5
            if elapsed > soft * stop_fraction:
                break

            iteration_time = elapsed - previous_elapsed
            allowance = soft if move is previous_best else soft * 1.6
            if elapsed + iteration_time * 6 > allowance:
                break

        previous_best = move
        previous_elapsed = elapsed

    chess_ai.SEARCH_DEADLINE = None
    elapsed = time.monotonic() - start
    print(
        f"info depth {reached_depth} score cp {int(evaluation * 100)}"
        f" time {int(elapsed * 1000)}",
        flush=True,
    )
    return f"bestmove {move_to_uci(best_move)}"


def main() -> None:
    game_state_holder = {"state": GameState(), "book_key": ""}
    depth = DEFAULT_DEPTH

    for line in sys.stdin:
        tokens = line.split()
        if not tokens:
            continue
        command, args = tokens[0], tokens[1:]

        if command == "uci":
            print(f"id name {ENGINE_NAME}")
            print(f"id author {ENGINE_AUTHOR}")
            print(f"option name Depth type spin default {DEFAULT_DEPTH} min 1 max 5")
            print("uciok", flush=True)

        elif command == "isready":
            print("readyok", flush=True)

        elif command == "ucinewgame":
            game_state_holder["state"] = GameState()
            game_state_holder["book_key"] = ""

        elif command == "setoption":
            if "Depth" in args and "value" in args:
                depth = int(args[args.index("value") + 1])

        elif command == "position":
            handle_position(game_state_holder, args)

        elif command == "go":
            print(handle_go(game_state_holder, args, depth), flush=True)

        elif command == "quit":
            break


if __name__ == "__main__":
    main()
