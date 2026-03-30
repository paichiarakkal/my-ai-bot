import telebot
import os
from flask import Flask, request
import requests
import yfinance as yf
from twilio.twiml.messaging_response import MessagingResponse

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
app = Flask(__name__)

def get_market_data():
    try:
        # Nifty 50 and Crude Oil (MCX symbol style)
        nifty = yf.Ticker("^NSEI")
        crude = yf.Ticker("CL=F") # International Crude Oil
        
        n_price = nifty.history(period="1d")['Close'].iloc[-1]
        c_price = crude.history(period="1d")['Close'].iloc[-1]
        
        return (f"📉 *MARKET UPDATE*\n"
                f"🇮🇳 Nifty 50: {n_price:,.2f}\n"
                f"🛢️ Crude Oil: ${c_price:,.2f}\n"
                f"━━━━━━━━━━━━━━")
    except:
        return "⚠️ മാർക്കറ്റ് ഡാറ്റ ലഭ്യമല്ല."

def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,inr,aed"
        r = requests.get(url, timeout=10)
        data = r.json()
        if 'bitcoin' in data:
            btc = data['bitcoin']
            return (f"📊 *BITCOIN LIVE*\n"
                    f"💵 USD: ${btc['usd']:,.2f}\n"
                    f"🇮🇳 INR: ₹{btc['inr']:,.2f}\n"
                    f"🇦🇪 AED: {btc['aed']:,.2f} Dh")
        return None
    except:
        return None

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    
    if "btc" in msg_body:
        resp.message(get_btc_price())
    elif "market" in msg_body or "nifty" in msg_body or "crude" in msg_body:
        resp.message(get_market_data())
    else:
        resp.message("💡 വില അറിയാൻ താഴെ ഉള്ളവ അയക്കുക:\n1. *BTC*\n2. *Market* (Nifty & Crude)")
    
    return str(resp)

@app.route('/')
def home():
    return "Bot is Running with Market Data! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
