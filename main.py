import telebot
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import yfinance as yf
import threading
import time

# API KEYS (Render-ൽ നിങ്ങൾ നേരത്തെ സെറ്റ് ചെയ്തവ)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
MY_NUMBER = os.environ.get('MY_WHATSAPP_NUMBER')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
app = Flask(__name__)

# വാട്സാപ്പിലേക്ക് മെസ്സേജ് അയക്കുന്ന ഫംഗ്ഷൻ
def send_whatsapp_msg(msg_text):
    try:
        twilio_client.messages.create(
            from_='whatsapp:+14155238886', # Twilio Sandbox Number
            body=msg_text,
            to=MY_NUMBER
        )
    except Exception as e:
        print(f"WhatsApp Error: {e}")

# സിഗ്നൽ കണക്കാക്കുന്ന ഫംഗ്ഷൻ
def get_trading_signal(symbol):
    try:
        search_symbol = "MCXCRUDEOIL1!" if "CRUDE" in symbol.upper() else symbol
        # NSE ഓഹരികൾക്ക് .NS ചേർക്കുന്നു
        if symbol.upper() not in ["^NSEI", "^NSEBANK", "MCXCRUDEOIL1!"]:
            search_symbol = f"{symbol.upper()}.NS"
            
        df = yf.download(search_symbol, interval="5m", period="2d", progress=False)
        if df.empty: return "ഡാറ്റ ലഭ്യമല്ല. ടിക്കർ ശരിയാണോ എന്ന് നോക്കുക."
        
        last_price = float(df['Close'].iloc[-1])
        # ലളിതമായ സിഗ്നൽ ലോജിക്
        signal = "BUY 🟢" if last_price > float(df['Open'].iloc[-1]) else "SELL 🔴"
        
        return f"📊 *{symbol.upper()}*\n💰 വില: ₹{last_price:.2f}\n⚡️ സിഗ്നൽ: {signal}"
    except:
        return "സിഗ്നൽ എടുക്കുന്നതിൽ ചെറിയൊരു തടസ്സം."

# --- വാട്സാപ്പ് വഴി മെസ്സേജ് വരുമ്പോൾ (Webhook) ---
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    incoming_msg = request.values.get('Body', '').upper().strip()
    # വാട്സാപ്പിൽ വന്ന മെസ്സേജിനുള്ള മറുപടി കണക്കാക്കുന്നു
    result = get_trading_signal(incoming_msg)
    
    resp = MessagingResponse()
    msg = resp.message()
    msg.body(result)
    return str(resp)

# --- ടെലിഗ്രാം വഴി മെസ്സേജ് വരുമ്പോൾ ---
@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200

@bot.message_handler(func=lambda message: True)
def handle_telegram(message):
    res = get_trading_signal(message.text.upper())
    bot.reply_to(message, res, parse_mode='Markdown')
    # ടെലിഗ്രാമിൽ ചോദിക്കുമ്പോൾ വാട്സാപ്പിലും നോട്ടിഫിക്കേഷൻ അയക്കുന്നു
    send_whatsapp_msg(f"Telegram Notification:\n{res}")

@app.route('/')
def home(): return "Bot is Active!"

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
