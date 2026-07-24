import io
import unittest

try:
    from scripts.build_repertoire_book import collect_entries, resolve_conflicts
except ImportError:  # book tooling needs python-chess (CPython only)
    raise unittest.SkipTest("python-chess not available in this interpreter")


WHITE_PGN = """
[Event "Repertoire"]
[White "Main line"]
[Black "Chapter"]
[Result "*"]

1. d4 d5 (1... Nf6 2. c4) 2. c4 *
"""

WHITE_ALTERNATIVES_PGN = """
[Event "Repertoire"]
[White "Main line"]
[Black "Chapter"]
[Result "*"]

1. d4 d5 2. c4 (2. Nf3 Nf6) 2... c6 *
"""

BLACK_PGN = """
[Event "Repertoire"]
[White "Main line"]
[Black "Chapter"]
[Result "*"]

1. e4 d5 2. exd5 Qxd5 *
"""

SETUP_PGN = """
[Event "Repertoire"]
[White "Tactics!"]
[Black "Tactic #1"]
[Result "*"]
[SetUp "1"]
[FEN "4k3/8/8/8/8/8/4P3/4K3 w - - 0 1"]

1. e4 *
"""

NULL_MOVE_PGN = """
[Event "Repertoire"]
[White "Main line"]
[Black "Chapter"]
[Result "*"]

1. d4 d5 2. -- e5 3. dxe5 *
"""

MODEL_GAME_PGN = """
[Event "Repertoire"]
[White "Carlsen, Magnus"]
[Black "Model Games"]
[Result "1-0"]

1. Nf3 d5 2. g3 *
"""


class CollectEntriesTests(unittest.TestCase):
    def test_white_records_replies_for_all_opponent_branches(self):
        entries = collect_entries(io.StringIO(WHITE_PGN), our_color_is_white=True)
        self.assertEqual(list(entries[""].keys()), ["d2d4"])
        self.assertIn("c2c4", entries["d2d4 d7d5"])
        self.assertIn("c2c4", entries["d2d4 g8f6"])

    def test_our_alternatives_follow_mainline_only(self):
        entries = collect_entries(
            io.StringIO(WHITE_ALTERNATIVES_PGN), our_color_is_white=True
        )
        self.assertEqual(list(entries["d2d4 d7d5"].keys()), ["c2c4"])
        for key in entries:
            self.assertNotIn("g1f3", key.split())

    def test_black_records_replies_on_black_to_move_keys(self):
        entries = collect_entries(io.StringIO(BLACK_PGN), our_color_is_white=False)
        self.assertIn("d7d5", entries["e2e4"])
        self.assertIn("d8d5", entries["e2e4 d7d5 e4d5"])
        self.assertNotIn("", entries)

    def test_setup_positions_are_skipped(self):
        entries = collect_entries(io.StringIO(SETUP_PGN), our_color_is_white=True)
        self.assertEqual(entries, {})

    def test_null_moves_end_the_line(self):
        entries = collect_entries(io.StringIO(NULL_MOVE_PGN), our_color_is_white=True)
        self.assertEqual(entries, {"": {"d2d4": 1}})

    def test_model_games_are_skipped(self):
        entries = collect_entries(io.StringIO(MODEL_GAME_PGN), our_color_is_white=True)
        self.assertEqual(entries, {})


class ResolveConflictsTests(unittest.TestCase):
    def test_most_frequent_reply_wins(self):
        entries = {"": {"d2d4": 3, "e2e4": 1}}
        self.assertEqual(resolve_conflicts(entries), {"": "d2d4"})

    def test_first_seen_wins_ties(self):
        entries = {"": {"d2d4": 2, "e2e4": 2}}
        self.assertEqual(resolve_conflicts(entries), {"": "d2d4"})


if __name__ == "__main__":
    unittest.main()
