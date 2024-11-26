class PredictionMarket:
    def __init__(self, market_name, threshold, initial_liquidity=None):
        self.initial_liquidity = initial_liquidity
        self.market_name = market_name
        self.threshold = threshold
        self.over_pool = initial_liquidity  # Initial liquidity for "Over Threshold"
        self.under_pool = initial_liquidity  # Initial liquidity for "Under Threshold"
        self.total_over_shares = initial_liquidity  # Initial shares for "Over Threshold"
        self.total_under_shares = initial_liquidity  # Initial shares for "Under Threshold"

    def buy_shares(self, side, amount):
        """
        Buy shares for a given side ('over' or 'under') with the specified amount of funds.
        Adjusts prices using the constant product formula.
        """
        if side not in ["over", "under"]:
            raise ValueError("Side must be 'over' or 'under'")
        prices = self.current_price()

        if side == "over":
            # Update "Over" pool with the new funds
            shares = amount * prices["over"]
            # Shares received are proportional to the change in the "Under" pool
            # shares = amount / (self.over_pool / self.total_over_shares)

            self.over_pool =  self.over_pool + shares
            self.total_over_shares += shares
        else:  # side == "under"

            # Shares received are proportional to the change in the "Over" pool
            # shares = amount / (self.under_pool / self.total_under_shares)
            shares = amount * prices["under"]
            # Update pool sizes
            self.under_pool = self.under_pool + shares
            self.total_under_shares += shares

        return shares

    def current_price(self):
        """
        Get the current price of 'over' and 'under' based on the pool sizes.
        """
        total_liquidity = self.over_pool + self.under_pool
        return {
            "over": self.over_pool / total_liquidity,
            "under": self.under_pool / total_liquidity,
        }

    def resolve_market(self, result):
        """
        Resolve the market by specifying the winning outcome ('over' or 'under').
        Returns the payout per share for the winning side.
        """
        if result not in ["over", "under"]:
            raise ValueError("Result must be 'over' or 'under'")
        
        if result == "over":

            payout_pool = self.under_pool - self.initial_liquidity
            winning_shares_amount = self.total_over_shares - self.initial_liquidity
            payout_per_share = payout_pool / winning_shares_amount if winning_shares_amount > 0 else 0
        else:

            payout_pool = self.over_pool - self.initial_liquidity
            winning_shares_amount = self.total_under_shares - self.initial_liquidity
            payout_per_share = payout_pool / winning_shares_amount if winning_shares_amount > 0 else 0


        return payout_per_share, payout_pool, winning_shares_amount


class MultiMarketSystem:
    def __init__(self):
        self.markets = {}

    def create_market(self, market_name, threshold, initial_liquidity=None):
        if market_name in self.markets:
            raise ValueError(f"Market '{market_name}' already exists.")
        self.markets[market_name] = PredictionMarket(market_name, threshold, initial_liquidity)

    def get_market(self, market_name):
        if market_name not in self.markets:
            raise ValueError(f"Market '{market_name}' not found.")
        return self.markets[market_name]

    def list_markets(self):
        return {name: market.threshold for name, market in self.markets.items()}


if __name__ == "__main__":
    # Example Usage
    
    # Initialize the multi-market system
    system = MultiMarketSystem()
    
    # Create a market with initial liquidity
    system.create_market("Market 1", threshold=5000, initial_liquidity=1000)
    
    # Access the market
    market1 = system.get_market("Market 1")
    
    # Check initial prices
    print("Initial Prices:", market1.current_price())
    
    # Buy shares
    print("Buying 100 units for 'over' in Market 1")
    shares_over = market1.buy_shares("over", 100)
    print(f"Received {shares_over:.2f} shares.")
    
    # Check updated prices
    print("Current Prices:", market1.current_price())
    
    print("Buying 100 units for 'under' in Market 1")
    shares_under = market1.buy_shares("under", 100)
    print(f"Received {shares_under:.2f} shares.")
    
    # Check updated prices again
    print("Updated Prices:", market1.current_price())
    
    print("Buying 100 units for 'under' in Market 1")
    shares_under = market1.buy_shares("under", 100)
    print(f"Received {shares_under:.2f} shares.")
    
    # Check updated prices again
    print("Updated Prices:", market1.current_price())
    
    result = "under"
    
    # Resolve the market
    print(f"Resolving Market 1 with '{result}' as the winner.")
    payout_per_share, payout_pool, winning_shares_amount = market1.resolve_market(result)

    print(f"Payout per '{result}' share: {payout_per_share}")
    print(f"Total payout: {payout_pool}")
    print(f"Total winning shares: {winning_shares_amount}")

    # List all markets
    print("All Markets:", system.list_markets())
