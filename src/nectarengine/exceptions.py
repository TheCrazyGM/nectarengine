# This Python file uses the following encoding: utf-8
from __future__ import absolute_import, division, print_function, unicode_literals


class TokenDoesNotExists(Exception):
    """Token does not (yet) exists"""

    pass


class NftDoesNotExists(Exception):
    """Nft does not (yet) exists"""

    pass


class TokenNotInWallet(Exception):
    """The token is not in the account wallet"""

    pass


class TransactionConfirmationError(Exception):
    """Raised when a Hive Engine transaction fails to confirm or contains errors after retries."""

    pass


class InsufficientTokenAmount(Exception):
    """Not suffienct amount for transfer in the wallet"""

    pass


class InvalidTokenAmount(Exception):
    """Invalid token amount (not fitting precision or max supply)"""

    pass


class TokenIssueNotPermitted(Exception):
    """Only the token issuer is allowed to permit new tokens"""

    pass


class MaxSupplyReached(Exception):
    """Only the token issuer is allowed to permit new tokens"""

    pass


class PoolDoesNotExist(Exception):
    """Liquidity pool does not (yet) exist"""

    pass
