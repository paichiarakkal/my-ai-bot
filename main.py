import telebot
import os
from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

# API KEYS (Render Environment Variables-ൽ സെറ്റ് ചെയ്തത്)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
app = Flask(__name__)

def get_btc_price():
    try:
        # കൂടുതൽ സ്റ്റേബിൾ ആയ CoinGecko API
        url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd,inr,aed"
        r = requests.get(url, timeout=10)
        data = r.json()
        
        if 'bitcoin' in data:
            btc = data['bitcoin']
            return (f"📊 *BITCOIN LIVE*\n"
                    f"💵 USD: ${btc['usd']:,.2f}\n"
                    f"🇮🇳 INR: ₹{btc['inr']:,.2f}\n"
                    f"🇦🇪 AED: {btc['aed']:,.2f} Dh\n"
                    f"━━━━━━━━━━━━━━")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# WhatsApp Webhook
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    
    if "btc" in msg_body:
        result = get_btc_price()
        if result:
            resp.message(result)
        else:
            resp.message("⚠️ ഡാറ്റ ലഭ്യമല്ല. ഒന്ന് കൂടി ശ്രമിക്കൂ.")
    else:
        resp.message("💡 BTC വില അറിയാൻ *BTC* എന്ന് അയക്കുക.")
    
    return str(resp)

# Telegram Webhook Router
@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

# Telegram Message Handler
@bot.message_handler(func=lambda message: True)
def handle_telegram(message):
    msg = message.text.lower()
    if "btc" in msg:
        res = get_btc_price()
        if res:
            bot.reply_to(message, res, parse_mode='Markdown')
        else:
            bot.reply_to(message, "⚠️ ഡാറ്റ ലഭിക്കുന്നില്ല.")
    else:
        bot.reply_to(message, "BTC എന്ന് അയച്ച് ബിറ്റ്‌കോയിൻ വില അറിയാം!")

@app.route('/')
def home():
    return "Bot is Active! 🚀"

if __name__ == "__main__":
    # Render URL സെറ്റ് ചെയ്യുന്നു
    RENDER_URL = f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL)
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
