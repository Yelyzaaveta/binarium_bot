import datetime
import time

from aiogram.utils.json import json

from analysis import filter_important_changes, check_price_change
from api import get_binance_prices
from gpt import analyze_market
from telegram import send_telegram_message, send_enter_point_message, send_closing_message


# ЦЕ СТАРИЙ НА БІНАНСІ НОВИЙ У ПАПЦІ НЕВ

def format_price(price):
    # Форматуємо число з 2 знаками після коми
    return "{:.10f}".format(price)

def format_message(message2):
    print(message2)
    message2 = json.loads(message2)
    message = (
        f"Дія: {message2['action']}\n"
        f"RSI: {message2['RSI']}\n"
        f"SMA: {message2['SMA']}\n"
        f"Зміна ціни: {message2['Price change']}\n"
        f"Потенціал руху: {message2['Potential move']}\n"
        f"Сила тренду: {message2['Trend strength']}\n\n"
        f"Аналіз АІ: {message2['Explain']}\n"
        f"Aналіз проведено за допомогою GPT-4 та BINARIUM"
    )
    return message

def move(message2):
    print(message2)
    message2 = json.loads(message2)
    message = message2['Potential move']
    if message == "high" :
        return True
    else:
        return None


def main():
    while True:
        prices_data = get_binance_prices()
        print(prices_data)
        important_changes = filter_important_changes(prices_data)

        if important_changes:
            isimportant = False
            for change in important_changes:
                symbol = change["symbol"]
                last_price = format_price(float(change["lastPrice"]))
                price_change_percent = float(change["priceChangePercent"])

                price_change = check_price_change(symbol)

                if price_change_percent > 0:
                    directionday = "*Вверх /*"
                elif price_change_percent < 0:
                    directionday = "*Вниз \*"
                else:
                    directionday = "*Без змін*"

                if price_change == 0:
                    direction = "зміна менше 2%"
                else:
                    if price_change > 0.5:
                        direction = "*Вверх"
                        isimportant = True
                    elif price_change < 0.5:
                        direction = "*Вниз"
                        isimportant = True

                message = f"""
*ПАРА: `{symbol} `*
*Ціна:* `{last_price}`

*Зміна за 24 години:* `{price_change_percent}%`
*Напрям за 24 години:* {directionday}

*ЗМІНА ЗА останні 5 ХВ*
*Зміна за останні 5 хв:* `{format_price(price_change)}%`
*Напрям* {direction}

Проводиться аналіз....
                """

                if isimportant:
                    #(message)
                    message2 = analyze_market(symbol)
                    mov = move(message2)
                    message2 = format_message(message2)
                    massagino = message + message2
                    send_telegram_message(massagino, "images/analysis.png")
                    print(massagino)
                    isimportant = False

                    if mov :

                        direction = "вгору" if price_change > 0.01 else "вниз"
                        entry_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                        send_enter_point_message(symbol, direction, entry_time, last_price)
                        entry_price =  float(last_price)
                        time.sleep(300)
                        updated_prices_data = get_binance_prices()
                        updated_price = None

                        for updated_change in updated_prices_data:
                            if updated_change["symbol"] == symbol:
                                updated_price = float(updated_change["lastPrice"])
                                break

                        if updated_price:
                            price_difference = updated_price - entry_price
                            percentage_change = (price_difference / entry_price) * 100

                            if direction == "вгору":
                                is_profit = percentage_change > 0
                            else:
                                is_profit = percentage_change < 0

                            send_closing_message(
                                is_profit=is_profit,
                                percentage=percentage_change,
                                asset=symbol,
                                open_price=entry_price,
                                close_price=updated_price
                            )


        time.sleep(360)

if __name__ == '__main__':
    main()


