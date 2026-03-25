import telebot
import google.generativeai as genai
import os
import time
from flask import Flask
from threading import Thread

# Tokens
TELEGRAM_BOT_TOKEN = '8638662433:AAHXPSoEJASPGimZZmwAvov1wgjF5UuzdrM'
GEMINI_API_KEY = 'AIzaSyB_hnsmETwaIGEb-XfNu6PV-zMgyTDISvI'

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Bot is active!", 200

@ message: True
def chat_with_ai(message):
    try:
        response = model.generate_content(message.text + " (reply in malayalam briefly)")
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Error: " + str(e))

def run():
    port = int(os.environ.get('PORT', 10000))
    server.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # പഴയ കണക്ഷൻ ഒഴിവാക്കാൻ ഇത് സഹായിക്കും
    bot.remove_webhook()
    time.sleep(1) 
    
    Thread(target=run).start()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)

