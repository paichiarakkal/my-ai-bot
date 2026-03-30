import telebot
import os

# നിങ്ങളുടെ പുതിയ ടോക്കൺ ഇവിടെ നേരിട്ട് നൽകുന്നു
TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

# ടെലിഗ്രാം മെസ്സേജ് വരുമ്പോൾ പ്രവർത്തിക്കാൻ
@bot.message_handler(func=lambda message: True)
def echo_all(message):
    msg_text = message.text.lower()
    
    if "btc" in msg_text:
        bot.reply_to(message, get_btc_price())
    elif "market" in msg_text or "nifty" in msg_text or "crude" in msg_text:
        bot.reply_to(message, get_market_data())
    else:
        bot.reply_to(message, "💡 വില അറിയാൻ BTC അല്ലെങ്കിൽ Market എന്ന് അയക്കൂ.")

# താഴെ കാണുന്ന വരി ടെലിഗ്രാം Webhook കണക്ട് ചെയ്യാൻ സഹായിക്കും
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200
