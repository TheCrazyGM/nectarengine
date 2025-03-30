from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from nectarengine.api import Api


class Testcases(unittest.TestCase):
    def test_api(self):
        api = Api()
        result = api.get_latest_block_info()
        self.assertTrue(len(result) > 0)

        result = api.get_block_info(200000)
        print(result)
        self.assertTrue(len(result) > 0)

        result = api.get_transaction_info("78aea60cdc4477cdf9437d8224e34c6033499169")
        self.assertTrue(len(result) > 0)

        result = api.get_contract("tokens")
        self.assertTrue(len(result) > 0)

        result = api.find("tokens", "tokens")
        self.assertTrue(len(result) > 0)

        result = api.find_one("tokens", "tokens")
        self.assertTrue(len(result) > 0)

        # result = api.get_history("thecrazygm", "INCOME")
        # self.assertTrue(len(result) > 0)
