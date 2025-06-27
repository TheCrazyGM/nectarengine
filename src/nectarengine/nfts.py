from __future__ import absolute_import, division, print_function, unicode_literals

from typing import Any, Dict, List, Optional

from nectarengine.api import Api
from nectarengine.nft import Nft


class Nfts(list):
    """Access the Hive-engine Nfts"""

    def __init__(self, api: Optional[Api] = None, **kwargs: Any) -> None:
        if api is None:
            self.api = Api()
        else:
            self.api = api
        self.refresh()

    def refresh(self) -> None:
        super(Nfts, self).__init__(self.get_nft_list())

    def get_nft_list(self) -> List[Dict[str, Any]]:
        """Returns all available nft as list"""
        tokens = self.api.find_all("nft", "nfts", query={})
        return tokens

    def get_nft_params(self) -> Dict[str, Any]:
        """Returns all available nft as list"""
        tokens = self.api.find_one("nft", "params", query={})
        if isinstance(tokens, list) and len(tokens) > 0:
            tokens = tokens[0]
        return tokens

    def get_symbol_list(self) -> List[str]:
        symbols: List[str] = []
        for nft in self:
            symbols.append(nft["symbol"])
        return symbols

    def get_nft(self, nft: str) -> Optional[Nft]:
        """Returns Token from given nft symbol. Is None
        when nft does not exists.
        """
        for t in self:
            if t["symbol"].lower() == nft.lower():
                return Nft(t, api=self.api)
        return None
