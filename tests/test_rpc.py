from __future__ import absolute_import, division, print_function, unicode_literals

import unittest

from nectarengine.rpc import RPC


class Testcases(unittest.TestCase):
    def test_rpc_blockchain(self):
        rpc = RPC()
        result = rpc.getLatestBlockInfo(endpoint="blockchain")
        self.assertTrue(len(result) > 0)

    def test_rpc_contract(self):
        rpc = RPC()
        result = rpc.getContract({"name": "token"}, endpoint="contracts")
        self.assertTrue(len(result) > 0)
