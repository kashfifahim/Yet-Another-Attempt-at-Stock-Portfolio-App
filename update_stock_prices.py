from collections import deque
from dotenv import load_dotenv
import json
import os 
import requests
import time


# Alpha Vantage API details
load_dotenv()
API_URL = "https://www.alphavantage.co/query"
API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")

# Caching
CACHE_DIR = "cache"

# Define your stock symbols and quantities in a circular queue
stock_queue = deque([
    {"symbol": "TSLA", "quantity": 16},
    {"symbol": "GOOGL", "quantity": 20},
    {"symbol": "AMZN", "quantity": 20},
    {"symbol": "AAPL", "quantity": 14},
    {"symbol": "CSCO", "quantity": 1},
    {"symbol": "NOK", "quantity": 2}
])

def cache_filename(symbol):
    try:
        return os.path.join(CACHE_DIR, f"{symbol}.json")
    except Exception as e:
        print(f"Error generating cache filename for symbol {symbol}: {e}")
        return None

# Function to get stock prices for a given symbol and update cache
def get_stock_prices(symbol):
    filename = cache_filename(symbol)

    try:
        # Make an API call
        response = requests.get(API_URL, {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": API_KEY
        })
        response.raise_for_status()  # Raises an error for bad status codes
        data = response.json()

        if "Global Quote" in data and "05. price" in data["Global Quote"]:
            price = float(data["Global Quote"]["05. price"])
            # Update cache with the new price
            write_cache(filename, price)
            return price, time.time()
        else:
            # Data not in the expected format
            print(f"Unexpected data format for {symbol}: {data}")
            cache_data = read_cache(filename) if os.path.exists(filename) else {"price": None}
            return cache_data["price"], cache_data.get("timestamp")

    except requests.exceptions.RequestException as e:
        # API call failed, fallback to cache
        print(f"Request error for symbol {symbol}: {e}")
        cache_data = read_cache(filename) if os.path.exists(filename) else {"price": None}
        return cache_data["price"], cache_data.get("timestamp")
    except Exception as e:
        print(f"An unexpected error occurred for symbol {symbol}: {e}")
        return None, None

def read_cache(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def write_cache(filename, data):
    cache_data = {
        "price": data,
        "timestamp": time.time()
    }
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(filename, 'w') as file:
        json.dump(cache_data, file)

# Function to update stock prices for all symbols in the queue
def update_stock_prices():
    for _ in range(len(stock_queue)):
        stock_info = stock_queue.popleft()
        symbol = stock_info["symbol"]
        quantity = stock_info["quantity"]
        price, _ = get_stock_prices(symbol)
        print(f"Updated {symbol} price: {price}")
        stock_queue.append(stock_info)  # Append the stock back to the queue

if __name__ == '__main__':
    # Run the update_stock_prices function
    update_stock_prices()


