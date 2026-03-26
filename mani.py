import telebot
import os
from flask import Flask
from threading import Thread
from groq import Groq

# Environment Variables
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

if not TELEGRAM_BOT_TOKEN or not GROQ_API_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or GROQ_API_KEY")

# Groq client
client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is Active!"

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # മലയാളത്തിന് മികച്ചത്
            messages=[
                {"role": "system", "content": "നീ ഒരു സഹായി. എല്ലാ ഉത്തരവും മലയാളത്തിൽ തരിക."},
                {"role": "user", "content": message.text}
            ],
            temperature=0.7,
            max_tokens=500
        )
        reply = completion.choices[0].message.content
        bot.reply_to(message, reply)
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

if __name__ == "__main__":
    Thread(target=run_flask).start()
    print("Starting Telegram Bot with Groq...")
    bot.infinity_polling()
