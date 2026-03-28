import telebot
import os
from flask import Flask, request
from groq import Groq

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

if not TELEGRAM_BOT_TOKEN or not GROQ_API_KEY:
    raise ValueError("Missing TELEGRAM_BOT_TOKEN or GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    if update.message:
        chat_with_ai(update.message)
    return 'OK', 200

@app.route('/')
def index():
    return "Bot is Active!"

def chat_with_ai(message):
    print(f"Received: {message.text}")
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "നീ ഒരു സഹായി. എല്ലാ ഉത്തരവും മലയാളത്തിൽ തരിക."},
                {"role": "user", "content": message.text}
            ],
            temperature=0.7,
            max_tokens=500
        )
        reply = completion.choices[0].message.content
        print(f"Reply: {reply}")
        bot.reply_to(message, reply)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, f"Error: {e}")
if __name__ == "__main__":
    # വെബ്ഹുക്ക് സെറ്റ് ചെയ്യാൻ താഴെ വരി ചേർക്കുക
    bot.remove_webhook()
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
import threading
import time
import requests

def keep_alive():
    while True:
        try:
            # നിങ്ങളുടെ ബോട്ടിന്റെ URL ഇവിടെ നൽകുക
            url = "https://my-ai-bot-a1d1.onrender.com/"
            requests.get(url)
            print("Pinged bot to keep it alive!")
        except Exception as e:
            print(f"Ping failed: {e}")
        time.sleep(600) # 10 മിനിറ്റ് (600 സെക്കൻഡ്) ഇടവേള

# ബോട്ട് സ്റ്റാർട്ട് ചെയ്യുന്നതിന് മുൻപായി ഇത് റൺ ചെയ്യുക
threading.Thread(target=keep_alive, daemon=True).start()
