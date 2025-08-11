import json
import time


from config import TWELVE_API_KEY
from gpt import chatgpt_request
import requests
BASE_URL = "https://api.twelvedata.com"

def get_indicators(pair):
    # ТЕСТОВИЙ РЕЖИМ для TEST/PAIR
    if pair == "TEST/PAIR":
        return {
            "rsi": 25.0,
            "sma": 1.0,
            "macd": 2.0,
            "macd_signal": 1.0,
            "macd_hist": 1.0,
            "min": 0.8,
            "max": 2.0,
            "roc": 10.0,
            "supertrend": 2.0
        }
    def fetch_indicator(endpoint, extra_params={}):
        url = f"{BASE_URL}/{endpoint}"
        params = {
            "symbol": pair,
            "interval": "1h",
            "apikey": TWELVE_API_KEY,
            "format": "JSON"
        }
        params.update(extra_params)
        res = requests.get(url, params=params).json()

        if "values" in res and res["values"]:
            return res["values"][0]
        return {}

    # 1. RSI
    rsi_data = fetch_indicator("rsi")
    rsi = float(rsi_data.get("rsi", 0))

    # 2. SMA (50)
    sma_data = fetch_indicator("sma", {"time_period": 50})
    sma = float(sma_data.get("sma", 0))

    # 3. MACD
    macd_data = fetch_indicator("macd")
    macd = float(macd_data.get("macd", 0))
    macd_signal = float(macd_data.get("macd_signal", 0))
    macd_hist = float(macd_data.get("macd_hist", 0))

    # 4. MIN
    min_data = fetch_indicator("min", {"time_period": 10})
    min_val = float(min_data.get("min", 0))

    # 5. MAX
    max_data = fetch_indicator("max", {"time_period": 10})
    max_val = float(max_data.get("max", 0))

    # 6. ROC (Rate of Change)
    roc_data = fetch_indicator("roc", {"time_period": 10})
    roc = float(roc_data.get("roc", 0))

    # 7. Supertrend
    supertrend_data = fetch_indicator("supertrend", {
        "period": 10,
        "multiplier": 3
    })

    supertrend = float(supertrend_data.get("supertrend", 0))

    return {
        "rsi": rsi,
        "sma": sma,
        "macd": macd,
        "macd_signal": macd_signal,
        "macd_hist": macd_hist,
        "min": min_val,
        "max": max_val,
        "roc": roc,
        "supertrend": supertrend
    }


def analyze_pair(pair, current_price):

    # отримуємо 7 індикаторів
    indicators = get_indicators(pair)
    print(indicators)

    # Розрахунок змін ціни
    price_change = (current_price - indicators["sma"]) / indicators["sma"] * 100
    potential_move = indicators["max"] - current_price if current_price < indicators["max"] else current_price - \
                                                                                                 indicators["min"]
    # Сила тренду
    trend_strength = (indicators["supertrend"] - current_price) / current_price * 100

    # Оцінка тренду
    if indicators["rsi"] < 30:
        rsi_trend = "buy"
    elif indicators["rsi"] > 70:
        rsi_trend = "sell"
    else:
        rsi_trend = "neutral"

    prompt = f"""
Ось останні індикатори для {pair}:
- RSI: {indicators["rsi"]} (вище 70 – перекупленість, нижче 30 – перепроданість)
- SMA (50): {indicators["sma"]}, ціна знаходиться {rsi_trend}
- MACD: {indicators["macd"]}, MACD Signal: {indicators["macd_signal"]}
- MACD Histogram: {indicators["macd_hist"]}
- Ціна: {current_price}, попередня ціна: {indicators["sma"]}
- Max за 10 свічок: {indicators["max"]}, Min: {indicators["min"]}
- Зміна ціни: {price_change}%
- Потенціал руху: {potential_move}


Враховуючи ці дані, перевірь розрахунок у відсотках і скажи якшо ціна має потенціал руху в найюлижці 10-15 хв то в який бік (Expected move):
1. Зміни ціни
2. Потенціал руху
3. Силу тренду

Надай відповідь у форматі:
Action: WAIT or ENTER (ENTER - це коли можна купляти аьо продавати)
RSI:  
SMA:  
Price Change:  
Potential Move:  
Trend Strength:
Expected Move: Up\down or stay  
Explain: in 10 words укр мовою                                                                                                                                                                  
"""
    print("\n[DEBUG] PROMPT до GPT:")
    print(prompt)
    max_attempts = 5
    gpt_response = {}
    for attempt in range(max_attempts):
        print(f"\u0421\u043f\u0440\u043e\u0431\u0430 {attempt + 1} \u043e\u0442\u0440\u0438\u043c\u0430\u0442\u0438 \u0432\u0456\u0434\u043f\u043e\u0432\u0456\u0434\u044c \u0432\u0456\u0434 GPT...")
        raw_response = chatgpt_request(prompt)
        print("[DEBUG] RAW_RESPONSE від GPT:")
        print(repr(raw_response))
        if raw_response and not raw_response.startswith("Помилка"):
            try:
                cleaned = raw_response.strip().strip('`')
                print("[DEBUG] CLEANED RESPONSE:")
                print(repr(cleaned))
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:].strip()
                gpt_response = json.loads(cleaned)
                print("✅ Успішна відповідь GPT:")
                print(gpt_response)
                # Видалено жорстку підміну для тесту точки входу
                break
            except json.JSONDecodeError:
                print("\u274c \u041d\u0435 \u0432\u0434\u0430\u043b\u043e\u0441\u044f \u0440\u043e\u0437\u043f\u0430\u0440\u0441\u0438\u0442\u0438 JSON. \u0421\u0438\u0440\u0430 \u0432\u0456\u0434\u043f\u043e\u0432\u0456\u0434\u044c:", repr(raw_response))
        else:
            print("\u26a0\ufe0f \u0412\u0456\u0434\u043f\u043e\u0432\u0456\u0434\u044c \u043f\u043e\u0440\u043e\u0436\u043d\u044f \u0430\u0431\u043e \u043f\u043e\u043c\u0438\u043b\u043a\u0430:", repr(raw_response))

        time.sleep(5)

    # Форматуємо дані для аналізу
    analysis = {
        "Action": gpt_response["Action"],
        "RSI": gpt_response["RSI"],
        "SMA": gpt_response["SMA"],
        "Price Change": gpt_response["Price Change"],
        "Potential Move": gpt_response["Potential Move"],
        "Trend Strength": gpt_response["Trend Strength"],
        "Expected Move": gpt_response["Expected Move"],
        "Explain": gpt_response["Explain"]
    }

    # Форматуємо повідомлення для відправки
    message = f"""
*Валютна пара {pair}:*

Сигнал: `{analysis["Action"]}`
Ціна: `{current_price}`
  
Зміни: `{analysis["Price Change"]}`  
Потенціал: `{analysis["Potential Move"]}`  
Сила тренду: `{analysis["Trend Strength"]}`

Аналіз АI: `{analysis["Explain"]}`

⚛   Аналіз проведено за допомогою GPT-4, BINARIUM AI та за 10 індикаторами які показують напрям руху {analysis["Expected Move"]}

Шукаємо точку входу ...
"""

    print(message)
    return analysis, message
