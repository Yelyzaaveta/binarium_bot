import requests
from datetime import datetime
from config import BINANCE_API_URL, BINANCE_API_URL2


# def get_binance_prices():  # всі пари
#     try:
#         response = requests.get(BINANCE_API_URL)
#         response.raise_for_status()
#         data = response.json()
#
#         formatted_data = [
#             {
#                 "symbol": item["symbol"],
#                 "lastPrice": float(item["lastPrice"]),
#                 "priceChangePercent": float(item["priceChangePercent"]),
#                 "volume": float(item["volume"]),
#                 "quoteVolume": float(item["quoteVolume"]),
#                 "highPrice": float(item["highPrice"]),
#                 "lowPrice": float(item["lowPrice"]),
#             }
#             for item in data
#         ]
#
#         return formatted_data
#
#     except requests.exceptions.RequestException as e:
#         print(f"Error with Binance API: {e}")
#         return []

def get_binance_prices():  # всі пари ДЛЯ ОБРОБКИ
    try:
        response = requests.get(BINANCE_API_URL)
        print(response)
        response.raise_for_status()
        data = response.json()
        print(data)
        # Список бажаних символів
        desired_symbols = ["USDCHF", "GBPJPY", "USDCAD", "EURNXD", "EURUSD", "EURGBP", "USDJPY", "NZDJPY", "AUDNZD"]

        # Фільтруємо дані за бажаними парами
        filtered_data = [
            {
                "symbol": item["symbol"],
                "lastPrice": float(item["lastPrice"]),
                "priceChangePercent": float(item["priceChangePercent"]),
                "volume": float(item["volume"]),
                "quoteVolume": float(item["quoteVolume"]),
                "highPrice": float(item["highPrice"]),
                "lowPrice": float(item["lowPrice"]),
            }
            for item in data if item["symbol"] in desired_symbols
        ]
        print(filtered_data)
        return filtered_data

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

def get_binance_symbols():
    try:
        response = requests.get("https://api.binance.com/api/v3/exchangeInfo")
        response.raise_for_status()
        data = response.json()

        symbols = [item['symbol'] for item in data['symbols'] if item['status'] == 'TRADING']
        print(symbols)  # Перевірка доступних пар
        return symbols

    except requests.exceptions.RequestException as e:
        print(f"Error with Binance API: {e}")
        return []

pairs = ["EURUSDT", "USDJPY", "GBPUSDT", "USDCHF", "USDCAD", "AUDUSDT"]
base_url = "https://api.binance.com/api/v3/ticker/price?symbol="

def get_prices():
    try:
        for pair in pairs:
            response = requests.get(base_url + pair)
            data = response.json()
            if "price" in data:
                print(f"{data['symbol']}: {data['price']}")
            else:
                print(f"Не вдалося отримати дані для {pair}")
    except Exception as e:
        print(f"Помилка: {e}")

#get_prices()

def get_binance_prices():
    try:
        response = requests.get(BINANCE_API_URL)
        response.raise_for_status()
        data = response.json()

        # Визначаємо потрібні символи у форматі Binance
        desired_symbols = {
            "EURUSD": "EURUSDT",
            "USDJPY": "USDTJPY",
            "GBPUSD": "GBPUSDT",
            "USDCHF": "USDCHF",
            "USDCAD": "USDCAD",
            "AUDUSD": "AUDUSDT",
            "GBPJPY": "GBPJPY",
            "NZDJPY": "NZDJPY",
            "AUDNZD": "AUDNZD",
            "EURNXD": "EURNZD",
            "EURGBP": "EURGBP",
        }

        # Фільтруємо дані за бажаними парами
        filtered_data = [
            {
                "symbol": item["symbol"],
                "lastPrice": float(item["lastPrice"]),
                "priceChangePercent": float(item["priceChangePercent"]),
                "volume": float(item["volume"]),
                "quoteVolume": float(item["quoteVolume"]),
                "highPrice": float(item["highPrice"]),
                "lowPrice": float(item["lowPrice"]),
            }
            for item in data if item["symbol"] in desired_symbols.values()
        ]

        print(filtered_data)
        return filtered_data

    except requests.exceptions.RequestException as e:
        print(f"Error with Binance API: {e}")
        return []

get_binance_prices()