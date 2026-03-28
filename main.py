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
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
app = Flask(__name__)

# സിഗ്നൽ കണക്കാക്കുന്ന ഫംഗ്ഷൻ
def get_supertrend_signal(symbol):
    try:
        # MCX Crude Oil ആണെങ്കിൽ മാത്രം ഈ സിംബൽ ഉപയോഗിക്കുന്നു
        if symbol == "CRUDE_MCX":
            search_symbol = "MCXCRUDEOIL1!" # അല്ലെങ്കിൽ "CRUDEOIL.NS" പരീക്ഷിക്കാം
        else:
            search_symbol = symbol

        # 5 മിനിറ്റ് ഇന്റർവലിൽ ഡാറ്റ എടുക്കുന്നു
        df = yf.download(search_symbol, interval="5m", period="2d", progress=False)
        
        if df.empty or len(df) < 11: 
            return "വിവരങ്ങൾ ലഭ്യമല്ല. മാർക്കറ്റ് ഓഫ് ആണോ എന്ന് നോക്കുക."
        
        high, low, close = df['High'], df['Low'], df['Close']
        atr = (high - low).rolling(10).mean()
        upper_band = (high + low) / 2 + 3 * atr
        
        last_close = float(close.iloc[-1])
        last_upper = float(upper_band.iloc[-1])
        
        signal = "BUY 🟢" if last_close > last_upper else "SELL 🔴"
        
        # പേര് സെറ്റ് ചെയ്യുന്നു
        names = {
            "CRUDE_MCX": "Crude Oil (MCX)", 
            "^NSEI": "Nifty 50", 
            "^NSEBANK": "Bank Nifty", 
            "NIFTY_FIN_SERVICE.NS": "Fin Nifty"
        }
        disp_name = names.get(symbol, symbol.replace(".NS", ""))
        
        return f"📊 *({disp_name})*\n💰 വില: ₹{last_close:.2f}\n⚡️ സിഗ്നൽ: {signal}"
    except:
        return "ഡാറ്റ എടുക്കുന്നതിൽ തടസ്സം നേരിട്ടു."

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    return 'Forbidden', 403

@app.route('/')
def index(): return "Bot is Active!"

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.upper().strip()
    
    # പ്രധാന ഇൻഡക്സുകൾ
    if "CRUDE" in text:
        bot.reply_to(message, get_supertrend_signal("CRUDE_MCX"), parse_mode='Markdown')
    elif "BANK" in text:
        bot.reply_to(message, get_supertrend_signal("^NSEBANK"), parse_mode='Markdown')
    elif "FIN" in text:
        bot.reply_to(message, get_supertrend_signal("NIFTY_FIN_SERVICE.NS"), parse_mode='Markdown')
    elif "NIFTY" in text or "GIFT" in text:
        bot.reply_to(message, get_supertrend_signal("^NSEI"), parse_mode='Markdown')
    
    # സ്റ്റോക്ക് സിഗ്നലുകൾ (ഉദാ: SBIN, TATASTEEL)
    else:
        symbol = text if any(x in text for x in [".NS", "=", "^"]) else f"{text}.NS"
        result = get_supertrend_signal(symbol)
        
        if "വിവരങ്ങൾ ലഭ്യമല്ല" in result:
            try:
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": message.text}]
                )
                bot.reply_to(message, completion.choices[0].message.content)
            except:
                bot.reply_to(message, result)
        else:
            bot.reply_to(message, result, parse_mode='Markdown')

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
