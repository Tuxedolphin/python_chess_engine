import unittest

from uci import game_state_from_fen, move_to_uci


class CastlingTests(unittest.TestCase):
    def test_black_cannot_castle_through_a_pawn_attack(self):
        state = game_state_from_fen("r3k3/4P3/8/8/8/8/8/4K3 b q - 0 1")
        legal_moves = {move_to_uci(move) for move in state.get_valid_moves()}
        self.assertNotIn("e8c8", legal_moves)

    def test_white_cannot_castle_through_a_pawn_attack(self):
        state = game_state_from_fen("4k3/8/8/8/8/8/4p3/R3K3 w Q - 0 1")
        legal_moves = {move_to_uci(move) for move in state.get_valid_moves()}
        self.assertNotIn("e1c1", legal_moves)


if __name__ == "__main__":
    unittest.main()
