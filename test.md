i have added a method to nectarengine.api with the following:

```python

def get_block_range_info(self,
    start_block: int, count: int) -> List[Dict[str, Any]]:
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
```

I would like to include the option to get the blocks in bulk, similar to what we are doing in stream_blocks.py but let's do it in stream_engine_sidechain_blocks.py to get them in 1k block chunks, to speed this up, but ONLY if a .env flag is set, because most nodes have this turned off as it's resource intensive
