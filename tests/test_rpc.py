import json
import unittest
from unittest.mock import Mock, patch

from nectarengine.rpc import RPC


class Testcases(unittest.TestCase):
    @patch("nectarengine.rpc.RPC.request_send")
    def test_rpc_blockchain(self, mock_send):
        mock_send.return_value = json.dumps({"result": {"blockNumber": 123}})
        rpc = RPC()
        rpc.nodes = Mock()
        rpc.nodes.reset_error_cnt_call = Mock()
        result = rpc.getLatestBlockInfo(endpoint="blockchain")
        self.assertEqual(result["blockNumber"], 123)
        mock_send.assert_called_once()

    @patch("nectarengine.rpc.RPC.request_send")
    def test_rpc_contract(self, mock_send):
        mock_send.return_value = json.dumps({"result": {"name": "token"}})
        rpc = RPC()
        rpc.nodes = Mock()
        rpc.nodes.reset_error_cnt_call = Mock()
        result = rpc.getContract({"name": "token"}, endpoint="contracts")
        self.assertEqual(result["name"], "token")
        mock_send.assert_called_once()
