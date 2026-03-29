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

# RSI കണക്കാക്കുന്ന ഫംഗ്ഷൻ
def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_trading_signal(symbol):
    try:
        msg = symbol.upper().strip()
        # സിംബലുകൾ സെറ്റ് ചെയ്യുന്നു
        if "BTC" in msg: search_sym = "BTC-USD"
        elif "GOLD" in msg: search_sym = "GC=F"
        elif "CRUDE" in msg: search_sym = "CL=F"
        elif "NIFTY" in msg: search_sym = "^NSEI"
        else: search_sym = f"{msg}.NS"

        # ഇന്ന് ഞായറാഴ്ച ആയതുകൊണ്ട് '1d' ഇന്റർവെൽ ഉപയോഗിക്കുന്നു
        df = yf.download(search_sym, period="30d", interval="1d", progress=False)
        
        if df.empty or len(df) < 15:
            return f"❌ {msg}: ഇപ്പോൾ വിവരങ്ങൾ ലഭ്യമല്ല."

        # വിലയും RSI-യും എടുക്കുന്നു
        last_price_usd = float(df['Close'].iloc[-1])
        df['RSI'] = calculate_rsi(df['Close'])
        rsi_val = float(df['RSI'].iloc[-1])
        
        # കറൻസി റേറ്റ് (ഏകദേശം)
        price_inr = last_price_usd * 83.30
        price_aed = last_price_usd * 3.67
        
        # സിഗ്നൽ ലോജിക്
        signal = "BUY 🟢" if rsi_val > 50 else "SELL 🔴"
        
        return (f"📊 *{msg}*\n"
                f"💵 USD: ${last_price_usd:,.2f}\n"
                f"🇮🇳 INR: ₹{price_inr:,.2f}\n"
                f"🇦🇪 AED: {price_aed:,.2f} Dh\n"
                f"📈 RSI: {rsi_val:.1f}\n"
                f"⚡ സിഗ്നൽ: {signal}")
    except Exception as e:
        return "⚠️ കണക്കുകൂട്ടലിൽ പിശക് നേരിട്ടു."

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
def home(): return "Bot Active"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
