import unittest

try:
    from scripts.extend_zobrist_book import multipv_width, select_candidates
except (ImportError, SyntaxError):
    raise unittest.SkipTest("needs python-chess and engine (pypy venv)")


class MultipvWidthTests(unittest.TestCase):
    def test_width_decays_with_ply(self):
        self.assertEqual(multipv_width(0), 4)
        self.assertEqual(multipv_width(6), 3)
        self.assertEqual(multipv_width(10), 2)


class SelectCandidatesTests(unittest.TestCase):
    def test_keeps_multipv_moves_within_window_of_best(self):
        scored = [("e2e4", 30), ("d2d4", 25), ("g1f3", -40), ("b1c3", -80)]
        picked = select_candidates(scored, observed=set(), window_cp=50)
        self.assertEqual(picked, {"e2e4", "d2d4"})

    def test_observed_book_moves_always_included(self):
        scored = [("e2e4", 30)]
        picked = select_candidates(scored, observed={"b2b3"}, window_cp=50)
        self.assertEqual(picked, {"e2e4", "b2b3"})


if __name__ == "__main__":
    unittest.main()
