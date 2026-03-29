import telebot
import os
from flask import Flask, request
from twilio.rest import Client
import yfinance as yf
import threading
import time

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
MY_NUMBER = os.environ.get('MY_WHATSAPP_NUMBER')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
app = Flask(__name__)

def send_whatsapp(msg_text):
    try:
        twilio_client.messages.create(
            from_='whatsapp:+14155238886',
            body=msg_text,
            to=MY_NUMBER
        )
    except Exception as e:
        print(f"WhatsApp Error: {e}")

def get_trading_signal(symbol):
    try:
        search_symbol = "MCXCRUDEOIL1!" if "CRUDE" in symbol.upper() else symbol
        df = yf.download(search_symbol, interval="5m", period="2d", progress=False)
        if df.empty or len(df) < 20: return "വിവരങ്ങൾ ലഭ്യമല്ല. മാർക്കറ്റ് ഓഫ് ആണോ എന്ന് നോക്കുക."
        
        close = df['Close'].iloc[-1]
        st_signal = "BUY 🟢" if close > df['High'].iloc[-2] else "SELL 🔴" # ലളിതമായ സിഗ്നൽ
        
        return f"📊 *({symbol})*\n💰 വില: ₹{close:.2f}\n⚡️ സിഗ്നൽ: {st_signal}"
    except: return "ഡാറ്റ എടുക്കുന്നതിൽ തടസ്സം നേരിട്ടു."

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    res = get_trading_signal(message.text.upper())
    bot.reply_to(message, res, parse_mode='Markdown')
    send_whatsapp(res) # ഇത് വാട്സാപ്പിലേക്ക് നോട്ടിഫിക്കേഷൻ അയക്കും

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
