from unittest import TestCase

from nectarengine.utils import Cond, Query


class TestUtils(TestCase):
    def test_cond_operators(self):
        self.assertEqual(Cond.gt(5), {"$gt": 5})
        self.assertEqual(Cond.gte(5), {"$gte": 5})
        self.assertEqual(Cond.lt(5), {"$lt": 5})
        self.assertEqual(Cond.lte(5), {"$lte": 5})
        self.assertEqual(Cond.ne(5), {"$ne": 5})
        self.assertEqual(Cond.in_list([1, 2]), {"$in": [1, 2]})
        self.assertEqual(Cond.nin([1, 2]), {"$nin": [1, 2]})

    def test_query_match(self):
        q = Query.match(account="hive-engine", balance=Cond.gt(100))
        self.assertEqual(q, {"account": "hive-engine", "balance": {"$gt": 100}})
