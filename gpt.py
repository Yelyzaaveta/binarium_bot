from urllib import response

import pandas as pd
import pandas_ta as ta
import requests
import openai
from aiogram.utils.json import json

from config import OPENAI_API_KEY

BINANCE_URL = "https://api.binance.com/api/v3/klines"

def get_kline_data(symbol, interval="5m", limit=100):
    """ Отримуємо історичні дані (свічки) з Binance """
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    response = requests.get(BINANCE_URL, params=params)
    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_asset_volume", "num_trades",
        "taker_buy_base_vol", "taker_buy_quote_vol", "ignore"
    ])
    df["close"] = df["close"].astype(float)
    return df


def calculate_indicators(df):
    """ Розраховуємо RSI, SMA та MACD """
    df["RSI"] = ta.rsi(df["close"], length=14)
    df["SMA"] = ta.sma(df["close"], length=50)
    macd_df = ta.macd(df["close"], fast=12, slow=26, signal=9)
    df["MACD"] = macd_df["MACD_12_26_9"]
    df["MACD_signal"] = macd_df["MACDs_12_26_9"]
    df["MACD_hist"] = macd_df["MACDh_12_26_9"]
    df.dropna(inplace=True)
    return df


def analyze_market(symbol):
    """ Основний алгоритм аналізу ринку """
    print("analyzing....")
    df = get_kline_data(symbol)
    df = calculate_indicators(df)

    latest_rsi = float(df["RSI"].iloc[-1])
    latest_sma = float(df["SMA"].iloc[-1])
    latest_macd = float(df["MACD"].iloc[-1])
    latest_macd_signal = float(df["MACD_signal"].iloc[-1])
    latest_macd_hist = float(df["MACD_hist"].iloc[-1])
    prev_macd_hist = float(df["MACD_hist"].iloc[-2])
    sma_trend = "above" if latest_sma < df["close"].iloc[-1] else "below"
    rsi_trend = "increasing" if df["RSI"].iloc[-1] > df["RSI"].iloc[-2] else "decreasing"
    max_price = df["high"].iloc[-10:].max()
    min_price = df["low"].iloc[-10:].min()
    max_price = float(max_price) if isinstance(max_price, str) else max_price
    min_price = float(min_price) if isinstance(min_price, str) else min_price
    macd_variance = df["MACD_hist"].iloc[-10:].var()

    price_change_val = ((df["close"].iloc[-1] - df["close"].iloc[-5]) / df["close"].iloc[-5]) * 100
    potential_move_val = ((max_price - min_price) / df["close"].iloc[-1]) * 100
    trend_strength_val = (abs(latest_macd_hist) / macd_variance * 100) if macd_variance != 0 else 0

    price_change = f"{max(1, round(price_change_val))}% - {max(1, round(price_change_val))}%"
    potential_move = f"{max(1, round(potential_move_val))}% - {max(1, round(potential_move_val))}%"
    trend_strength = f"{max(1, min(100, round(trend_strength_val)))}% - {max(1, min(100, round(trend_strength_val) + 1))}%"

    print(price_change)
    print(potential_move)
    print(trend_strength)
    if None in [latest_rsi, latest_sma, latest_macd, latest_macd_signal]:
        return "Недостатньо даних для аналізу."

    # Логіка пошуку точки входу
    if latest_rsi < 30 and latest_macd > latest_macd_signal:
        signal = "Buy Signal"
    elif latest_rsi > 70 and latest_macd < latest_macd_signal:
        signal = "Sell Signal"
    else:
        signal = "Wait for a better entry point"

    # Формуємо запит до ChatGPT
    prompt = f"""
    Ось останні індикатори для {symbol}:
    - RSI: {latest_rsi:.2f} (вище 70 – перекупленість, нижче 30 – перепроданість)
    - SMA (50): {latest_sma:.2f}, ціна знаходиться {sma_trend if isinstance(sma_trend, str) else f'{sma_trend:.2f}'} SMA
    - MACD: {latest_macd:.2f}, MACD Signal: {latest_macd_signal:.2f}
    - MACD Histogram: {latest_macd_hist:.2f} (попереднє значення {prev_macd_hist:.2f})
    - Ціна: {df["close"].iloc[-1]:.2f}, попередня ціна {df["close"].iloc[-5]:.2f}
    - Максимальна ціна за 10 свічок: {max_price:.2f}
    - Мінімальна ціна за 10 свічок: {min_price:.2f}
    - Дисперсія MACD за 10 свічок: {macd_variance:.6f}
    - Зміни : {price_change}
    - Потенціал руху: {potential_move} 
    - Сила тренду: {trend_strength}

    Враховуючи ці дані, перевірь розрахуник у відсотках:
    1. Зміни ціни
    2. Потенціал руху
    3. Силу тренду

    Будь ласка, надай пояснення для кожного з розрахунків.
    Надішли відповід у форматі:
    action: WHAIT або ENTER
    RSI: одним словом
    SMA: одним словом
    Price change: одним словом    v
    Potential move: - одним словом низький\сердній\вискокий
    Trend strength: - одним словом
    Explain: Очикуєм точку входи\входим 3 слова
    """
    chatgpt_response = chatgpt_request(prompt)

    return chatgpt_response


def chatgpt_request(prompt):
    """ Запит до ChatGPT через API """
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Ти трейдер-аналітик. Чи варто зараз входити купояти цю пару чи чекати? Відповідь в форматі json"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error in API request: {e}"

