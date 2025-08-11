import datetime

import requests
import time

from config import TWELVE_API_KEY
from analyse import analyze_pair
from enterpionts import check_entry_point, get_current_price
from telegram import send_enter_point_message, send_closing_message, send_telegram_message


TEST_MODE = False  # Вимкнено тестовий режим

def get_candles(pairs):
    if TEST_MODE:
        # Повертаємо штучно волатильні дані для тесту
        return {
            "TEST/PAIR": [
                {"datetime": "2025-07-25 04:15:00", "open": "1.00", "high": "1.10", "low": "0.90", "close": "1.10"},
                {"datetime": "2025-07-25 04:00:00", "open": "1.10", "high": "1.15", "low": "1.00", "close": "1.15"},
                {"datetime": "2025-07-25 03:45:00", "open": "1.15", "high": "1.20", "low": "1.10", "close": "1.20"},
                {"datetime": "2025-07-25 03:30:00", "open": "1.20", "high": "1.25", "low": "1.15", "close": "1.25"},
                {"datetime": "2025-07-25 03:15:00", "open": "1.25", "high": "1.30", "low": "1.20", "close": "1.30"},
                {"datetime": "2025-07-25 03:00:00", "open": "1.30", "high": "1.35", "low": "1.25", "close": "1.35"},
                {"datetime": "2025-07-25 02:45:00", "open": "1.35", "high": "1.40", "low": "1.30", "close": "1.40"},
                {"datetime": "2025-07-25 02:30:00", "open": "1.40", "high": "1.45", "low": "1.35", "close": "1.45"}
            ]
        }
    all_candles = {}
    for pair in pairs:
        url = f"https://api.twelvedata.com/time_series?symbol={pair}&interval=15min&outputsize=8&apikey={TWELVE_API_KEY}"

        try:
            response = requests.get(url)
            print(f"Відповідь від сервера для {pair}: {response.status_code}")

            if response.status_code == 200:
                try:
                    data = response.json()

                    if "values" in data:
                        all_candles[pair] = data["values"]
                    else:
                        print(f"[❌] Дані для {pair} не містять 'values': {data}")
                        all_candles[pair] = []

                except ValueError:
                    print(f"[❌] JSONDecodeError: Неможливо розпарсити відповідь для {pair}")
                    all_candles[pair] = []

            else:
                print(f"[❌] Статус {response.status_code} для {pair}. Пропускаємо.")
                all_candles[pair] = []

        except requests.exceptions.RequestException as e:
            print(f"[❌] Помилка при запиті до API для {pair}: {e}")
            all_candles[pair] = []

        time.sleep(1)  # затримка, щоб не перевищити ліміт API

    return all_candles

def calculate_percentage_change(open_price, close_price):
    return ((close_price - open_price) / open_price) * 100

def find_most_volatile_pair(candles_data, threshold=2.0):
    max_change = 0
    most_volatile_info = None

    for pair, candles in candles_data.items():
        if len(candles) < 2:
            continue

        first_candle = candles[-1]
        last_candle = candles[0]

        open_price = float(first_candle["open"])
        close_price = float(last_candle["close"])
        print("00000")
        change = calculate_percentage_change(open_price, close_price)
        print(change)
        if abs(change) > abs(max_change) and abs(change) >= threshold:
            print("00000-00000-000000")
            max_change = change
            most_volatile_info = {
                "pair": pair,
                "change_percent": round(change, 2),
                "start_time": first_candle["datetime"],
                "end_time": last_candle["datetime"],
                "current_price": close_price
            }

    return most_volatile_info


def monitor_pair(pair, change_percent, current_price):
    print (pair, change_percent, current_price)

    # технічний аналіз + прогноз
    analysis_result, analysis_message = analyze_pair(pair, current_price)
    print ("xxxxxxxxxxxxxxxxxxxxxxxx")
    print(analysis_result)
    send_telegram_message(analysis_message, "images/analysis.png")

    # моніторинг точки входу (12 спроб)
    max_attempts = 4
    entry_found = False

    for attempt in range(max_attempts):
        print(f"Спроба {attempt + 1} пошуку точки входу для {pair}...")

        entry_point = check_entry_point(pair, analysis_result)

        if entry_point:
            direction = entry_point["direction"]
            entry_price = entry_point["price"]
            entry_time = entry_point["entry_time"]

            # меседж про точку входу
            send_enter_point_message(pair, direction, entry_time, entry_price)

            # через 5 хв перевіряємо результат
            time.sleep(300)

            # звірка ціни
            new_price = get_current_price(pair)
            if new_price == entry_price:
                is_profit = True # неважно
                non = "на місці"
                change = "0%"
            else:
                is_profit = (new_price > entry_price) if direction.lower() == "вгору" else (new_price < entry_price)
                change = ((new_price - entry_price) / entry_price) * 100
                non = None

            # повідомлення про закриття
            send_closing_message(is_profit, change, pair, entry_price, new_price, non)
            entry_found = True
            break


        else:
            time.sleep(300)
            current_price = get_current_price(pair)
            analysis_result, _ = analyze_pair(pair, current_price)

    if not entry_found:
        send_telegram_message("Пошук закрит, точки входу не знайдено")
        print("")
