from api import get_kline_data


def filter_important_changes(prices_data):
    # Фільтруємо зміни, де відсоткова зміна більше 2%
    important_changes = []
    for item in prices_data:
        price_change_percent = item['priceChangePercent']
        if abs(price_change_percent) > 2:
            important_changes.append(item)
    return important_changes


def filter_important_pairs(prices_data):
    # Фільтруємо пари, де відсоткова зміна більше 2%
    important_changes = []
    for item in prices_data:
        price_change_percent = item['priceChangePercent']
        if abs(price_change_percent) > 2:
            important_changes.append(item)
    return important_changes

def check_price_change(symbol):
    kline_data = get_kline_data(symbol, interval="5m", limit=3)
    if kline_data:
        open_price = kline_data[0]["openPrice"]
        close_price = kline_data[-1]["closePrice"]

        # Розраховуємо зміну ціни
        price_change = (close_price - open_price) / open_price * 100
        print(price_change)
        if abs(price_change) > 2:

           return price_change
        else:
            return 0
    return None
