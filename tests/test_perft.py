import unittest

from python_chess.chess_logic import GameState


def perft(state: GameState, depth: int) -> int:
    if depth == 0:
        return 1

    nodes = 0
    for move in state.get_valid_moves():
        state.make_move(move, "Q" if move.is_pawn_promotion else "")
        nodes += perft(state, depth - 1)
        state.undo_move()
    return nodes


class PerftTests(unittest.TestCase):
    def test_starting_position(self):
        state = GameState()
        for depth, expected in ((1, 20), (2, 400), (3, 8902)):
            with self.subTest(depth=depth):
                self.assertEqual(perft(state, depth), expected)


if __name__ == "__main__":
    unittest.main()
