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

    # Get pool stats
    price = income_pool.calculate_price()

    print(f"\nPool Price: {price}")
else:
    print("SWAP.HIVE:INCOME pool not found")
