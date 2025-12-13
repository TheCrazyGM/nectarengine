from unittest import TestCase
from unittest.mock import MagicMock

from nectarengine.api import Api


class TestFindMany(TestCase):
    def test_find_many_passthrough_without_last_id(self):
        """Should behave exactly like find if no last_id is provided."""
        api = Api(url="http://mock-node")
        api.find = MagicMock(return_value=[])

        api.find_many("tokens", "tokens", {"precision": 8})

        api.find.assert_called_once_with(
            "tokens", "tokens", query={"precision": 8}, limit=1000, offset=0, indexes=[]
        )

    def test_find_many_injects_last_id(self):
        """Should inject _id > last_id into the query."""
        api = Api(url="http://mock-node")
        api.find = MagicMock(return_value=[])

        api.find_many("tokens", "tokens", {"precision": 8}, last_id="mock_id_123")

        expected_query = {"precision": 8, "_id": {"$gt": "mock_id_123"}}
        api.find.assert_called_once_with(
            "tokens", "tokens", query=expected_query, limit=1000, offset=0, indexes=[]
        )

    def test_find_many_injects_into_existing_id_query(self):
        """Should merge with existing _id query if it is a dict."""
        api = Api(url="http://mock-node")
        api.find = MagicMock(return_value=[])

        # Existing query with _id condition
        query = {"_id": {"$in": [1, 2, 3]}}
        api.find_many("tokens", "tokens", query, last_id="mock_id_123")

        expected_query = {"_id": {"$in": [1, 2, 3], "$gt": "mock_id_123"}}
        api.find.assert_called_once_with(
            "tokens", "tokens", query=expected_query, limit=1000, offset=0, indexes=[]
        )

    def test_find_many_overrides_simple_id_query(self):
        """Should override simple _id equality with range check if last_id provided."""
        api = Api(url="http://mock-node")
        api.find = MagicMock(return_value=[])

        # Existing query with simple equality
        query = {"_id": "specific_id"}
        api.find_many("tokens", "tokens", query, last_id="mock_id_123")

        # This behavior is debatable but matches the implementation logic choice
        expected_query = {"_id": {"$gt": "mock_id_123"}}
        api.find.assert_called_once_with(
            "tokens", "tokens", query=expected_query, limit=1000, offset=0, indexes=[]
        )
