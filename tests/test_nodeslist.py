import unittest
from unittest.mock import Mock, patch

from nectarengine.api import Api
from nectarengine.nodeslist import Node, Nodes


def sample_metadata():
    return {
        "report": [
            {
                "node": "https://engine-fast.example",
                "engine": True,
                "SSCnodeVersion": "ivm-1.1.3",
                "token": {"rank": 1, "ok": True},
                "contract": {"rank": 2, "ok": True},
                "account_history": {"rank": 3, "ok": True},
                "config": {"rank": 4, "ok": True},
                "latency": {"rank": 5, "ok": True},
            },
            {
                "node": "https://engine-slow.example",
                "engine": True,
                "SSCnodeVersion": "ivm-1.1.3",
                "token": {"rank": 5, "ok": False},
                "contract": {"rank": 10, "ok": True},
                "account_history": {"rank": 15, "ok": False},
                "config": {"rank": 12, "ok": True},
                "latency": {"rank": 30, "ok": True},
            },
            {
                "node": "https://engine-invalid.example",
                "engine": False,
                "SSCnodeVersion": "unknown",
            },
        ],
        "failing_nodes": {"https://engine-slow.example": "Timeout while syncing"},
    }


class NodesListTests(unittest.TestCase):
    def test_node_trailing_slash_and_string_representation(self):
        node = Node(rank=1.0, url="https://foo.example", data={})
        self.assertEqual(node.as_url(), "https://foo.example/")
        self.assertEqual(str(node), "https://foo.example/")

    def test_nodes_refresh_and_sorting(self):
        metadata = sample_metadata()
        with (
            patch("nectarengine.nodeslist.Hive"),
            patch("nectarengine.nodeslist.Account") as account,
        ):
            account.return_value.json_metadata = metadata
            nodes = Nodes(auto_refresh=False)
            nodes.refresh()

        urls = [node.as_url() for node in nodes.node_list()]
        self.assertEqual(
            urls,
            [
                "https://engine-fast.example/",
                "https://engine-slow.example/",
                "https://engine-invalid.example/",
            ],
        )
        self.assertIsNone(nodes[0].failing_cause)
        self.assertEqual(nodes[1].failing_cause, "Timeout while syncing")

    def test_node_list_triggers_refresh_when_empty(self):
        metadata = sample_metadata()
        with (
            patch("nectarengine.nodeslist.Hive"),
            patch("nectarengine.nodeslist.Account") as account,
        ):
            account.return_value.json_metadata = metadata
            nodes = Nodes(auto_refresh=False)
            urls = nodes.as_urls(limit=1)
            self.assertEqual(account.call_count, 1)
            nodes.node_list()
            self.assertEqual(account.call_count, 1)
        self.assertEqual(urls, ["https://engine-fast.example/"])

    def test_fastest_and_primary_url_helpers(self):
        metadata = sample_metadata()
        with (
            patch("nectarengine.nodeslist.Hive"),
            patch("nectarengine.nodeslist.Account") as account,
        ):
            account.return_value.json_metadata = metadata
            nodes = Nodes(auto_refresh=False)
            nodes.refresh()

        self.assertEqual(nodes.primary_url(), "https://engine-fast.example/")
        self.assertEqual(
            [node.as_url() for node in nodes.fastest(2)],
            ["https://engine-fast.example/", "https://engine-slow.example/"],
        )
        self.assertEqual(nodes.fastest(0), [])
        self.assertEqual(nodes.fastest(5), nodes.node_list())

    def test_raw_metadata_is_copied(self):
        metadata = sample_metadata()
        with (
            patch("nectarengine.nodeslist.Hive"),
            patch("nectarengine.nodeslist.Account") as account,
        ):
            account.return_value.json_metadata = metadata
            nodes = Nodes(auto_refresh=False)
            nodes.refresh()

        raw_copy = nodes.raw_metadata
        raw_copy["new_key"] = "value"
        self.assertNotIn("new_key", nodes.raw_metadata)

    def test_api_accepts_nodes_inputs(self):
        nodes = Nodes(auto_refresh=False)
        nodes._nodes = [
            Node(rank=1.0, url="https://primary.example", data={}),
            Node(rank=2.0, url="https://secondary.example", data={}),
        ]

        with patch("nectarengine.api.RPC") as rpc:
            api_from_nodes = Api(url=nodes)
            self.assertEqual(api_from_nodes.url, "https://primary.example/")
            rpc.assert_called_once_with(url="https://primary.example/", user=None, password=None)

            rpc.reset_mock()
            Api(url=nodes.fastest(2))
            rpc.assert_called_once_with(url="https://primary.example/", user=None, password=None)

            rpc.reset_mock()
            Api(url=[nodes.node_list()[1]])
            rpc.assert_called_once_with(url="https://secondary.example/", user=None, password=None)

    @patch("nectarengine.nodeslist.requests.get")
    def test_beacon_fetches_and_sorts_nodes(self, mock_get: Mock):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"endpoint": "https://node-a", "score": 100, "fail": 0},
            {"endpoint": "https://node-b", "score": 80, "fail": 2},
        ]
        mock_get.return_value = mock_response

        nodes = Nodes(auto_refresh=False)
        beacon_nodes = nodes.beacon()

        self.assertEqual(
            [node.as_url() for node in beacon_nodes],
            ["https://node-a/", "https://node-b/"],
        )
        self.assertEqual(beacon_nodes[1].failing_cause, "2 failed health checks")

        limited_nodes = nodes.beacon(limit=1)
        self.assertEqual(len(limited_nodes), 1)
        self.assertEqual(limited_nodes[0].as_url(), "https://node-a/")

    @patch("nectarengine.nodeslist.requests.get")
    def test_beacon_history_fetches_nodes(self, mock_get: Mock):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = [
            {"endpoint": "https://history-a", "score": 95, "fail": 0},
        ]
        mock_get.return_value = mock_response

        nodes = Nodes(auto_refresh=False)
        history_nodes = nodes.beacon_history()

        self.assertEqual([node.as_url() for node in history_nodes], ["https://history-a/"])


if __name__ == "__main__":
    unittest.main()
