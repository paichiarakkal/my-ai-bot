import telebot
import os
from flask import Flask, request
import requests
import yfinance as yf
from twilio.twiml.messaging_response import MessagingResponse

# Flask App configuration
app = Flask(__name__)

# നിങ്ങളുടെ പുതിയ ടെലിഗ്രാം ടോക്കൺ
TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

def get_market_data():
    try:
        # Nifty 50 and International Crude Oil
        nifty = yf.Ticker("^NSEI")
        crude = yf.Ticker("CL=F")
        
        n_price = nifty.history(period="1d")['Close'].iloc[-1]
        c_price = crude.history(period="1d")['Close'].iloc[-1]
        
        return (f"📉 *MARKET UPDATE*\n\n"
                f"🇮🇳 Nifty 50: {n_price:,.2f}\n"
                f"🛢️ Crude Oil: ${c_price:,.2f}\n"
                f"━━━━━━━━━━━━━━\n"
                f"Updated Just Now 🚀")
    except Exception as e:
        return "⚠️ മാർക്കറ്റ് ഡാറ്റ ഇപ്പോൾ ലഭ്യമല്ല."

def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,inr,aed"
        data = requests.get(url, timeout=10).json()
        btc = data['bitcoin']
        return (f"📊 *BITCOIN LIVE*\n\n"
                f"💵 USD: ${btc['usd']:,.2f}\n"
                f"🇮🇳 INR: ₹{btc['inr']:,.2f}\n"
                f"🇦🇪 AED: {btc['aed']:,.2f} Dh")
    except:
        return "⚠️ BTC ഡാറ്റ ലഭ്യമല്ല."

# WhatsApp Webhook
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    
    if "btc" in msg_body:
        resp.message(get_btc_price())
    else:
        # Default to Market Data for Nifty/Crude/Market keywords
        resp.message(get_market_data())
    return str(resp)

# Telegram Webhook & Handlers
@bot.message_handler(func=lambda message: True)
def telegram_reply(message):
    msg_text = message.text.lower()
    if "btc" in msg_text:
        bot.reply_to(message, get_btc_price())
    else:
        bot.reply_to(message, get_market_data())

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route('/')
def home():
    return "AI Trading Bot is Online! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
def get_market_data():
    try:
        # Nifty 50
        nifty = yf.Ticker("^NSEI")
        # International Crude Oil (USD)
        crude_intl = yf.Ticker("CL=F")
        
        n_price = nifty.history(period="1d")['Close'].iloc[-1]
        c_intl_price = crude_intl.history(period="1d")['Close'].iloc[-1]
        
        # MCX Crude Oil-ന് ഏകദേശമായി ഡോളർ വിലയെ കറൻസി റേറ്റ് കൊണ്ട് ഗുണിക്കുന്നു
        # (യഥാർത്ഥ MCX വിലകൾക്ക് പെയ്ഡ് API വേണം, ഇത് സൗജന്യമായുള്ള വഴിയാണ്)
        mcx_approx = c_intl_price * 83.5 * 1.1 # ഒരു ഏകദേശ കണക്ക്
        
        return (f"📉 *MARKET UPDATE*\n\n"
                f"🇮🇳 Nifty 50: {n_price:,.2f}\n"
                f"🛢️ Crude (Intl): ${c_intl_price:,.2f}\n"
                f"🇮🇳 MCX Approx: ₹{mcx_approx:,.0f}\n"
                f"━━━━━━━━━━━━━━")
    except:
        return "⚠️ ഡാറ്റ ലഭ്യമല്ല."
