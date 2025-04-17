// src/index.js
require('dotenv').config(); // Loads variables from a .env file into process.env

const Binance = require('node-binance-api');
const binance = new Binance().options({
  APIKEY: process.env.BINANCE_API_KEY,      // Read from .env file
  APISECRET: process.env.BINANCE_API_SECRET,  // Read from .env file
  useServerTime: true,
  test: true // Test mode; change to false for live trading
});

async function fetchPrices() {
  try {
    const prices = await binance.prices();
    console.log("Current Market Prices:", prices);
  } catch (error) {
    console.error("Error fetching market prices:", error);
  }
}

console.log("Binance Trading AI Bot Initialized!");
console.log("Starting Binance Trading AI Bot...");
fetchPrices();
