import contextlib
import io
import re
import unittest

import uci
from python_chess.chess_logic import GameState


class ScoreOutputTests(unittest.TestCase):
    def test_info_score_is_centipawns_not_hundredths(self):
        holder = {"state": GameState()}
        original = uci.BOOK
        uci.BOOK = {}  # force a search
        try:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                result = uci.handle_go(holder, ["go", "depth", "2"], default_depth=2)
        finally:
            uci.BOOK = original
        self.assertTrue(result.startswith("bestmove"))
        match = re.search(r"score cp (-?\d+)", out.getvalue())
        self.assertIsNotNone(match)
        # startpos at depth 2 is near equality: tens of cp, never thousands
        self.assertLess(abs(int(match.group(1))), 1000)


if __name__ == "__main__":
    unittest.main()
