import telebot
import os
from flask import Flask, request
import requests
from twilio.twiml.messaging_response import MessagingResponse

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
app = Flask(__name__)

def get_btc_price():
    try:
        # Binance API (വളരെ വേഗത്തിൽ വില ലഭിക്കും)
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
            resp.message("⚠️ ഡാറ്റ ലഭ്യമല്ല. അല്പം കഴിഞ്ഞ് ശ്രമിക്കൂ.")
    else:
        resp.message("💡 ബിറ്റ്‌കോയിൻ വില അറിയാൻ *BTC* എന്ന് അയക്കുക.")
    
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
    return "Bot is Live! WhatsApp URL: /whatsapp"

if __name__ == "__main__":
    # Render URL സെറ്റ് ചെയ്യുന്നു
    RENDER_URL = f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=RENDER_URL)
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
