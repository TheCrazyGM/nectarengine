from typing import Any, Dict, List, Union


class Cond:
    """Helper for constructing Hive Engine query conditions (Mongo-style operators)."""

    @staticmethod
    def gt(value: Any) -> Dict[str, Any]:
        """Greater than ($gt)."""
        return {"$gt": value}

    @staticmethod
    def gte(value: Any) -> Dict[str, Any]:
        """Greater than or equal ($gte)."""
        return {"$gte": value}

    @staticmethod
    def lt(value: Any) -> Dict[str, Any]:
        """Less than ($lt)."""
        return {"$lt": value}

    @staticmethod
    def lte(value: Any) -> Dict[str, Any]:
        """Less than or equal ($lte)."""
        return {"$lte": value}

    @staticmethod
    def ne(value: Any) -> Dict[str, Any]:
        """Not equal ($ne)."""
        return {"$ne": value}

    @staticmethod
    def in_list(values: List[Any]) -> Dict[str, Any]:
        """In list ($in)."""
        return {"$in": values}

    @staticmethod
    def nin(values: List[Any]) -> Dict[str, Any]:
        """Not in list ($nin)."""
        return {"$nin": values}


class Query:
    """Helper for constructing dictionary queries."""

    @staticmethod
    def match(**kwargs: Union[Any, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Construct a query dictionary from keyword arguments.

        Example:
            Query.match(account="hive-engine", _id=Cond.gt(10))
            # Returns: {'account': 'hive-engine', '_id': {'$gt': 10}}
        """
        return kwargs
