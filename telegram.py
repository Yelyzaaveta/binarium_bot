import requests
from config import TELEGRAM_API_URL, CHAT_ID

def send_telegram_message(message):
    try:
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        response = requests.get(f"{TELEGRAM_API_URL}/sendMessage", params=payload)
        response.raise_for_status()
        print("Message sent to Telegram successfully!")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to Telegram: {e}")