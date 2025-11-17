import unittest

from nectarengine.tokens import Tokens


class Testcases(unittest.TestCase):
    def test_tokens(self):
        tokens = Tokens()
        self.assertTrue(tokens is not None)
        self.assertTrue(len(tokens) > 0)
