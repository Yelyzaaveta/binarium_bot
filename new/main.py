import time

from new.twelveapi import get_candles, find_most_volatile_pair, monitor_pair


def main_loop():
    pairs = ["USD/CHF", "EUR/USD", "USD/JPY", "EUR/NZD", "USD/CHF", "USD/CAD", "EUR/GBP", "AUD/NZD"]
    index = 0

    while True:
        print("Завантажуємо свічки...")

        # отримання цінової та історичної інфи про пари
        current_pair = pairs[index]
        candles = get_candles([current_pair])
        print(candles)

        # пошук пари з найблішою зміною
        result = find_most_volatile_pair(candles, threshold=0.2)
        print("rrrrrrrrr")
        print(result)
        if result:
            print(f"Знайдено пару: {result['pair']} — {result['change_percent']}%")

            # аналіз та моніториг пари
            monitor_pair(
                result["pair"],
                result["change_percent"],
                result["current_price"]
            )
        else:
            print("Не знайдено сильних рухів. Наступна пара через 1 хвилину.")
            time.sleep(60)

        index = (index + 1) % len(pairs)


if __name__ == "__main__":
    main_loop()
