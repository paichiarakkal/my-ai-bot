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

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
app = Flask(__name__)

def get_crypto_price():
    try:
        # CoinGecko API ഉപയോഗിച്ച് ബിറ്റ്‌കോയിൻ വില എടുക്കുന്നു
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,inr,aed"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        price_usd = data['bitcoin']['usd']
        price_inr = data['bitcoin']['inr']
        price_aed = data['bitcoin']['aed']
        
        return (f"📊 *BITCOIN (Live)*\n"
                f"💵 USD: ${price_usd:,.2f}\n"
                f"🇮🇳 INR: ₹{price_inr:,.2f}\n"
                f"🇦🇪 AED: {price_aed:,.2f} Dh\n"
                f"━━━━━━━━━━━━━━")
    except Exception as e:
        print(f"Error: {e}")
        return None

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    
    if "btc" in msg_body:
        result = get_crypto_price()
        if result:
            resp.message().body(result)
        else:
            resp.message().body("⚠️ ഇപ്പോൾ വില ലഭ്യമല്ല. അല്പം കഴിഞ്ഞ് ശ്രമിക്കൂ.")
    else:
        resp.message().body("💡 ബിറ്റ്‌കോയിൻ വില അറിയാൻ *BTC* എന്ന് അയക്കുക.")
    
    return str(resp)

@bot.message_handler(func=lambda message: True)
def handle_telegram(message):
    msg = message.text.lower()
    if "btc" in msg:
        res = get_crypto_price()
        if res:
            bot.reply_to(message, res, parse_mode='Markdown')
        else:
            bot.reply_to(message, "⚠️ ഡാറ്റ ലഭിക്കുന്നില്ല.")
    else:
        bot.reply_to(message, "BTC എന്ന് അയച്ചു നോക്കൂ!")

@app.route('/')
def home(): return "Bot is Online"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
    
