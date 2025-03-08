import time

from analysis import filter_important_changes, check_price_change
from api import get_binance_prices
from telegram import send_telegram_message

def format_price(price):
    # Форматуємо число в звичайний вигляд без експоненціальної форми
    return "{:,.20f}".format(price)


def main():
    while True:
        prices_data = get_binance_prices()
        important_changes = filter_important_changes(prices_data)

        if important_changes:
            isimportant = False
            for change in important_changes:
                symbol = change["symbol"]
                last_price =  format_price(float(change["lastPrice"]))
                price_change_percent = float(change["priceChangePercent"])

                price_change = check_price_change(symbol)

                if price_change_percent > 0:
                    directionday = "*Вверх _/*"
                elif price_change_percent < 0:
                    directionday = "*Вниз \_*"
                else:
                    directionday = "*Без змін*"

                if price_change == 0:
                    direction = "зміна менше 2%"
                else:
                    if price_change > 0:
                        direction = "*Вверх _/*"
                        isimportant = True
                    elif price_change < 0:
                        direction = "*Вниз \_*"
                        isimportant = True

                message = f"""
        *ВАЖЛИВА ЗМІНА*
        
        *ПАРА: `{symbol} `*
        *Ціна:* `{last_price}`
        
        *Зміна за 24 години:* `{price_change_percent}%`
        *Напрям за 24 години:* {directionday}
        
        *ЗМІНА ЗА 5 ХВ*
        *Зміна за 5 хв:* `{price_change}%`
        *Напрям* {direction}
                        """

                if isimportant:
                    send_telegram_message(message)
                    isimportant = False

            time.sleep(1200)


if __name__ == '__main__':
    main()
