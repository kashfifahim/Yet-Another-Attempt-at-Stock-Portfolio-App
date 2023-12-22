from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template
import json
import os
import pytz

app = Flask(__name__)

load_dotenv()

API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

# Define your stock symbols and quantities
stocks = {
    "TSLA": 16,
    "GOOGL": 20,
    "AMZN": 20,
    "AAPL": 14,
    "CSCO": 1,
    "NOK": 2
}

# Function to read stock prices from cache
def read_stock_prices():
    prices = {}
    formatted_timestamps = {}
    for stock, quantity in stocks.items():
        filename = cache_filename(stock)
        cache_data = read_cache(filename) if os.path.exists(filename) else {"price": None, "timestamp": None}
        price = cache_data["price"]
        timestamp = cache_data["timestamp"]

        prices[stock] = price if price is not None else "N/A"

        # Convert and format the timestamp from UTC to EST
        if timestamp:
            utc_time = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
            est_time = utc_time.astimezone(pytz.timezone('US/Eastern'))
            formatted_timestamps[stock] = est_time.strftime('%Y-%m-%d %I:%M %p EST')
        else:
            formatted_timestamps[stock] = "N/A"

    return prices, formatted_timestamps

@app.route('/')
def index():
    prices, formatted_timestamps = read_stock_prices()

    total_value = 0
    for stock, price in prices.items():
        if price != "N/A":
            total_value += price * stocks[stock]

    return render_template('index.html', prices=prices, total=total_value, stocks=stocks, timestamps=formatted_timestamps)

def cache_filename(symbol):
    try:
        return os.path.join("cache", f"{symbol}.json")
    except Exception as e:
        print(f"Error generating cache filename for symbol {symbol}: {e}")
        return None

def read_cache(filename):
    with open(filename, 'r') as file:
        return json.load(file)