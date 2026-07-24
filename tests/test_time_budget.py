import unittest

from python_chess.chess_logic import GameState
from uci import game_state_from_fen, time_budget


PARAMS = {"wtime": 300000, "winc": 3000}


def with_full_ramp(state):
    state.move_log = [None] * 40  # past the early-game ramp
    return state


class TimeBudgetTests(unittest.TestCase):
    def test_full_board_spends_at_base_rate(self):
        state = with_full_ramp(GameState())  # 32 pieces
        soft, hard = time_budget(state, PARAMS)
        self.assertAlmostEqual(soft, (300000 / 10 + 3000 / 2) / 1000)
        self.assertAlmostEqual(hard, min(soft * 2, 300000 / 4 / 1000))

    def test_early_game_ramp_still_applies(self):
        state = GameState()  # empty move_log
        soft, _ = time_budget(state, PARAMS)
        self.assertAlmostEqual(soft, (300000 / 10 + 3000 / 2) / 1000 * 0.35)

    def test_sparse_board_tapers_budget(self):
        # 9 pieces: halfway into the taper band (14 full -> 8 floor)
        state = with_full_ramp(
            game_state_from_fen("4k3/pppp2pp/8/8/8/8/8/R3K3 w - - 0 1")
        )
        soft, _ = time_budget(state, PARAMS)
        base = (300000 / 10 + 3000 / 2) / 1000
        self.assertAlmostEqual(soft, base * (0.5 + 0.5 * (9 - 8) / 6))

    def test_near_tablebase_board_spends_half_rate(self):
        # 7 pieces: at or below the taper floor
        state = with_full_ramp(
            game_state_from_fen("4k3/pppp4/8/8/8/8/8/R3K3 w - - 0 1")
        )
        soft, _ = time_budget(state, PARAMS)
        base = (300000 / 10 + 3000 / 2) / 1000
        self.assertAlmostEqual(soft, base * 0.5)


if __name__ == "__main__":
    unittest.main()
