import unittest

from nectarengine.tokenobject import Token


class Testcases(unittest.TestCase):
    def test_token(self):
        eng = Token("BEE")
        self.assertTrue(eng is not None)
        self.assertTrue(eng["symbol"] == "BEE")
