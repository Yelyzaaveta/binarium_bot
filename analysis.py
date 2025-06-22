from api import get_kline_data


def filter_important_changes(prices_data):
    # Фільтруємо зміни, де відсоткова зміна більше 2%
    important_changes = []
    for item in prices_data:
        price_change_percent = item['priceChangePercent']
        print(price_change_percent)
        if abs(price_change_percent) > 0.1:
            print("sssssssss")
            important_changes.append(item)
    return important_changes

def filter_important_pairs(prices_data):
    # Фільтруємо пари, де відсоткова зміна більше 2%
    important_changes = []
    for item in prices_data:
        price_change_percent = item['priceChangePercent']
        if abs(price_change_percent) > 1.5:
            print("sss")
            important_changes.append(item)
    return important_changes

def check_price_change(symbol):
    kline_data = get_kline_data(symbol, interval="5m", limit=3)
    print(kline_data)
    if kline_data:
        open_price = kline_data[0]["openPrice"]
        close_price = kline_data[-1]["closePrice"]

        price_change = (close_price - open_price) / open_price * 100
        print("fffff")
        print(price_change)
        if abs(price_change) > 0.09:
           return price_change
        else:
            return 0
    return None
