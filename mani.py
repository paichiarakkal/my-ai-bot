import telebot
from google import genai
import os
from flask import Flask
from threading import Thread

# കീകൾ എടുക്കുന്നു
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running!"

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=message.text + " (reply in Malayalam)"
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    # Flask സെർവർ പശ്ചാത്തലത്തിൽ തുടങ്ങുന്നു
    Thread(target=run_flask).start()
    # ബോട്ട് റൺ ചെയ്യുന്നു
    print("Bot is starting...")
    bot.infinity_polling()
