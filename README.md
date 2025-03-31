# nectarengine

Python tools for obtaining and processing hive engine tokens

[![Latest Version](https://img.shields.io/pypi/v/nectarengine.svg)](https://pypi.python.org/pypi/nectarengine/)

[![Python Versions](https://img.shields.io/pypi/pyversions/nectarengine.svg)](https://pypi.python.org/pypi/nectarengine/)

## Installation

```bash
pip install nectarengine
```

## Commands

Get the latest block of the sidechain

```python
from nectarengine.api import Api
api = Api()
print(api.get_latest_block_info())
```

Get the block with the specified block number of the sidechain

```python
from nectarengine.api import Api
api = Api()
print(api.get_block_info(1910))
```

Retrieve the specified transaction info of the sidechain

```python
from nectarengine.api import Api
api = Api()
print(api.get_transaction_info("e6c7f351b3743d1ed3d66eb9c6f2c102020aaa5d"))
```

Get the contract specified from the database

```python
from nectarengine.api import Api
api = Api()
print(api.get_contract("tokens"))
```

Get an array of objects that match the query from the table of the specified contract

```python
from nectarengine.api import Api
api = Api()
print(api.find("tokens", "tokens"))
```

Get the object that matches the query from the table of the specified contract

```python
from nectarengine.api import Api
api = Api()
print(api.find_one("tokens", "tokens"))
```

Get the transaction history for an account and a token

```python
from nectarengine.api import Api
api = Api()
print(api.get_history("thecrazygm", "INCOME"))
```

## Token transfer

```python
from nectar import Hive
from nectarengine.wallet import Wallet
hv = Hive(keys=["5xx"])
wallet = Wallet("test_user", blockchain_instance=hv)
wallet.transfer("test1",1,"TST", memo="This is a test")
```

## Buy/Sell

### Create a buy order

```python
from nectar import Hive
from nectarengine.market import Market
hv = Hive(keys=["5xx"])
m=Market(blockchain_instance=hv)
m.buy("test_user", 1, "TST", 9.99)
```

### Create a sell order

```python
from nectar import Hive
from nectarengine.market import Market
hv = Hive(keys=["5xx"])
m=Market(blockchain_instance=hv)
m.sell("test_user", 1, "TST", 9.99)
```

### Cancel a buy order

```python
from nectar import Hive
from nectarengine.market import Market
hv = Hive(keys=["5xx"])
m=Market(blockchain_instance=hv)
open_buy_orders = m.get_buy_book("TST", "test_user")
m.cancel("test_user", "buy", open_buy_orders[0]["_id"])
```

### Cancel a sell order

```python
from nectar import Hive
from nectarengine.market import Market
hv = Hive(keys=["5xx"])
m=Market(blockchain_instance=hv)
open_sell_orders = m.get_sell_book("TST", "test_user")
m.cancel("test_user", "sell", open_sell_orders[0]["_id"])
```

### Deposit Hive

```python
from nectar import Hive
from nectarengine.market import Market
hv = Hive(keys=["5xx"])
m=Market(blockchain_instance=hv)
m.deposit("test_user", 10)
```

### Withdrawal

```python
from nectar import Hive
from nectarengine.market import Market
hv = Hive(keys=["5xx"])
m=Market(blockchain_instance=hv)
m.withdraw("test_user", 10)
```
