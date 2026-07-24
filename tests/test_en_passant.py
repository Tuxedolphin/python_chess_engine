import unittest

from uci import apply_uci_move, game_state_from_fen, move_to_uci


POSITIONS = (
    ("5k2/5p2/1p2p2p/3pr1pP/3P3K/5bP1/6q1/8 w - g6 0 39", "h5g6"),
    ("8/4k3/1p6/1Pp3R1/3KB1P1/7P/4r3/8 w - c6 0 46", "b5c6"),
    ("6k1/4b3/4p1p1/4PpP1/4Kn2/1p6/8/1RB2r2 w - f6 0 52", "g5f6"),
)


class EnPassantCheckEvasionTests(unittest.TestCase):
    def test_en_passant_can_capture_a_checking_pawn(self):
        for fen, expected in POSITIONS:
            with self.subTest(fen=fen):
                state = game_state_from_fen(fen)
                legal_moves = {move_to_uci(move) for move in state.get_valid_moves()}
                self.assertIn(expected, legal_moves)

    def test_uci_adapter_accepts_en_passant_check_evasions(self):
        for fen, move in POSITIONS:
            with self.subTest(fen=fen):
                state = game_state_from_fen(fen)
                apply_uci_move(state, move)
                self.assertFalse(state.white_move)

    def test_en_passant_is_the_only_reply_when_it_is_the_only_evasion(self):
        state = game_state_from_fen(POSITIONS[0][0])
        legal_moves = {move_to_uci(move) for move in state.get_valid_moves()}
        self.assertEqual(legal_moves, {"h5g6"})


if __name__ == "__main__":
    unittest.main()
