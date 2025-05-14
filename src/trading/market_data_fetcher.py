from binance.client import Client
import csv

# Binance Testnet API Credentials
API_KEY = "YOUR_TESTNET_API_KEY"
API_SECRET = "YOUR_TESTNET_API_SECRET"

client = Client(API_KEY, API_SECRET, testnet=True)

# ✅ Fetch historical candlestick (K-line) data
symbol = "BTCUSDT"  # Change to desired asset
interval = Client.KLINE_INTERVAL_1HOUR

# 🔥 Fix: Define `candles` before using it
candles = client.get_klines(symbol=symbol, interval=interval, limit=100)

# ✅ Save data to CSV
with open("market_data.csv", "w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Time", "Open", "High", "Low", "Close", "Volume"])

    for candle in candles:
        writer.writerow([candle[0], candle[1], candle[2], candle[3], candle[4], candle[5]])

print("✅ Market data saved as 'market_data.csv'!")