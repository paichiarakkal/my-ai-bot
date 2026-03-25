import telebot
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# Updated Tokens
TELEGRAM_BOT_TOKEN = '8638662433:AAGebohbfT4OAqiZ8Jz6snrWFYwd4tFohXg'
GEMINI_API_KEY = 'AIzaSyC19R9rkdHHUN8bgz5WoDbOM7lulLprpAU'

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-001')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
server = Flask(__name__)

@server.route("/")
def webhook():
    return "Paichi Arakkal Bot is running!", 200

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        # Prompt: മലയാളത്തിൽ മറുപടി നൽകാൻ നിർദ്ദേശിക്കുന്നു
        response = model.generate_content(message.text + " (reply in malayalam briefly as Paichi arakkal)")
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Error: " + str(e))

def run():
    port = int(os.environ.get('PORT', 10000))
    server.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    Thread(target=run).start()
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
