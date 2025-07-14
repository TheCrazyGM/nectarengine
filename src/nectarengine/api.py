from __future__ import absolute_import, division, print_function, unicode_literals

from typing import Any, Dict, List, Optional

import requests

from .rpc import RPC


class Api:
    """Access the hive-engine API"""

    def __init__(
        self,
        url: Optional[str] = None,
        rpcurl: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        if url is None:
            self.url = "https://enginerpc.com/"
        else:
            # Ensure URL has trailing slash
            self.url = url if url.endswith("/") else url + "/"
        if url is not None and rpcurl is None:
            # Pass the normalized URL to RPC
            self.rpc = RPC(url=self.url)
        else:
            # If rpcurl is provided, normalize it as well
            normalized_rpcurl = rpcurl
            if rpcurl is not None and not rpcurl.endswith("/"):
                normalized_rpcurl = rpcurl + "/"
            self.rpc = RPC(url=normalized_rpcurl)

    def get_history(
        self, account: str, symbol: str, limit: int = 1000, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """ "Get the transaction history for an account and a token"""
        response = requests.get(
            "https://accounts.hive-engine.com/accountHistory?account=%s&limit=%d&offset=%d&symbol=%s"
            % (account, limit, offset, symbol)
        )
        cnt2 = 0
        while response.status_code != 200 and cnt2 < 10:
            response = requests.get(
                "https://accounts.hive-engine.com/accountHistory?account=%s&limit=%d&offset=%d&symbol=%s"
                % (account, limit, offset, symbol)
            )
            cnt2 += 1
        return response.json()

    def get_latest_block_info(self) -> Dict[str, Any]:
        """get the latest block of the sidechain"""
        ret = self.rpc.getLatestBlockInfo(endpoint="blockchain")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def get_status(self) -> Dict[str, Any]:
        """gets the status of the sidechain"""
        ret = self.rpc.getStatus(endpoint="blockchain")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def get_block_info(self, blocknumber: int) -> Dict[str, Any]:
        """get the block with the specified block number of the sidechain"""
        ret = self.rpc.getBlockInfo({"blockNumber": blocknumber}, endpoint="blockchain")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def get_block_range_info(self, start_block: int, count: int) -> List[Dict[str, Any]]:
        """Get information for a consecutive range of blocks.

        This is a convenience wrapper around the ``getBlockRangeInfo`` JSON-RPC
        call. It can fetch up to 1000 blocks in one request and is much more
        efficient than calling :py:meth:`get_block_info` repeatedly.

        Parameters
        ----------
        start_block : int
            The first block number to retrieve.
        count : int
            The number of blocks to retrieve (maximum 1000).

        Returns
        -------
        List[Dict[str, Any]]
            A list where each element is a block dictionary as returned by the
            side-chain node.
        """
        ret = self.rpc.getBlockRangeInfo(
            {"startBlockNumber": start_block, "count": count}, endpoint="blockchain"
        )
        # Some nodes wrap the actual result in an additional list entry; unwrap
        # it to ensure a consistent return type for callers.
        if isinstance(ret, list) and len(ret) == 1 and isinstance(ret[0], list):
            return ret[0]
        return ret

    def get_transaction_info(self, txid: str) -> Dict[str, Any]:
        """Retrieve the specified transaction info of the sidechain"""
        ret = self.rpc.getTransactionInfo({"txid": txid}, endpoint="blockchain")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def get_contract(self, contract_name: str) -> Optional[Dict[str, Any]]:
        """Get the contract specified from the database"""
        ret = self.rpc.getContract({"name": contract_name}, endpoint="contracts")
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def find_one(
        self, contract_name: str, table_name: str, query: Dict[str, Any] = {}
    ) -> Optional[Dict[str, Any]]:
        """Get the object that matches the query from the table of the specified contract"""
        ret = self.rpc.findOne(
            {"contract": contract_name, "table": table_name, "query": query},
            endpoint="contracts",
        )
        # If rpc.findOne wraps the result in a list, unwrap it.
        if isinstance(ret, list) and len(ret) == 1 and isinstance(ret[0], dict):
            return ret[0]
        # If rpc.findOne returns a dictionary directly (expected case for a 'findOne' operation)
        elif isinstance(ret, dict):
            return ret
        # Otherwise, it's not found or an unexpected format
        return None

    def find(
        self,
        contract_name: str,
        table_name: str,
        query: Dict[str, Any] = {},
        limit: int = 1000,
        offset: int = 0,
        indexes: List[str] = [],
    ) -> List[Dict[str, Any]]:
        """Get an array of objects that match the query from the table of the specified contract"""
        ret = self.rpc.find(
            {
                "contract": contract_name,
                "table": table_name,
                "query": query,
                "limit": limit,
                "offset": offset,
                "indexes": indexes,
            },
            endpoint="contracts",
        )
        if isinstance(ret, list) and len(ret) == 1:
            return ret[0]
        else:
            return ret

    def find_all(
        self, contract_name: str, table_name: str, query: Dict[str, Any] = {}
    ) -> List[Dict[str, Any]]:
        """Get an array of objects that match the query from the table of the specified contract"""
        limit = 1000
        offset = 0
        last_result: List[Dict[str, Any]] = []
        cnt = 0
        result: List[Dict[str, Any]] = []
        while last_result is not None and len(last_result) == limit or cnt == 0:
            cnt += 1
            last_result = self.find(contract_name, table_name, query, limit=limit, offset=offset)
            if last_result is not None:
                result += last_result
                offset += limit
        return result
