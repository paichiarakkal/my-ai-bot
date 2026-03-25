import telebot
from google import genai
import os
from flask import Flask
from threading import Thread

# Environment Variables എടുക്കുന്നു
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Client സെറ്റ് ചെയ്യുന്നു
client = genai.Client(api_key=GEMINI_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is Active!"

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        # മോഡൽ കൃത്യമായി നൽകുന്നു
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
    # Flask പശ്ചാത്തലത്തിൽ റൺ ചെയ്യാൻ ത്രെഡ് ഉപയോഗിക്കുന്നു
    Thread(target=run_flask).start()
    print("Starting Telegram Bot...")
    bot.infinity_polling()
