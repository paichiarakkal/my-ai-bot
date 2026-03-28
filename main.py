import telebot
import os
from flask import Flask, request
from groq import Groq
import pandas as pd
import yfinance as yf
import threading
import time
import requests

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
app = Flask(__name__)

# സൂപ്പർട്രെൻഡ് സിഗ്നൽ കണക്കാക്കാനുള്ള ഫംഗ്ഷൻ
def get_supertrend_signal(symbol):
    try:
        # 5 മിനിറ്റ് കാൻഡിൽ ഡാറ്റ എടുക്കുന്നു
        df = yf.download(symbol, interval="5m", period="2d")
        if df.empty: return "ഡാറ്റ ലഭ്യമല്ല."

        # ATR കണക്കാക്കുന്നു
        high_low = df['High'] - df['Low']
        high_cp = abs(df['High'] - df['Close'].shift())
        low_cp = abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_cp, low_cp], axis=1).max(axis=1)
        atr = tr.ewm(alpha=1/10, adjust=False).mean()

        hl2 = (df['High'] + df['Low']) / 2
        upperband = hl2 + (3 * atr)
        
        last_close = df['Close'].iloc[-1]
        last_upper = upperband.iloc[-1]
        
        signal = "BUY 🟢" if last_close > last_upper else "SELL 🔴"
        return f"📊 *{symbol}* \n💰 വില: {round(last_close, 2)}\n⚡ സിഗ്നൽ: {signal}"
    except Exception as e:
        return f"Error: {e}"

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return "Bot is Active!"

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    text = message.text.lower()
    
    # ട്രേഡിംഗ് കമാൻഡുകൾ
    if "crude" in text:
        bot.reply_to(message, get_supertrend_signal("CL=F"), parse_mode='Markdown')
    elif "nifty" in text:
        bot.reply_to(message, get_supertrend_signal("^NSEI"), parse_mode='Markdown')
    
    # മറ്റുള്ളവയ്ക്ക് AI മറുപടി നൽകുന്നു
    else:
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[
                    {"role": "system", "content": "നീ ഒരു മലയാളം സഹായിയാണ്."},
                    {"role": "user", "content": message.text}
                ]
            )
            bot.reply_to(message, completion.choices[0].message.content)
        except:
            bot.reply_to(message, "ക്ഷമിക്കണം, എനിക്ക് ഇപ്പോൾ മറുപടി നൽകാൻ കഴിയുന്നില്ല.")

# ബോട്ട് ഓഫ് ആകാതിരിക്കാൻ (Keep Alive)
def keep_alive():
    while True:
        try:
            requests.get("https://my-ai-bot-a1d1.onrender.com/")
        except: pass
        time.sleep(600)

if __name__ == "__main__":
    threading.Thread(target=keep_alive, daemon=True).start()
    bot.remove_webhook()
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
