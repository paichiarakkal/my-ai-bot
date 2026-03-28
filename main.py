import telebot
import os
from flask import Flask, request
from groq import Groq
import pandas as pd
import yfinance as yf
import threading
import time
import requests

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

if not TELEGRAM_BOT_TOKEN or not GROQ_API_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# Supertrend signal for crude/nifty
def get_supertrend_signal(symbol):
    try:
        df = yf.download(symbol, interval="5m", period="2d", progress=False)
        if df.empty:
            return "No data available"
        high = df['High']
        low = df['Low']
        close = df['Close']
        # Basic Supertrend logic (simplified)
        atr = (high - low).rolling(14).mean()
        upper_band = (high + low) / 2 + 2 * atr
        lower_band = (high + low) / 2 - 2 * atr
        last_close = close.iloc[-1]
        last_upper = upper_band.iloc[-1]
        last_lower = lower_band.iloc[-1]
        if last_close > last_upper:
            signal = "BUY"
        elif last_close < last_lower:
            signal = "SELL"
        else:
            signal = "NEUTRAL"
        return f"{signal} @ {last_close:.2f}"
    except Exception as e:
        return f"Error: {e}"

# Webhook endpoint (must match the token)
@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return "Bot is Active!"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower().strip()
    if "crude" in text:
        reply = get_supertrend_signal("CL=F")
        bot.reply_to(message, reply)
    elif "nifty" in text:
        reply = get_supertrend_signal("NSEI")
        bot.reply_to(message, reply)
    else:
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "നീ ഒരു സഹായി. എല്ലാ ഉത്തരവും മലയാളത്തിൽ തരിക."},
                    {"role": "user", "content": message.text}
                ],
                temperature=0.7,
                max_tokens=500
            )
            reply = completion.choices[0].message.content
            bot.reply_to(message, reply)
        except Exception as e:
            bot.reply_to(message, f"Error: {e}")

# Keep-alive thread (optional, to avoid spin down)
def keep_alive():
    while True:
        try:
            requests.get("https://my-ai-bot-aid1.onrender.com/")
        except:
            pass
        time.sleep(600)

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    # This block is only for local testing; on Render, gunicorn will run the app.
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
