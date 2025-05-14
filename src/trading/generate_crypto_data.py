import pandas as pd
import numpy as np
import pandas_ta as ta # This library makes adding technical indicators easy!
                        # If you don't have it, install with: pip install pandas_ta

# --- 1. Generate Sample OHLCV Data (Corrected Version) ---
print("Step 1: Generating sample OHLCV data...")

# Configuration for data generation
num_periods = 1200  # INCREASED: Let's generate 1200 hours of data
start_price = 60000 # Initial price for BTC/USD
volatility = 0.02   # Controls how much the price can change per period
base_volume = 10    # Base volume

# Create a date range for timestamps
timestamps = pd.date_range(start='2024-01-01 00:00:00', periods=num_periods, freq='h') # Use 'h' for hourly

data = {'timestamp': timestamps}
df = pd.DataFrame(data)

# Simulate prices and volume - REVISED LOGIC
np.random.seed(42) # For reproducible random numbers

# Initialize lists
opens = []
highs = []
lows = []
closes = []
volumes = []

previous_close_price = start_price # Start with the initial price as the first "previous close"

for i in range(num_periods):
    if i == 0:
        open_price = start_price
    else:
        # Subsequent open prices are based on the previous period's actual close price
        open_price = previous_close_price * (1 + np.random.normal(0, volatility / 20)) # Smaller variance for open from prev close

    # Simulate close price for the current period
    price_change_for_period = open_price * volatility * np.random.normal(0, 1)
    close_price = open_price + price_change_for_period

    # Determine high and low for the period
    # Ensure high >= open/close and low <= open/close
    min_oc = min(open_price, close_price)
    max_oc = max(open_price, close_price)

    # High price is at least the max of open/close, plus some potential upward wick
    high_price = max_oc + abs(max_oc * volatility * np.random.normal(0, 0.5))
    # Low price is at most the min of open/close, minus some potential downward wick
    low_price = min_oc - abs(min_oc * volatility * np.random.normal(0, 0.5))

    # Just in case, ensure consistency again
    if low_price > min_oc: low_price = min_oc
    if high_price < max_oc: high_price = max_oc


    # Append calculated values for the current period
    opens.append(open_price)
    highs.append(high_price)
    lows.append(low_price)
    closes.append(close_price)

    # Simulate volume
    volume_val = base_volume + base_volume * 5 * abs(np.random.normal(0, 1))
    if open_price != 0: # Avoid division by zero if price ever became 0
        volume_val += abs(price_change_for_period / open_price) * 100
    volumes.append(volume_val)

    # Update previous_close_price for the next iteration
    previous_close_price = close_price

# Assign generated lists to DataFrame columns
df['open'] = opens
df['high'] = highs
df['low'] = lows
df['close'] = closes
df['volume'] = volumes
df['crypto_pair'] = 'BTC/USD' # Adding the crypto_pair column

print(f"Generated {len(df)} periods of sample OHLCV data.")
print(df.head())
print("\n" + "="*50 + "\n")

# --- 2. Calculate Technical Indicators ---
print("Step 2: Calculating technical indicators...")

# Ensure columns are named as pandas_ta expects for OHLCV (it's case-insensitive but good practice)
# Our generated columns 'open', 'high', 'low', 'close', 'volume' are standard.

# SMA (Simple Moving Average) - e.g., 20-period SMA
df.ta.sma(length=20, append=True, col_names=('SMA_20'))

# RSI (Relative Strength Index) - e.g., 14-period RSI
df.ta.rsi(length=14, append=True, col_names=('RSI_14'))

# MACD (Moving Average Convergence Divergence)
# This will add three columns: MACD_12_26_9, MACDh_12_26_9 (histogram), MACDs_12_26_9 (signal)
df.ta.macd(fast=12, slow=26, signal=9, append=True,
            col_names=('MACD_12_26_9', 'MACD_hist_12_26_9', 'MACD_signal_12_26_9'))

# Bollinger Bands
df.ta.bbands(length=20, std=2, append=True,
             col_names=('BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0', 'BBB_20_2.0', 'BBP_20_2.0'))


print("Technical indicators added.")
# Showing more columns to see some indicators
print(df[['timestamp', 'close', 'SMA_20', 'RSI_14', 'MACD_12_26_9']].head())
print("\n" + "="*50 + "\n")


# --- 3. Create a Target Variable ---
print("Step 3: Creating a target variable (e.g., predict next hour's closing price)...")

# Let's create a target: the closing price 1 period (1 hour) into the future.
# This is a common setup for price prediction (a regression task).
future_prediction_period = 1
df['target_future_close_price'] = df['close'].shift(-future_prediction_period)

print("Target variable 'target_future_close_price' created.")
print(df[['close', 'target_future_close_price']].head())
print("\n" + "="*50 + "\n")

# --- 4. Handle NaNs (Missing Values) ---
print("Step 4: Handling NaNs created by indicators and target shifting...")

# Technical indicators with a window (like SMA_20) will have NaNs for the first (window-1) periods.
# Shifting the target variable will create NaNs at the end of the DataFrame.
original_rows = len(df)
df.dropna(inplace=True) # Remove rows with any NaN values
rows_after_dropna = len(df)

print(f"Original rows: {original_rows}, Rows after dropping NaNs: {rows_after_dropna}")
print(f"Number of rows dropped: {original_rows - rows_after_dropna}")
print(f"Final number of rows for training: {rows_after_dropna}") # Added this line for clarity
print("NaNs handled.")
print("\n" + "="*50 + "\n")

# --- 5. Inspect the Final Dataset ---
print("Step 5: Inspecting the final dataset...")
print("Dataset Information:")
df.info()
print("\nFirst 5 rows of the final dataset:")
print(df.head())
print("\nLast 5 rows of the final dataset:")
print(df.tail())
print("\n" + "="*50 + "\n")

# --- 6. Save the Dataset to a File ---
output_filename = 'simulated_crypto_insights_dataset.csv'
df.to_csv(output_filename, index=False) # index=False is important so pandas doesn't write row numbers as a column
print(f"Step 6: Dataset saved to '{output_filename}'")

print("\n" + "="*50 + "\n")
print("Process Complete! You now have a simulated dataset with more rows.")
print("Remember to replace this with REAL historical data for actual model training.")
print("Key things for real data: source from a reliable API, handle missing data carefully, ensure chronological splits for training/validation/testing.")
