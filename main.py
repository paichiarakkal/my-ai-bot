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
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# Price Fetch Function
def get_price(symbol):
    try:
        df = yf.download(symbol, interval="5m", period="1d")
        if df.empty: return "ഡാറ്റ ലഭ്യമല്ല."
        last_price = round(df['Close'].iloc[-1], 2)
        return f"{symbol} നിലവിലെ വില: {last_price}"
    except:
        return "വില പരിശോധിക്കുന്നതിൽ തടസ്സം നേരിട്ടു."

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
def handle_messages(message):
    text = message.text.lower()
    if "price" in text or "crude" in text:
        # Crude Oil Price
        info = get_price("CL=F")
        bot.reply_to(message, info)
    else:
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": message.text}]
            )
            bot.reply_to(message, completion.choices[0].message.content)
        except Exception as e:
            bot.reply_to(message, "ക്ഷമിക്കണം, ഒരു എറർ സംഭവിച്ചു.")

def keep_alive():
    while True:
        try:
            requests.get("https://my-ai-bot-a1d1.onrender.com/")
        except:
            pass
        time.sleep(600)

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    bot.remove_webhook()
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
