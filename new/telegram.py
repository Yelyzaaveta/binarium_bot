from datetime import timedelta

import requests
from config import TELEGRAM_API_URL, CHAT_ID

def send_telegram_message(message, image_url=None):
    try:
        if image_url:
            with open(image_url, 'rb') as image_file:
                image_payload = {
                    "chat_id": CHAT_ID,
                    "caption": message,
                    "parse_mode": "Markdown"
                }
                files = {"photo": image_file}

                image_response = requests.post(f"{TELEGRAM_API_URL}/sendPhoto", data=image_payload, files=files)
                image_response.raise_for_status()
                print("Зображення надіслано успішно!")
                return

        payload = {
           "chat_id": CHAT_ID,
          "text": message,
          "parse_mode": "Markdown"
        }
        response = requests.get(f"{TELEGRAM_API_URL}/sendMessage", params=payload)
        response.raise_for_status()
        print("Message sent to Telegram successfully!")
        print(message)
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")


def send_closing_message(is_profit: bool, percentage: float, asset: str, open_price: float, close_price: float, non=None):
    result = "ПЛЮС ✅" if is_profit else "МІНУС 🚨"
    result2 = "📈 ПРОФІТ" if is_profit else "📉 ЗБИТОК"
    image_url = "images/PLUSE.png" if is_profit else "images/MINUS.png"

    if non:
        result = "ПОВЕРНЕННЯ"
        result2 = "НА МАСЦІ"
        image_url = "images/onhold.png"

    message = f"""
*ТЕСТОВА ІНФА !*
*Актив:* `{asset}`

*Результат прогнозу:* {result}

*◾️Ціна відкриття:* `{open_price}`
*◾️Ціна закриття:* `{close_price}`

{result2}: `{percentage:.2f}%`
"""
    send_telegram_message(message, image_url)


def send_enter_point_message(asset: str, direction: str, entry_time: str, entry_price: float):
    if direction.lower() == "вгору":
        image_url = "images/UP.png"
        arrow = "⬆️"
    elif direction.lower() == "вниз":
        image_url = "images/DOWN.png"
        arrow = "⬇️"
    else:
        raise ValueError("err")
    entry_time_plus_5 = entry_time + timedelta(minutes=5)
    entry_time_plus_5_str = entry_time_plus_5.strftime("%Y-%m-%d %H:%M:%S")

    message = f"""
*ТЕСТОВА ІНФА !*
*Актив:* `{asset}`

*Точка входу знайдена!* {arrow}
*Cигнал:* `{direction}`

*Час:* `{entry_time}`
*До* `{entry_time_plus_5_str}`
*Ціна активу:* `{entry_price}`
"""
    send_telegram_message(message, image_url)
