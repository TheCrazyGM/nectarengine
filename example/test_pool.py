import os
import sys

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../src"))

from nectarengine.pool import LiquidityPool

# Initialize the LiquidityPool instance
pool = LiquidityPool()

# Get the SWAP.HIVE:INCOME pool
income_pool = pool.get_pool("SWAP.HIVE:INCOME")

if income_pool:
    print(f"Pool Info: {income_pool}")

    # Get liquidity positions
    positions = income_pool.get_liquidity_positions()

    print("\nLiquidity Positions:")
    for position in positions:
        print(f"Account: {position['account']}, Shares: {position['shares']}")
else:
    print("SWAP.HIVE:INCOME pool not found")
