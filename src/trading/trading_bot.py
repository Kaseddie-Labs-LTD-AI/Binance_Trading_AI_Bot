import os
import logging
import threading
import time
import pandas as pd
import numpy as np
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv

from binance.client import Client
from binance import ThreadedWebsocketManager
from binance.exceptions import BinanceAPIException

# -------------------------------------
# 1. Load Environment Variables
# -------------------------------------
load_dotenv()  # Loads your .env file
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

if not BINANCE_API_KEY or not BINANCE_SECRET_KEY:
    raise ValueError("❌ ERROR: Binance API keys are missing! Check your .env file.")

print(f"🔍 API Key Loaded: {BINANCE_API_KEY}")
print(f"🔍 Secret Key Loaded: {BINANCE_SECRET_KEY}")

# -------------------------------------
# 2. Setup Logging
# -------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info(f"🔍 API Key Loaded: {BINANCE_API_KEY[:6]}...")  # Masked for security

# -------------------------------------
# 3. Initialize Binance REST Client in TESTNET Mode with Retries
# -------------------------------------
session = requests.Session()
retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY, testnet=True)
logging.info("💻 Initialized Binance REST Client in TESTNET mode.")

# -------------------------------------
# 4. Global Variables for Live Market Price and Fallback Data
# -------------------------------------
live_price = None
# Replace the fallback_data definition with at least 14 data points.
fallback_data = pd.Series([84000, 84200, 84400, 84600, 84800, 85000, 85200, 85400, 85600, 85800, 86000, 86200, 86400, 86600])

# -------------------------------------
# 5. WebSocket Streaming for Real-Time Prices Using ThreadedWebsocketManager
# -------------------------------------
def handle_message(msg):
    global live_price
    logging.info(f"Received message: {msg}")
    if msg.get("s") == "BTCUSDT" and "p" in msg:
        try:
            live_price = float(msg["p"])
            logging.info(f"🔴 Live Market Price Updated: {live_price}")
        except ValueError:
            logging.error("❌ Received invalid price data.")
# Initialize and start the WebSocket manager (ensures the updated Testnet endpoints are used)
twm = ThreadedWebsocketManager(api_key=BINANCE_API_KEY,
                               api_secret=BINANCE_SECRET_KEY,
                               testnet=True)
twm.start()
# Subscribe to the BTCUSDT book ticker stream using the callback function
socket_key = twm.start_symbol_book_ticker_socket(callback=handle_message, symbol="BTCUSDT")
logging.info("📡 WebSocket stream started for BTCUSDT.")

# -------------------------------------
# 6. Connectivity Test Function
# -------------------------------------
def test_connectivity():
    try:
        # Test 1: Ping Binance Testnet
        client.ping()
        logging.info("✅ Ping successful! Connection to Binance Testnet established.")
        
        # Test 2: Retrieve Server Time
        server_time = client.get_server_time()
        logging.info(f"⏰ Server Time: {server_time}")
        
        # Test 3: Get Exchange Information
        exchange_info = client.get_exchange_info()
        if exchange_info:
            logging.info("ℹ️ Successfully retrieved Exchange Info from Binance Testnet.")
        else:
            logging.warning("⚠️ Exchange Info is empty. Check your connectivity or API settings.")
    except BinanceAPIException as e:
        logging.error(f"❌ Binance API Error during connectivity test: {e}")
        return False
    except Exception as e:
        logging.error(f"❌ Error during connectivity test: {e}")
        return False
    return True

# -------------------------------------
# 7. RSI Calculation Function
# -------------------------------------
def calculate_rsi(data, period=14):
    if len(data) < period:
        logging.error("❌ Not enough data for RSI calculation.")
        return pd.Series()
    
    delta = data.diff()
    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, abs(delta), 0)
    
    avg_gain = pd.Series(gain).rolling(window=period).mean()
    avg_loss = pd.Series(loss).rolling(window=period).mean()
    # Avoid division by zero by replacing zeros in loss with a small number
    avg_loss = avg_loss.replace(0, 0.0001)
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

# -------------------------------------
# 8. Trading Signal Generator
# -------------------------------------
def generate_signal(rsi_value):
    valid_rsi = rsi_value.dropna()
    if valid_rsi.empty:
        logging.error("❌ Not enough RSI data to generate a signal.")
        return "Error: Not enough data for RSI calculation."
    last_rsi = valid_rsi.iloc[-1]
    if last_rsi < 30:
        return "BUY 🚀"
    elif last_rsi > 70:
        return "SELL 🔻"
    else:
        return "HOLD"

# -------------------------------------
# 9. Trade Execution Function
# -------------------------------------
def execute_trade(signal, symbol="BTCUSDT", quantity=0.001):
    try:
        if signal == "BUY 🚀":
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
            logging.info(f"✅ BUY Order Executed: {order}")
            return "✅ BUY Order Executed"
        elif signal == "SELL 🔻":
            order = client.order_market_sell(symbol=symbol, quantity=quantity)
            logging.info(f"✅ SELL Order Executed: {order}")
            return "✅ SELL Order Executed"
        else:
            logging.info("🛑 No trade executed.")
            return "🛑 No trade executed."
    except BinanceAPIException as e:
        error_code = getattr(e, 'code', 'Unknown')
        logging.error(f"❌ Binance API Error (code {error_code}): {e}")
        return f"❌ Trade Execution Failed: {e}"

# -------------------------------------
# 10. Function to Run the Trading Bot
# -------------------------------------
def run_trading_bot():
    """Executes trading bot logic based on live price data (or fallback data if live data is missing)."""
    symbol = "BTCUSDT"
    # Allow time for the WebSocket stream to update the live price
    time.sleep(5)
    logging.info("🛡 Running trading bot in TESTNET mode.")
    
    if live_price is None:
        logging.warning("⚠️ Live price not available. Using fallback data for RSI calculation.")
        price_data = fallback_data
    else:
        # For demo purposes, create a series of 14 repeated live prices to simulate historical data
        price_data = pd.Series([live_price] * 14)
    
    rsi_values = calculate_rsi(price_data)
    signal = generate_signal(rsi_values)
    logging.info(f"💡 Trading Signal: {signal}")
    result = execute_trade(signal, symbol)
    logging.info(result)

# -------------------------------------
# 11. Main Execution: Connectivity Test + Trading Bot
# -------------------------------------
if __name__ == "__main__":
    logging.info("🔬 Starting connectivity tests...")
    if test_connectivity():
        input("✅ Connectivity test passed! Press Enter to run the trading bot (or Ctrl+C to exit)...")
        try:
            run_trading_bot()
        except Exception as e:
            logging.error(f"❌ An unexpected error occurred while running the trading bot: {e}")
        finally:
           logging.info("🔚 Shutting down WebSocket Manager...")