from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from nectarengine.pool import LiquidityPool


class Testcases(unittest.TestCase):
    def test_pool(self):
        lp = LiquidityPool()
        pool = lp.get_pool("SWAP.HIVE:INCOME")
        self.assertTrue(pool is not None)
        self.assertTrue(len(pool) > 0)
        p1 = lp.get_liquidity_positions(token_pair="SWAP.HIVE:INCOME")
        self.assertTrue(p1 is not None)
        self.assertTrue(len(p1) > 0)
        p2 = lp.get_liquidity_positions(account="thecrazygm")
        self.assertTrue(p2 is not None)
        self.assertTrue(len(p2) > 0)
