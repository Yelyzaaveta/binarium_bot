import requests
from datetime import datetime
from config import BINANCE_API_URL, BINANCE_API_URL2


def get_binance_prices():  # всі пари
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()
        data = response.json()

        formatted_data = [
            {
                "symbol": item["symbol"],
                "lastPrice": float(item["lastPrice"]),
                "priceChangePercent": float(item["priceChangePercent"]),
                "volume": float(item["volume"]),
                "quoteVolume": float(item["quoteVolume"]),
                "highPrice": float(item["highPrice"]),
                "lowPrice": float(item["lowPrice"]),
            }
            for item in data
        ]

        return formatted_data

    except requests.exceptions.RequestException as e:
        print(f"Error with Binance API: {e}")
        return []

def get_kline_data(symbol, interval="5m", limit=3):  # 3 свічки (по 5 хвилин кожна)
    try:
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        response = requests.get(BINANCE_API_URL2, params=params)
        response.raise_for_status()
        data = response.json()

        formatted_data = [
            {
                "symbol": symbol,
                "openTime": datetime.fromtimestamp(item[0] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                "closeTime": datetime.fromtimestamp(item[6] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                "openPrice": float(item[1]),
                "closePrice": float(item[4]),
                "highPrice": float(item[2]),
                "lowPrice": float(item[3]),
                "volume": float(item[5]),
            }
            for item in data
        ]

        return formatted_data

    except requests.exceptions.RequestException as e:
        print(f"Error with Binance API: {e}")
        return []