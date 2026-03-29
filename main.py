import telebot
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
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
        if "BTC" in sym: search_sym = "BTC-USD"
        elif "GOLD" in sym: search_sym = "GC=F"
        elif "CRUDE" in sym: search_sym = "CL=F"
        elif "NIFTY" in sym: search_sym = "^NSEI"
        else: search_sym = f"{sym}.NS"

        # ഡാറ്റ എടുക്കുന്നു
        df = yf.download(search_sym, period="5d", interval="1h", progress=False)
        
        if df.empty: return f"❌ {sym}: ഡാറ്റ ലഭ്യമല്ല."

        last_price_usd = float(df['Close'].iloc[-1])
        
        # കറൻസി കൺവേർഷൻ (ഏകദേശ നിരക്ക്)
        price_inr = last_price_usd * 83.30
        price_aed = last_price_usd * 3.67
        
        # സിഗ്നൽ (ലളിതമായത്)
        signal = "BUY 🟢" if last_price_usd > float(df['Open'].iloc[-1]) else "SELL 🔴"
        
        return (f"📊 *{sym}*\n"
                f"💵 USD: ${last_price_usd:.2f}\n"
                f"🇮🇳 INR: ₹{price_inr:.2f}\n"
                f"🇦🇪 AED: {price_aed:.2f} Dh\n"
                f"⚡ സിഗ്നൽ: {signal}")
    except:
        return "⚠️ Error!"

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

@app.route('/')
def home(): return "Bot Active with Currency Support"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
