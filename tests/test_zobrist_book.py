import unittest

import uci
from python_chess.chess_logic import GameState
from uci import apply_uci_move


def state_after(moves):
    state = GameState()
    for move in moves:
        apply_uci_move(state, move)
    return state


class ZobristBookTests(unittest.TestCase):
    def test_transposed_move_orders_share_a_key(self):
        a = state_after(["d2d4", "d7d5", "g1f3", "g8f6", "c2c4"])
        b = state_after(["d2d4", "g8f6", "g1f3", "d7d5", "c2c4"])
        self.assertEqual(a.zobrist_key(), b.zobrist_key())

    def test_handle_go_probes_book_by_position(self):
        state = state_after(["d2d4", "g8f6", "g1f3", "d7d5", "c2c4"])
        holder = {"state": state}
        original = uci.BOOK
        uci.BOOK = {str(state.zobrist_key()): "c7c6"}
        try:
            result = uci.handle_go(holder, ["go", "depth", "1"], default_depth=1)
        finally:
            uci.BOOK = original
        self.assertEqual(result, "bestmove c7c6")

    def test_unknown_position_falls_through_to_search(self):
        state = state_after(["h2h4"])
        holder = {"state": state}
        original = uci.BOOK
        uci.BOOK = {}
        try:
            result = uci.handle_go(holder, ["go", "depth", "1"], default_depth=1)
        finally:
            uci.BOOK = original
        self.assertTrue(result.startswith("bestmove "))
        self.assertNotEqual(result, "bestmove 0000")


if __name__ == "__main__":
    unittest.main()
