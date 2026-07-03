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

from python_chess.chess_ai import negamax_ai
from python_chess.chess_logic import CastleRights, DrawChecker, GameState, Move

ENGINE_NAME = "python_chess_engine"
ENGINE_AUTHOR = "Zhuo Zhuzhen"

DEFAULT_DEPTH = 3
MAX_DEPTH = 6
BRANCHING_ESTIMATE = 8

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
    if tokens and tokens[0] == "startpos":
        game_state = GameState()
        tokens = tokens[1:]
    elif tokens and tokens[0] == "fen":
        fen = " ".join(tokens[1:7])
        game_state = game_state_from_fen(fen)
        tokens = tokens[7:]
    else:
        return

    if tokens and tokens[0] == "moves":
        for uci in tokens[1:]:
            apply_uci_move(game_state, uci)

    game_state_holder["state"] = game_state


def time_budget(game_state: GameState, params: dict) -> float | None:
    if "movetime" in params:
        return params["movetime"] / 1000

    remaining = params.get("wtime" if game_state.white_move else "btime")
    if remaining is None:
        return None

    increment = params.get("winc" if game_state.white_move else "binc", 0)
    return min(remaining / 12 + increment * 0.8, remaining / 3) / 1000


def handle_go(game_state: GameState, tokens: list[str], default_depth: int) -> str:
    params = {}
    for key in ("wtime", "btime", "winc", "binc", "movetime", "depth"):
        if key in tokens:
            params[key] = int(tokens[tokens.index(key) + 1])

    valid_moves = game_state.get_valid_moves()
    if not valid_moves:
        return "bestmove 0000"

    if "depth" in params:
        max_depth = params["depth"]
        budget = None
    else:
        budget = time_budget(game_state, params)
        max_depth = MAX_DEPTH if budget is not None else default_depth

    start = time.monotonic()
    best_move = None

    for depth in range(1, max_depth + 1):
        with contextlib.redirect_stdout(io.StringIO()):
            move, _, evaluation = negamax_ai(game_state, valid_moves, depth)

        best_move = move
        elapsed = time.monotonic() - start
        print(
            f"info depth {depth} score cp {int(evaluation * 100)}"
            f" time {int(elapsed * 1000)}",
            flush=True,
        )

        if budget is not None and elapsed * BRANCHING_ESTIMATE > budget:
            break

    return f"bestmove {move_to_uci(best_move)}"


def main() -> None:
    game_state_holder = {"state": GameState()}
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

        elif command == "setoption":
            if "Depth" in args and "value" in args:
                depth = int(args[args.index("value") + 1])

        elif command == "position":
            handle_position(game_state_holder, args)

        elif command == "go":
            print(handle_go(game_state_holder["state"], args, depth), flush=True)

        elif command == "quit":
            break


if __name__ == "__main__":
    main()
