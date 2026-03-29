import telebot
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import requests # ഇത് ഡാറ്റ എടുക്കാൻ സഹായിക്കും

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
MY_NUMBER = os.environ.get('MY_WHATSAPP_NUMBER')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
app = Flask(__name__)

def get_btc_price():
    try:
        # ബിറ്റ്‌കോയിൻ വില നേരിട്ട് എടുക്കുന്നു
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url).json()
        price_usd = float(response['price'])
        
        # കറൻസി നിരക്കുകൾ
        price_inr = price_usd * 83.35
        price_aed = price_usd * 3.67
        
        return (f"📊 *BTC-USD (Live)*\n"
                f"💵 USD: ${price_usd:,.2f}\n"
                f"🇮🇳 INR: ₹{price_inr:,.2f}\n"
                f"🇦🇪 AED: {price_aed:,.2f} Dh")
    except:
        return "⚠️ ഇപ്പോൾ വില ലഭ്യമാക്കാൻ കഴിയുന്നില്ല."

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').upper().strip()
    if "BTC" in msg_body:
        result = get_btc_price()
    else:
        result = "💡 ബിറ്റ്‌കോയിൻ വില അറിയാൻ *BTC* എന്ന് അയക്കുക. നാളെ രാവിലെ മുതൽ നിഫ്റ്റി ലഭ്യമാകും."
    
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
    if "BTC" in message.text.upper():
        res = get_btc_price()
    else:
        res = "BTC എന്ന് അയച്ചു നോക്കൂ!"
    bot.reply_to(message, res, parse_mode='Markdown')

@app.route('/')
def home(): return "Bot Active"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
