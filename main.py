import telebot
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import yfinance as yf
import pandas as pd
import numpy as np
import time

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
MY_NUMBER = os.environ.get('MY_WHATSAPP_NUMBER')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
app = Flask(__name__)

# സൂപ്പർട്രെൻഡ് ലോജിക് (ലൈബ്രറി ഇല്ലാതെ)
def calculate_supertrend(df, period=10, multiplier=3):
    hl2 = (df['High'] + df['Low']) / 2
    df['atr'] = df['High'].combine(df['Close'].shift(), max) - df['Low'].combine(df['Close'].shift(), min)
    df['atr'] = df['atr'].rolling(period).mean()
    df['upperband'] = hl2 + (multiplier * df['atr'])
    df['lowerband'] = hl2 - (multiplier * df['atr'])
    df['trend'] = 1
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > df['upperband'].iloc[i-1]: df.loc[df.index[i], 'trend'] = 1
        elif df['Close'].iloc[i] < df['lowerband'].iloc[i-1]: df.loc[df.index[i], 'trend'] = -1
        else: df.loc[df.index[i], 'trend'] = df['trend'].iloc[i-1]
    return df

def get_trading_signal(symbol):
    try:
        sym = symbol.upper().strip()
        # അവധി ദിവസങ്ങളിൽ ഡാറ്റ കിട്ടാൻ പീരിയഡ് 5d ആക്കുന്നു
        if "GOLD" in sym: search_sym = "GC=F"
        elif "CRUDE" in sym: search_sym = "CL=F"
        elif "NIFTY" in sym: search_sym = "^NSEI"
        else: search_sym = f"{sym}" if "-" in sym else f"{sym}.NS"

        # ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു
        df = yf.download(search_sym, interval="15m", period="5d", progress=False)
        
        if df.empty or len(df) < 11:
            return f"❌ {sym}: ഡാറ്റ ലഭ്യമല്ല. സിംബൽ ശരിയാണോ എന്ന് നോക്കുക."

        df = calculate_supertrend(df)
        last_price = float(df['Close'].iloc[-1])
        trend = df['trend'].iloc[-1]
        
        signal = "BUY 🟢" if trend == 1 else "SELL 🔴"
        
        return f"📊 *{sym}*\n💰 വില: {last_price:.2f}\n⚡ സിഗ്നൽ: {signal}"
    except Exception as e:
        return "⚠️ കണക്കുകൂട്ടലിൽ തടസ്സം."

# --- Webhooks ---
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').upper().strip()
    result = get_trading_signal(msg_body)
    resp = MessagingResponse()
    resp.message().body(result)
    return str(resp)

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200

@bot.message_handler(func=lambda message: True)
def handle_telegram(message):
    res = get_trading_signal(message.text)
    bot.reply_to(message, res, parse_mode='Markdown')
    try:
        twilio_client.messages.create(from_='whatsapp:+14155238886', body=res, to=MY_NUMBER)
    except: pass

@app.route('/')
def home(): return "Bot is Online and Ready!"

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
