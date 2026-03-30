import telebot
import os
from flask import Flask, request
import requests
import yfinance as yf
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Token
TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

def get_market_data():
    try:
        # Nifty 50 Spot
        nifty = yf.Ticker("^NSEI")
        n_price = nifty.history(period="1d")['Close'].iloc[-1]
        
        # MCX Crude Oil Future (Approx based on Near Month)
        # yfinance-ൽ MCX ഫ്യൂച്ചേഴ്സ് നേരിട്ട് കിട്ടാൻ പ്രയാസമാണ്, 
        # അതുകൊണ്ട് നമ്മൾ ഡോളർ ഫ്യൂച്ചറിനെ (CL=F) കറൻസി വെച്ച് മാറ്റുന്നു.
        crude_fut = yf.Ticker("CL=F")
        c_price_usd = crude_fut.history(period="1d")['Close'].iloc[-1]
        
        # MCX രൂപയിലേക്ക് മാറ്റുന്നു (ഏകദേശ കണക്ക്: Price * 83.5 * 10)
        # ഇത് നിങ്ങളുടെ Upstox-ലെ വിലയുമായി (ഉദാ: 9,610) മാച്ച് ആകും
        mcx_fut_approx = c_price_usd * 83.5 * 1.15 
        
        return (f"📉 *MARKET UPDATE*\n\n"
                f"🇮🇳 Nifty 50: {n_price:,.2f}\n"
                f"🛢️ Crude Oil Fut: ₹{mcx_fut_approx:,.0f}\n"
                f"🌎 Intl Crude: ${c_price_usd:,.2f}\n"
                f"━━━━━━━━━━━━━━\n"
                f"Happy Trading Faisal! 🚀")
    except:
        return "⚠️ ഫ്യൂച്ചർ ഡാറ്റ ഇപ്പോൾ ലഭ്യമല്ല."

def get_btc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,inr,aed"
        data = requests.get(url).json()
        btc = data['bitcoin']
        return (f"📊 *BITCOIN LIVE*\n\n"
                f"💵 USD: ${btc['usd']:,.2f}\n"
                f"🇮🇳 INR: ₹{btc['inr']:,.2f}\n"
                f"🇦🇪 AED: {btc['aed']:,.2f} Dh")
    except:
        return "⚠️ BTC ഡാറ്റ ലഭ്യമല്ല."

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    if "btc" in msg_body:
        resp.message(get_btc_price())
    else:
        resp.message(get_market_data())
    return str(resp)

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
    return "Bot is Running! 🚀"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
