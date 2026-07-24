import io
import unittest

try:
    from scripts.build_zobrist_book import history_to_zobrist, load_dump_entries
    from python_chess.chess_logic import GameState
    from uci import apply_uci_move
except (ImportError, SyntaxError):
    raise unittest.SkipTest("needs python-chess and engine (pypy venv)")


DUMP_PGN = """[Event "?"]
[White "A1) Ruy Lopez Main"]
[Black "5.O-O Be7"]
[FEN "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"]
[Result "*"]

1. e4 {comment}
1. e5
2. Nf3( { alt }2.Nc3 Nf6 3.f4 ( 3.Bc4 { nested } ) )
2. Nc6
*
[Event "?"]
[White "Introduction"]
[Black "Introduction"]
[Result "*"]

1. d4
*
"""


class LoadDumpEntriesTests(unittest.TestCase):
    def test_parses_one_move_per_line_format_for_black(self):
        entries = load_dump_entries(io.StringIO(DUMP_PGN), our_color_is_white=False)
        self.assertEqual(entries["e2e4"], {"e7e5": 1})
        self.assertEqual(entries["e2e4 e7e5 g1f3"], {"b8c6": 1})

    def test_skips_intro_chapters(self):
        entries = load_dump_entries(io.StringIO(DUMP_PGN), our_color_is_white=False)
        for key in entries:
            self.assertFalse(key.startswith("d2d4"))


class HistoryToZobristTests(unittest.TestCase):
    def test_startpos_key_maps_to_startpos_hash(self):
        result = history_to_zobrist({"": "d2d4"})
        self.assertEqual(result, {str(GameState().zobrist_key()): "d2d4"})

    def test_transposed_histories_collapse_to_one_position(self):
        a = "d2d4 d7d5 g1f3 g8f6 c2c4"
        b = "d2d4 g8f6 g1f3 d7d5 c2c4"
        result = history_to_zobrist({a: "c7c6", b: "c7c6"})
        self.assertEqual(len(result), 1)
        self.assertEqual(list(result.values()), ["c7c6"])


if __name__ == "__main__":
    unittest.main()
