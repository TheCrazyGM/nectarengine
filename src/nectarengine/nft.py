from __future__ import absolute_import, division, print_function, unicode_literals

from typing import Any, Dict, List, Optional, Union

from nectar.instance import shared_blockchain_instance

from nectarengine.api import Api
from nectarengine.exceptions import NftDoesNotExists


class Nft(dict):
    """Access the hive-engine Nfts"""

    def __init__(
        self,
        symbol: Union[str, Dict[str, Any]],
        api: Optional[Api] = None,
        blockchain_instance: Optional[Any] = None,
    ) -> None:
        if api is None:
            self.api = Api()
        else:
            self.api = api
        self.blockchain = blockchain_instance or shared_blockchain_instance()
        self.ssc_id = "ssc-mainnet-hive"
        if isinstance(symbol, dict):
            self.symbol = symbol["symbol"]
            super(Nft, self).__init__(symbol)
        else:
            self.symbol = symbol.upper()
            self.refresh()

    def refresh(self) -> None:
        info = self.get_info()
        if info is None:
            raise NftDoesNotExists("Nft %s does not exists!" % self.symbol)
        super(Nft, self).__init__(info)

    def get_info(self) -> Optional[Dict[str, Any]]:
        """Returns information about the nft"""
        token = self.api.find_one("nft", "nfts", query={"symbol": self.symbol})
        if token and isinstance(token, list) and len(token) > 0:
            return token[0]
        elif token and isinstance(token, dict):
            return token
        else:
            return None

    @property
    def properties(self) -> List[str]:
        return list(self["properties"].keys())

    @property
    def issuer(self) -> str:
        return self["issuer"]

    def get_property(self, property_name: str) -> List[Dict[str, Any]]:
        """Returns all token properties"""
        return self.api.find_all(
            "nft", "%sinstances" % self.symbol, query={"properties.name": property_name}
        )

    def get_collection(self, account: str) -> List[Dict[str, Any]]:
        """Get NFT collection"""
        tokens = self.api.find_all("nft", "%sinstances" % self.symbol, query={"account": account})
        return tokens

    def get_id(self, _id: int) -> Optional[Dict[str, Any]]:
        """Get info about a token"""
        tokens = self.api.find_one("nft", "%sinstances" % self.symbol, query={"_id": _id})
        if tokens and isinstance(tokens, list) and len(tokens) > 0:
            return tokens[0]
        elif tokens and isinstance(tokens, dict):
            return tokens
        return None

    def get_trade_history(
        self, query: Dict[str, Any] = {}, limit: int = -1, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Returns market information
        :param dict query: can be priceSymbol, timestamp
        """
        if limit < 0 or limit > 1000:
            return self.api.find_all("nftmarket", "%stradesHistory" % self.symbol, query=query)
        else:
            return self.api.find(
                "nftmarket",
                "%stradesHistory" % self.symbol,
                query=query,
                limit=limit,
                offset=offset,
            )

    def get_open_interest(
        self, query: Dict[str, Any] = {}, limit: int = -1, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Returns open interests
        :param dict query: side, priceSymbol, grouping
        """
        if limit < 0 or limit > 1000:
            return self.api.find_all("nftmarket", "%sopenInterest" % self.symbol, query=query)
        else:
            return self.api.find(
                "nftmarket", "%sopenInterest" % self.symbol, query=query, limit=limit, offset=offset
            )

    def get_sell_book(
        self, query: Dict[str, Any] = {}, limit: int = -1, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Returns the sell book
        :param dict query: can be ownedBy, account, nftId, grouping, priceSymbol
        """
        if limit < 0 or limit > 1000:
            return self.api.find_all("nftmarket", "%ssellBook" % self.symbol, query=query)
        else:
            return self.api.find(
                "nftmarket", "%ssellBook" % self.symbol, query=query, limit=limit, offset=offset
            )

    def update_url(self, url: str) -> Dict[str, Any]:
        """Updates the NFT project website

        :param str url: new url

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            active_wif = "5xxxx"
            hive = Hive(keys=[active_wif])
            nft = Nft("STAR", blockchain_instance=hive)
            nft.update_url("https://new_url.com")
        """
        contract_payload = {"symbol": self.symbol.upper(), "url": url}
        json_data = {
            "contractName": "nft",
            "contractAction": "updateUrl",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(
            self.ssc_id, json_data, required_posting_auths=[self["issuer"]]
        )
        return tx

    def update_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Updates the metadata of a token.

        :param dict medadata: new medadata

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            active_wif = "5xxxx"
            hive = Hive(keys=[active_wif])
            nft = Nft("STAR", blockchain_instance=hive)
            metadata = {"url": "https://mycoolnft.com",
                        "icon": "https://mycoolnft.com/token.jpg",
                        "desc": "This NFT will rock your world! It has features x, y, and z. So cool!"}
            nft.update_metadata(metadata)
        """
        contract_payload = {"symbol": self.symbol.upper(), "metadata": metadata}
        json_data = {
            "contractName": "nft",
            "contractAction": "updateMetadata",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(
            self.ssc_id, json_data, required_posting_auths=[self["issuer"]]
        )
        return tx

    def update_name(self, name: str) -> Dict[str, Any]:
        """Updates the user friendly name of an NFT.

        :param str name: new name

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            posting_wif = "5xxxx"
            hive = Hive(keys=[posting_wif])
            nft = Nft("STAR", blockchain_instance=hive)
            nft.update_name("My Awesome NFT")
        """
        contract_payload = {"symbol": self.symbol.upper(), "name": name}
        json_data = {
            "contractName": "nft",
            "contractAction": "updateName",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(
            self.ssc_id, json_data, required_posting_auths=[self["issuer"]]
        )
        return tx

    def update_org_name(self, org_name: str) -> Dict[str, Any]:
        """Updates the name of the company/organization that manages an NFT.

        :param str org_name: new org_name

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            posting_wif = "5xxxx"
            hive = Hive(keys=[posting_wif])
            nft = Nft("STAR", blockchain_instance=hive)
            nft.update_org_name("Nifty Company Inc")
        """
        contract_payload = {"symbol": self.symbol.upper(), "orgName": org_name}
        json_data = {
            "contractName": "nft",
            "contractAction": "updateOrgName",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(
            self.ssc_id, json_data, required_posting_auths=[self["issuer"]]
        )
        return tx

    def update_product_name(self, product_name: str) -> Dict[str, Any]:
        """Updates the name of the company/organization that manages an NFT.

        :param str org_name: new org_name

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            posting_wif = "5xxxx"
            hive = Hive(keys=[posting_wif])
            nft = Nft("STAR", blockchain_instance=hive)
            nft.update_product_name("Acme Exploding NFTs")
        """
        contract_payload = {"symbol": self.symbol.upper(), "productName": product_name}
        json_data = {
            "contractName": "nft",
            "contractAction": "updateProductName",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(
            self.ssc_id, json_data, required_posting_auths=[self["issuer"]]
        )
        return tx

    def add_authorized_issuing_accounts(self, accounts: List[str]) -> Dict[str, Any]:
        """Adds Hive accounts to the list of accounts that are authorized to issue
        new tokens on behalf of the NFT owner.

         :param list accounts: A list of hive accounts to add to the authorized list

         example:

         .. code-block:: python

             from nectarengine.nft import Nft
             from nectar import Hive
             active_wif = "5xxxx"
             hive = Hive(keys=[active_wif])
             nft = Nft("TESTNFT", blockchain_instance=hive)
             nft.add_authorized_issuing_accounts(["satoshi","aggroed","cryptomancer"])
        """
        contract_payload = {"symbol": self.symbol.upper(), "accounts": accounts}
        json_data = {
            "contractName": "nft",
            "contractAction": "addAuthorizedIssuingAccounts",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx

    def add_authorized_issuing_contracts(self, contracts: List[str]) -> Dict[str, Any]:
        """Adds smart contracts to the list of contracts that are authorized to issue
        new tokens on behalf of the NFT owner.

         :param list contracts: A list of smart contracts t to add to the authorized list

         example:

         .. code-block:: python

             from nectarengine.nft import Nft
             from nectar import Hive
             active_wif = "5xxxx"
             hive = Hive(keys=[active_wif])
             nft = Nft("TESTNFT", blockchain_instance=hive)
             nft.add_authorized_issuing_contracts(["mycontract","anothercontract","mygamecontract"])
        """
        contract_payload = {"symbol": self.symbol.upper(), "contracts": contracts}
        json_data = {
            "contractName": "nft",
            "contractAction": "addAuthorizedIssuingContracts",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx

    def remove_authorized_issuing_accounts(self, accounts: List[str]) -> Dict[str, Any]:
        """Removes Hive accounts from the list of accounts that are authorized to issue
        new tokens on behalf of the NFT owner.

         :param list accounts: A list of hive accounts to remove from the authorized list

         example:

         .. code-block:: python

             from nectarengine.nft import Nft
             from nectar import Hive
             active_wif = "5xxxx"
             hive = Hive(keys=[active_wif])
             nft = Nft("TESTNFT", blockchain_instance=hive)
             nft.remove_authorized_issuing_accounts(["aggroed","cryptomancer"])
        """
        contract_payload = {"symbol": self.symbol.upper(), "accounts": accounts}
        json_data = {
            "contractName": "nft",
            "contractAction": "removeAuthorizedIssuingAccounts",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx

    def remove_authorized_issuing_contracts(self, contracts: List[str]) -> Dict[str, Any]:
        """Remvoes smart contracts from the list of contracts that are authorized to issue
        new tokens on behalf of the NFT owner.

         :param list contracts: A list of smart contracts to remove from the authorized list

         example:

         .. code-block:: python

             from nectarengine.nft import Nft
             from nectar import Hive
             active_wif = "5xxxx"
             hive = Hive(keys=[active_wif])
             nft = Nft("TESTNFT", blockchain_instance=hive)
             nft.remove_authorized_issuing_contracts(["mycontract","mygamecontract"])
        """
        contract_payload = {"symbol": self.symbol.upper(), "contracts": contracts}
        json_data = {
            "contractName": "nft",
            "contractAction": "removeAuthorizedIssuingContracts",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx

    def transfer_ownership(self, to: str) -> Dict[str, Any]:
        """Transfers ownership of an NFT from the current owner to another Hive account.

        :param str to: Hive accounts to become the new owner

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            active_wif = "5xxxx"
            hive = Hive(keys=[active_wif])
            nft = Nft("TESTNFT", blockchain_instance=hive)
            nft.transfer_ownership("aggroed")
        """
        contract_payload = {"symbol": self.symbol.upper(), "to": to}
        json_data = {
            "contractName": "nft",
            "contractAction": "transferOwnership",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx

    def add_property(
        self,
        name: str,
        prop_type: str,
        is_read_only: Optional[bool] = None,
        authorized_editing_accounts: Optional[List[str]] = None,
        authorized_editing_contracts: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Adds a new data property schema to an existing NFT definition

        :param str name: Name of the new property
        :param str prop_type: must be number, string or boolean
        :param bool is_read_only:
        :param list authorized_editing_accounts:
        :param list authorized_editing_contracts:

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            active_wif = "5xxxx"
            hive = Hive(keys=[active_wif])
            nft = Nft("TESTNFT", blockchain_instance=hive)
            nft.add_property("color", "string")
        """
        contract_payload: Dict[str, Any] = {
            "symbol": self.symbol.upper(),
            "name": name,
            "type": prop_type,
        }
        if is_read_only is not None:
            contract_payload["isReadOnly"] = is_read_only
        if authorized_editing_accounts is not None:
            contract_payload["authorizedEditingAccounts"] = authorized_editing_accounts
        if authorized_editing_contracts is not None:
            contract_payload["authorizedEditingContracts"] = authorized_editing_contracts
        json_data = {
            "contractName": "nft",
            "contractAction": "addProperty",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx

    def set_property_permissions(
        self, name: str, accounts: Optional[List[str]] = None, contracts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Can be used after calling the addProperty action to change the lists of
        authorized editing accounts & contracts for a given data property.

         :param str name: Name of the new property
         :param list accounts:
         :param list contracts:

         example:

         .. code-block:: python

             from nectarengine.nft import Nft
             from nectar import Hive
             active_wif = "5xxxx"
             hive = Hive(keys=[active_wif])
             nft = Nft("TESTNFT", blockchain_instance=hive)
             nft.set_property_permissions("color", accounts=["cryptomancer","marc"])
        """
        contract_payload: Dict[str, Any] = {"symbol": self.symbol.upper(), "name": name}
        if accounts is not None:
            contract_payload["accounts"] = accounts
        if contracts is not None:
            contract_payload["contracts"] = contracts
        json_data = {
            "contractName": "nft",
            "contractAction": "setPropertyPermissions",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx

    def set_properties(
        self,
        nfts: List[Dict[str, Any]],
        from_type: Optional[str] = None,
        authorized_account: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Edits one or more data properties on one or more instances of an NFT.

        :param list nfts:
        :param str from_type:
        :param str authorized_account: authorized hive account

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            posting_wif = "5xxxx"
            hive = Hive(keys=[posting_wif])
            nft = Nft("TESTNFT", blockchain_instance=hive)
            nft.set_properties([{ "id":"573", "properties": {"color": "red", "level": 2}}])
        """
        if authorized_account is None:
            authorized_account = self["issuer"]
        contract_payload: Dict[str, Any] = {"symbol": self.symbol.upper(), "nfts": nfts}
        if from_type is not None:
            contract_payload["fromType"] = from_type
        json_data = {
            "contractName": "nft",
            "contractAction": "setPropertyPermissions",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(
            self.ssc_id, json_data, required_posting_auths=[authorized_account]
        )
        return tx

    def set_group_by(self, properties: List[str]) -> Dict[str, Any]:
        """Can be used after calling the addProperty action to change the lists of
        authorized editing accounts & contracts for a given data property.

         :param list properties:

         example:

         .. code-block:: python

             from nectarengine.nft import Nft
             from nectar import Hive
             active_wif = "5xxxx"
             hive = Hive(keys=[active_wif])
             nft = Nft("TESTNFT", blockchain_instance=hive)
             nft.set_group_by(["level", "isFood"])
        """
        contract_payload = {"symbol": self.symbol.upper(), "properties ": properties}
        json_data = {
            "contractName": "nft",
            "contractAction": "setGroupBy",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx

    def update_property_definition(
        self,
        name: str,
        new_name: Optional[str] = None,
        prop_type: Optional[str] = None,
        is_read_only: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Updates the schema of a data property.
        This action can only be called if no tokens for this NFT have been issued yet.

        :param str name: Name of the new property
        :param str name:
        :param str new_name:
        :param str prop_type:
        :param bool is_read_only:

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            active_wif = "5xxxx"
            hive = Hive(keys=[active_wif])
            nft = Nft("TESTNFT", blockchain_instance=hive)
            nft.update_property_definition("color", new_name="Color")
        """
        contract_payload: Dict[str, Any] = {"symbol": self.symbol.upper(), "name": name}
        if new_name is not None:
            contract_payload["newName"] = new_name
        if prop_type is not None:
            contract_payload["type"] = prop_type
        if is_read_only is not None:
            contract_payload["isReadOnly"] = is_read_only
        json_data = {
            "contractName": "nft",
            "contractAction": "updatePropertyDefinition",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx

    def issue(
        self,
        to: str,
        fee_symbol: str,
        from_type: Optional[str] = None,
        to_type: Optional[str] = None,
        lock_tokens: Optional[Dict[str, Any]] = None,
        lock_nfts: Optional[List[str]] = None,
        properties: Optional[Dict[str, Any]] = None,
        authorized_account: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Issues a new instance of an NFT to a Hive account or smart contract.

        :param str to:
        :param str fee_symbol:
        :param str from_type:
        :param str to_type:
        :param dict lock_tokens:
        :param list lock_nfts:
        :param dict properties:
        :param str authorized_account: authorized hive account

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            active_wif = "5xxxx"
            hive = Hive(keys=[active_wif])
            nft = Nft("TESTNFT", blockchain_instance=hive)
            nft.issue("aggroed", "PAL")
        """
        if authorized_account is None:
            authorized_account = self["issuer"]
        contract_payload: Dict[str, Any] = {
            "symbol": self.symbol.upper(),
            "to": to,
            "feeSymbol": fee_symbol,
        }
        if from_type is not None:
            contract_payload["fromType"] = from_type
        if to_type is not None:
            contract_payload["toType"] = to_type
        if lock_tokens is not None:
            contract_payload["lockTokens"] = lock_tokens
        if lock_nfts is not None:
            contract_payload["lockNfts"] = lock_nfts
        if properties is not None:
            contract_payload["properties"] = properties

        json_data = {
            "contractName": "nft",
            "contractAction": "issue",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(
            self.ssc_id, json_data, required_auths=[authorized_account]
        )
        return tx

    def issue_multiple(
        self, instances: List[Dict[str, Any]], authorized_account: Optional[str] = None
    ) -> Dict[str, Any]:
        """Issues multiple NFT instances at once.

        :param list instances:
        :param str authorized_account: authorized hive account

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            active_wif = "5xxxx"
            hive = Hive(keys=[active_wif])
            nft = Nft("TESTNFT", blockchain_instance=hive)
            nft.issue_multiple([{"fromType": "contract", "symbol": "TSTNFT", "to": "marc", "feeSymbol": "PAL"}])
        """
        if authorized_account is None:
            authorized_account = self["issuer"]
        contract_payload = {"instances": instances}
        json_data = {
            "contractName": "nft",
            "contractAction": "issueMultiple",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(
            self.ssc_id, json_data, required_auths=[authorized_account]
        )
        return tx

    def enable_delegation(self, undelegation_cooldown: int) -> Dict[str, Any]:
        """Enables the delegation feature for a NFT

        :param int undelegation_cooldown: Cooldown in days

        example:

        .. code-block:: python

            from nectarengine.nft import Nft
            from nectar import Hive
            active_wif = "5xxxx"
            hive = Hive(keys=[active_wif])
            nft = Nft("TESTNFT", blockchain_instance=hive)
            nft.enable_delegation(30)
        """
        contract_payload = {
            "symbol": self.symbol.upper(),
            "undelegationCooldown": undelegation_cooldown,
        }
        json_data = {
            "contractName": "nft",
            "contractAction": "enableDelegation",
            "contractPayload": contract_payload,
        }
        assert self.blockchain.is_hive
        tx = self.blockchain.custom_json(self.ssc_id, json_data, required_auths=[self["issuer"]])
        return tx
