import pandas as pd
import numpy as np
import pandas_ta as ta # This library makes adding technical indicators easy!
                        # If you don't have it, install with: pip install pandas_ta

# --- 1. Generate Sample OHLCV Data ---
print("Step 1: Generating sample OHLCV data...")

# Configuration for data generation
num_periods = 500  # Let's generate 500 hours of data (approx 20 days)
start_price = 60000 # Initial price for BTC/USD
volatility = 0.02   # Controls how much the price can change per period
base_volume = 10    # Base volume

# Create a date range for timestamps
# Using a fixed start date for reproducibility. In a real scenario, these would be actual timestamps.
timestamps = pd.date_range(start='2024-01-01 00:00:00', periods=num_periods, freq='H')

data = {'timestamp': timestamps}
df = pd.DataFrame(data)

# Simulate prices and volume
np.random.seed(42) # For reproducible random numbers
opens = [start_price]
highs = []
lows = []
closes = []
volumes = []

current_price = start_price
for i in range(num_periods):
    if i > 0:
        # Simulate next open based on previous close
        opens.append(closes[-1] * (1 + np.random.normal(0, volatility / 10))) # Smaller change for open from prev close

    # Simulate high, low, close for the current period around the open price
    open_price = opens[-1]
    change = open_price * volatility * np.random.normal(0, 1) # Main change for the period
    close_price = open_price + change

    # Ensure high is highest and low is lowest
    point1 = open_price + open_price * volatility * abs(np.random.normal(0, 0.5))
    point2 = open_price - open_price * volatility * abs(np.random.normal(0, 0.5))
    point3 = close_price + close_price * volatility * abs(np.random.normal(0, 0.3))
    point4 = close_price - close_price * volatility * abs(np.random.normal(0, 0.3))

    high_price = max(open_price, close_price, point1, point3)
    low_price = min(open_price, close_price, point2, point4)

    #