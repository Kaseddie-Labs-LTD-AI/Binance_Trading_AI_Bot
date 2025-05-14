import os
import pandas as pd
import numpy as np
import ta  # Technical Analysis library
from binance.client import Client
from trading_ai import get_market_insights  # AI handler for market analysis
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY")

# Initialize Binance API client
client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)

# List of trading pairs to analyze
trading_pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]

def fetch_market_data(symbol, interval='1d', limit=200):
    """Fetch market data for technical analysis"""
    try:
        candles = client.get_klines(symbol=symbol, interval=interval, limit=limit)
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', '_', '_', '_', '_', '_', '_'])
        df["close"] = df["close"].astype(float)
        df["50_SMA"] = df["close"].rolling(window=50).mean()
        df["200_SMA"] = df["close"].rolling(window=200).mean()
        df["RSI"] = ta.momentum.RSIIndicator(df["close"]).rsi()
        return df
    except Exception as e:
        print(f"❌ Error fetching market data for {symbol}: {e}")
        return None

def generate_signals(df):
    """Generate trading signals based on SMA & RSI"""
    latest = df.iloc[-1]
    sma50, sma200, rsi = latest["50_SMA"], latest["200_SMA"], latest["RSI"]

    if sma50 > sma200 and 50 < rsi < 75:
        return "BUY"
    elif sma50 < sma200 and 25 < rsi < 50:
        return "SELL"
    return "HOLD"

def execute_trade(symbol):
    """Execute trade based on AI insights + technical signals"""
    print(f"\n🚀 Fetching AI market insights for {symbol}...")
    ai_insight = get_market_insights(f"Current trend for {symbol}")
    print(f"💡 AI Insights: {ai_insight}")

    df = fetch_market_data(symbol)
    if df is None:
        return

    signal = generate_signals(df)
    print(f"📊 Technical Signal: {signal}")

    try:
        if signal == "BUY" and "bullish" in ai_insight:
            print(f"✅ Buying {symbol} based on AI + technical confirmation!")
            order = client.order_market_buy(symbol=symbol, quantity=0.001)  # Adjusted qty
            print("Trade Executed:", order)
        elif signal == "SELL" and "bearish" in ai_insight:
            print(f"✅ Selling {symbol} based on AI + technical confirmation!")
            order = client.order_market_sell(symbol=symbol, quantity=0.001)  # Adjusted qty
            print("Trade Executed:", order)
        else:
            print(f"🔵 No strong trading signal for {symbol}. Waiting for better conditions.")
    except Exception as e:
        print(f"❌ Trade execution failed for {symbol}: {e}")

# Execute trading bot for multiple pairs
if __name__ == "__main__":
    for pair in trading_pairs:
        print(f"\n🚀 Running trading bot for {pair}...")
        execute_trade(pair)