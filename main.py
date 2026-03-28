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

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
app = Flask(__name__)

def get_supertrend_signal(symbol):
    try:
        df = yf.download(symbol, interval="5m", period="1d", progress=False)
        if df.empty: return "ഡാറ്റ ലഭ്യമല്ല."
        high, low, close = df['High'], df['Low'], df['Close']
        atr = (high - low).rolling(10).mean()
        upper_band = (high + low) / 2 + 3 * atr
        last_close = float(close.iloc[-1])
        signal = "BUY 🟢" if last_close > float(upper_band.iloc[-1]) else "SELL 🔴"
        return f"📊 *({symbol})*\n💰 വില: {last_close:.2f}\n⚡️ സിഗ്നൽ: {signal}"
    except: return "Error fetching data"

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

@app.route('/')
def index(): return "Bot is Active!"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower().strip()
    if "crude" in text:
        bot.reply_to(message, get_supertrend_signal("CL=F"), parse_mode='Markdown')
    elif "nifty" in text:
        bot.reply_to(message, get_supertrend_signal("^NSEI"), parse_mode='Markdown')
    else:
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": message.text}]
            )
            bot.reply_to(message, completion.choices[0].message.content)
        except: bot.reply_to(message, "AI Error")

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    # നിങ്ങളുടെ ശരിയായ URL ഇവിടെ ഉണ്ടെന്ന് ഉറപ്പാക്കുക
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
