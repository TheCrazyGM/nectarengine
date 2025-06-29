from __future__ import absolute_import, division, print_function, unicode_literals

import decimal
from typing import Any, Dict, List, Optional

from nectar.account import Account
from nectar.instance import shared_blockchain_instance

from nectarengine.api import Api
from nectarengine.exceptions import (
    InsufficientTokenAmount,
    InvalidTokenAmount,
    TokenDoesNotExists,
    TokenNotInWallet,
)
from nectarengine.tokenobject import Token
from nectarengine.tokens import Tokens
from nectarengine.wallet import Wallet


class Market(list):
    """Access the hive-engine market

    :param Hive blockchain_instance: Hive
           instance
    """

    def __init__(
        self, api: Optional[Api] = None, blockchain_instance: Optional[Any] = None
    ) -> None:
        if api is None:
            self.api = Api()
        else:
            self.api = api
        self.blockchain = blockchain_instance or shared_blockchain_instance()
        self.tokens = Tokens(api=self.api)
        self.ssc_id = "ssc-mainnet-hive"
        self.refresh()

    def refresh(self) -> None:
        super(Market, self).__init__(self.get_metrics())

    def set_id(self, ssc_id: str) -> None:
        """Sets the ssc id (default is ssc-mainnet-hive)"""
        self.ssc_id = ssc_id

    def get_metrics(self) -> List[Dict[str, Any]]:
        """Returns all token within the wallet as list"""
        metrics = self.api.find("market", "metrics", query={})
        return metrics

    def get_buy_book(
        self, symbol: str, account: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Returns the buy book for a given symbol. When account is set,
        the order book from the given account is shown.
        """
        if self.tokens.get_token(symbol) is None:
            raise TokenDoesNotExists("%s does not exists" % symbol)
        if account is None:
            buy_book = self.api.find(
                "market", "buyBook", query={"symbol": symbol.upper()}, limit=limit, offset=offset
            )
        else:
            buy_book = self.api.find(
                "market",
                "buyBook",
                query={"symbol": symbol.upper(), "account": account},
                limit=limit,
                offset=offset,
            )
        return buy_book

    def get_sell_book(
        self, symbol: str, account: Optional[str] = None, limit: int = 100, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Returns the sell book for a given symbol. When account is set,
        the order book from the given account is shown.
        """
        if self.tokens.get_token(symbol) is None:
            raise TokenDoesNotExists("%s does not exists" % symbol)
        if account is None:
            sell_book = self.api.find(
                "market", "sellBook", query={"symbol": symbol.upper()}, limit=limit, offset=offset
            )
        else:
            sell_book = self.api.find(
                "market",
                "sellBook",
                query={"symbol": symbol.upper(), "account": account},
                limit=limit,
                offset=offset,
            )
        return sell_book

    def get_trades_history(
        self, symbol: str, account: Optional[str] = None, limit: int = 30, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Returns the trade history for a given symbol. When account is set,
        the trade history from the given account is shown.
        """
        if self.tokens.get_token(symbol) is None:
            raise TokenDoesNotExists("%s does not exists" % symbol)
        if account is None:
            trades_history = self.api.find(
                "market",
                "tradesHistory",
                query={"symbol": symbol.upper()},
                limit=limit,
                offset=offset,
            )
        else:
            trades_history = self.api.find(
                "market",
                "tradesHistory",
                query={"symbol": symbol.upper(), "account": account},
                limit=limit,
                offset=offset,
            )
        return trades_history

    def withdraw(self, account: str, amount: float) -> Dict[str, Any]:
        """Widthdraw SWAP.HIVE to account as HIVE.

        :param str account: account name
        :param float amount: Amount to withdraw

        Withdraw example:

        .. code-block:: python

            from nectarengine.market import Market
            from nectar import Hive
            active_wif = "5xxxx"
            hv = Hive(keys=[active_wif])
            market = Market(blockchain_instance=hv)
            market.withdraw("test", 1)
        """
        wallet = Wallet(account, api=self.api, blockchain_instance=self.blockchain)
        token_in_wallet = wallet.get_token("SWAP.HIVE")
        if token_in_wallet is None:
            raise TokenNotInWallet("%s is not in wallet." % "SWAP.HIVE")
        if float(token_in_wallet["balance"]) < float(amount):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(token_in_wallet["balance"]))
        token = Token("SWAP.HIVE", api=self.api)
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount(
                "Amount to transfer is below token precision of %d" % token["precision"]
            )
        contract_payload = {"quantity": str(quant_amount)}
        json_data = {
            "contractName": "hivepegged",
            "contractAction": "withdraw",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[account])
        return tx

    def deposit(self, account: str, amount: float) -> Dict[str, Any]:
        """Deposit HIVE to market in exchange for SWAP.HIVE.

        :param str account: account name
        :param float amount: Amount to deposit

        Deposit example:

        .. code-block:: python

            from nectarengine.market import Market
            from nectar import Hive
            active_wif = "5xxxx"
            hv = Hive(keys=[active_wif])
            market = Market(blockchain_instance=hv)
            market.deposit("test", 1)
        """
        acc = Account(account, blockchain_instance=self.blockchain)
        hive_balance = acc.get_balance("available", "HIVE")
        if float(hive_balance) < float(amount):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(hive_balance))
        json_data = (
            '{"id":"'
            + self.ssc_id
            + '","json":{"contractName":"hivepegged","contractAction":"buy","contractPayload":{}}}'
        )
        tx = acc.transfer("honey-swap", amount, "HIVE", memo=json_data)
        return tx

    def buy(self, account: str, amount: float, symbol: str, price: float) -> Dict[str, Any]:
        """Buy token for given price.

        :param str account: account name
        :param float amount: Amount to withdraw
        :param str symbol: symbol
        :param float price: price

        Buy example:

        .. code-block:: python

            from nectarengine.market import Market
            from nectar import Hive
            active_wif = "5xxxx"
            hv = Hive(keys=[active_wif])
            market = Market(blockchain_instance=hv)
            market.buy("test", 1, "BEE", 0.95)
        """
        wallet = Wallet(account, api=self.api, blockchain_instance=self.blockchain)
        token_in_wallet = wallet.get_token("SWAP.HIVE")
        if token_in_wallet is None:
            raise TokenNotInWallet("%s is not in wallet." % "SWAP.HIVE")
        if float(token_in_wallet["balance"]) < float(amount) * float(price):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(token_in_wallet["balance"]))

        token = Token(symbol, api=self.api)
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount(
                "Amount to transfer is below token precision of %d" % token["precision"]
            )
        contract_payload = {
            "symbol": symbol.upper(),
            "quantity": str(quant_amount),
            "price": str(price),
        }
        json_data = {
            "contractName": "market",
            "contractAction": "buy",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[account])
        return tx

    def sell(self, account: str, amount: float, symbol: str, price: float) -> Dict[str, Any]:
        """Sell token for given price.

        :param str account: account name
        :param float amount: Amount to withdraw
        :param str symbol: symbol
        :param float price: price

        Sell example:

        .. code-block:: python

            from nectarengine.market import Market
            from nectar import Hive
            active_wif = "5xxxx"
            hv = Hive(keys=[active_wif])
            market = Market(blockchain_instance=hv)
            market.sell("test", 1, "BEE", 0.95)
        """
        wallet = Wallet(account, api=self.api, blockchain_instance=self.blockchain)
        token_in_wallet = wallet.get_token(symbol)
        if token_in_wallet is None:
            raise TokenNotInWallet("%s is not in wallet." % symbol)
        if float(token_in_wallet["balance"]) < float(amount):
            raise InsufficientTokenAmount("Only %.3f in wallet" % float(token_in_wallet["balance"]))

        token = Token(symbol, api=self.api)
        quant_amount = token.quantize(amount)
        if quant_amount <= decimal.Decimal("0"):
            raise InvalidTokenAmount(
                "Amount to transfer is below token precision of %d" % token["precision"]
            )
        contract_payload = {
            "symbol": symbol.upper(),
            "quantity": str(quant_amount),
            "price": str(price),
        }
        json_data = {
            "contractName": "market",
            "contractAction": "sell",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[account])
        return tx

    def cancel(self, account: str, order_type: str, order_id: int) -> Dict[str, Any]:
        """Cancel buy/sell order.

        :param str account: account name
        :param str order_type: sell or buy
        :param int order_id: order id

        Cancel example:

        .. code-block:: python

            from nectarengine.market import Market
            from nectar import Hive
            active_wif = "5xxxx"
            hv = Hive(keys=[active_wif])
            market = Market(blockchain_instance=hv)
            market.sell("test", "sell", 12)
        """

        contract_payload = {"type": order_type, "id": order_id}
        json_data = {
            "contractName": "market",
            "contractAction": "cancel",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[account])
        return tx
