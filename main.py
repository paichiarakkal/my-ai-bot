import telebot
import os
from flask import Flask, request
from twilio.rest import Client
import yfinance as yf
import pandas as pd
import time

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
MY_NUMBER = os.environ.get('MY_WHATSAPP_NUMBER')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
app = Flask(__name__)

def get_trading_signal(symbol):
    try:
        sym = symbol.upper().strip()
        search_sym = "CL=F" if "CRUDE" in sym else "GC=F" if "GOLD" in sym else "^NSEI" if "NIFTY" in sym else f"{sym}.NS"
        
        df = yf.download(search_sym, interval="5m", period="2d", progress=False)
        if df.empty: return "❌ ഡാറ്റ ലഭ്യമല്ല."

        # Simple Moving Average (SMA) ഉപയോഗിച്ചുള്ള സിഗ്നൽ
        df['SMA'] = df['Close'].rolling(window=10).mean()
        last_price = float(df['Close'].iloc[-1])
        sma_val = float(df['SMA'].iloc[-1])

        signal = "BUY 🟢" if last_price > sma_val else "SELL 🔴"
        
        return f"📊 *{sym}*\n💰 വില: {last_price:.2f}\n⚡ സിഗ്നൽ: {signal}"
    except: return "⚠️ Error!"

# Webhooks
@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200

@bot.message_handler(func=lambda message: True)
def handle_telegram(message):
    res = get_trading_signal(message.text)
    bot.reply_to(message, res, parse_mode='Markdown')

@app.route('/')
def home(): return "Bot Active"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
