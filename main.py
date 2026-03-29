import telebot
import os
from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
app = Flask(__name__)

def get_crypto_price():
    try:
        # ബിനാൻസ് API നേരിട്ട് ഉപയോഗിക്കുന്നു (കൂടുതൽ വേഗത്തിൽ കിട്ടും)
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'price' in data:
            price_usd = float(data['price'])
            # ഏകദേശ കണക്ക് (INR: 83.5, AED: 3.67)
            return (f"📊 *BITCOIN (Live)*\n"
                    f"💵 USD: ${price_usd:,.2f}\n"
                    f"🇮🇳 INR: ₹{price_usd * 83.5:,.2f}\n"
                    f"🇦🇪 AED: {price_usd * 3.67:,.2f} Dh\n"
                    f"━━━━━━━━━━━━━━")
        return None
    except:
        return None

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    
    if "btc" in msg_body:
        result = get_crypto_price()
        if result:
            resp.message(result)
        else:
            resp.message("⚠️ ഡാറ്റ എടുക്കാൻ പറ്റിയില്ല. ഒന്നുകൂടി ശ്രമിക്കൂ.")
    else:
        resp.message("💡 ബിറ്റ്‌കോയിൻ വില അറിയാൻ *BTC* എന്ന് അയക്കുക.")
    
    return str(resp)

@app.route('/')
def home():
    return "Bot is Live 🚀"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
