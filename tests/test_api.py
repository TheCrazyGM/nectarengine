from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from nectarengine.api import Api


class Testcases(unittest.TestCase):
    def test_api(self):
        api = Api()
        result = api.get_latest_block_info()
        next_test = result["blockNumber"]
        self.assertTrue(len(result) > 0)

        result = api.get_block_info(next_test - 64000)
        next_test = result["transactions"][0]["transactionId"]
        self.assertTrue(len(result) > 0)

        result = api.get_transaction_info(next_test)
        self.assertTrue(len(result) > 0)

        result = api.get_contract("tokens")
        self.assertTrue(len(result) > 0)

        result = api.find("tokens", "tokens")
        self.assertTrue(len(result) > 0)

        result = api.find_one("tokens", "tokens")
        self.assertTrue(len(result) > 0)

        result = api.get_history("thecrazygm", "INCOME")
        self.assertTrue(len(result) > 0)
