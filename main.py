import telebot
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import requests

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
MY_NUMBER = os.environ.get('MY_WHATSAPP_NUMBER')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
app = Flask(__name__)

def get_crypto_price(symbol):
    try:
        # ബിറ്റ്‌കോയിൻ വില നേരിട്ട് എടുക്കുന്നു
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        data = requests.get(url).json()
        price_usd = float(data['price'])
        
        # കറൻസി നിരക്കുകൾ (സ്ഥിരമായവ)
        price_inr = price_usd * 83.35
        price_aed = price_usd * 3.67
        
        return (f"📊 *{symbol} (Live)*\n"
                f"💵 USD: ${price_usd:,.2f}\n"
                f"🇮🇳 INR: ₹{price_inr:,.2f}\n"
                f"🇦🇪 AED: {price_aed:,.2f} Dh")
    except:
        return None

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').upper().strip()
    
    if "BTC" in msg_body:
        result = get_crypto_price("BTC")
        if not result: result = "⚠️ ഇപ്പോൾ വില ലഭ്യമാക്കാൻ കഴിയുന്നില്ല."
    else:
        result = "💡 ബിറ്റ്‌കോയിൻ വില അറിയാൻ *BTC* എന്ന് അയക്കുക. നിഫ്റ്റിയും മറ്റും നാളെ രാവിലെ ലഭ്യമാകും."
    
    resp = MessagingResponse()
    resp.message().body(result)
    return str(resp)

@bot.message_handler(func=lambda message: True)
def handle_telegram(message):
    msg = message.text.upper()
    if "BTC" in msg:
        res = get_crypto_price("BTC")
        if not res: res = "⚠️ ഡാറ്റ ലഭിക്കുന്നില്ല."
    else:
        res = "BTC എന്ന് അയച്ചു നോക്കൂ!"
    bot.reply_to(message, res, parse_mode='Markdown')

@app.route('/')
def home(): return "Bot is Online"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
