import telebot
import google.generativeai as genai
import os
from flask import Flask
from threading import Threadi

# Tokens
TELEGRAM_BOT_TOKEN = '8638662433:AAGKc6Uo-X06w6i2Sdt5Ul1bIpv_FoxHvJQ'
GEMINI_API_KEY = 'AIzaSyC9CUkynm2xlmBD1Obx6xkff10Dm9vqg_4'

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Paichi Arakkal Bot is running!", 200

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        response = model.generate_content(message.text + " (reply in malayalam briefly as Paichi arakkal)")
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Error: " + str(e))

def run():
    port = int(os.environ.get('PORT', 10000))
    server.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling()

