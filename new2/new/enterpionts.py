from datetime import datetime

import requests
from config import TWELVE_API_KEY


def get_current_price(pair: str) -> float:
    if pair == "TEST/PAIR":
        return 1.1
    url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=1min&outputsize=1&apikey={TWELVE_API_KEY}"
    response = requests.get(url)
    data = response.json()
    print(data)
    if "values" in data and isinstance(data["values"], list) and len(data["values"]) > 0:
        current_price = float(data["values"][0]["close"])
        return current_price
    else:
        print("Помилка при отриманні ціни:", data.get("message", "невідома помилка"))
        return None


def check_entry_point(pair, analysis_result):
    print(f"Перевірка точки входу для пари {pair}")
    print("Аналіз:", analysis_result)

    move = analysis_result.get("Action", "").strip().upper()
    expected_move = analysis_result.get("Expected Move", "").strip().upper()
    print(f"[DEBUG] check_entry_point: Action={move}, Expected Move={expected_move}")
    if move == "ENTER":
        if expected_move == "UP":
            return {
                "direction": "вгору",
                "price": get_current_price(pair),
                "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

        elif expected_move == "DOWN":
            return {
                "direction": "вниз",
                "price": get_current_price(pair),
                "entry_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        print("[DEBUG] check_entry_point: Action=ENTER, але Expected Move не UP і не DOWN")
        return None
    print("[DEBUG] check_entry_point: Action не ENTER, точка входу не знайдена")
    return None

