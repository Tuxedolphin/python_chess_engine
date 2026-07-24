import unittest

from uci import should_start_next_depth


class DepthGateTests(unittest.TestCase):
    def test_starts_next_depth_when_estimate_fits_hard_budget(self):
        # y7yKc0KB move 8: depth 4 done at 4s, next estimated ~22s.
        # soft ~19s blocked it under the old gate; hard (2x soft) allows it.
        self.assertTrue(
            should_start_next_depth(
                elapsed=4.0, iteration_time=3.0, soft=19.4, hard=38.8, stable=True
            )
        )

    def test_stops_when_estimate_exceeds_hard_budget(self):
        self.assertFalse(
            should_start_next_depth(
                elapsed=4.0, iteration_time=8.0, soft=19.4, hard=38.8, stable=True
            )
        )

    def test_stops_after_soft_fraction_spent_when_stable(self):
        self.assertFalse(
            should_start_next_depth(
                elapsed=7.0, iteration_time=0.5, soft=19.4, hard=38.8, stable=True
            )
        )

    def test_unstable_best_move_gets_more_of_the_soft_budget(self):
        # 7s > 0.35*soft but < 0.5*soft: stable stops, unstable continues
        self.assertTrue(
            should_start_next_depth(
                elapsed=7.0, iteration_time=0.5, soft=19.4, hard=38.8, stable=False
            )
        )


if __name__ == "__main__":
    unittest.main()
