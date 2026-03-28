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

# 5 മിനിറ്റ് ഇടവേളയിൽ സെർവർ ഉണർത്തുന്ന ഫംഗ്ഷൻ
def keep_alive():
    while True:
        try:
            # നിങ്ങളുടെ Render URL
            requests.get("https://my-ai-bot-a1d1.onrender.com/")
            print("Pinged server (5 min interval)...")
        except:
            print("Ping failed")
        time.sleep(300) # 5 മിനിറ്റ് = 300 സെക്കൻഡ്

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_trading_signal(symbol):
    try:
        search_symbol = "MCXCRUDEOIL1!" if symbol == "CRUDE_MCX" else symbol
        df = yf.download(search_symbol, interval="5m", period="2d", progress=False)
        
        if df.empty or len(df) < 20: 
            return "വിവരങ്ങൾ ലഭ്യമല്ല. മാർക്കറ്റ് ഓഫ് ആണോ എന്ന് നോക്കുക."
        
        close_prices = df['Close']
        high_prices = df['High']
        low_prices = df['Low']

        atr = (high_prices - low_prices).rolling(10).mean()
        upper_band = (high_prices + low_prices) / 2 + 3 * atr
        last_close = float(close_prices.iloc[-1])
        st_signal = "BUY 🟢" if last_close > float(upper_band.iloc[-1]) else "SELL 🔴"

        rsi_values = calculate_rsi(close_prices)
        last_rsi = float(rsi_values.iloc[-1])
        rsi_status = "(Overbought ⚠️)" if last_rsi >= 70 else ("(Oversold ⚠️)" if last_rsi <= 30 else "")

        names = {"CRUDE_MCX": "Crude Oil (MCX)", "^NSEI": "Nifty 50", "^NSEBANK": "Bank Nifty"}
        disp_name = names.get(symbol, symbol.replace(".NS", ""))
        currency = "₹" if "MCX" in symbol or ".NS" in symbol or "^" in symbol else "$"
        
        return (f"📊 *({disp_name})*\n💰 വില: {currency}{last_close:.2f}\n⚡️ സിഗ്നൽ: {st_signal}\n📈 RSI: {last_rsi:.2f} {rsi_status}")
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
    if "CRUDE" in text:
        bot.reply_to(message, get_trading_signal("CRUDE_MCX"), parse_mode='Markdown')
    elif "BANK" in text:
        bot.reply_to(message, get_trading_signal("^NSEBANK"), parse_mode='Markdown')
    elif "NIFTY" in text:
        bot.reply_to(message, get_trading_signal("^NSEI"), parse_mode='Markdown')
    else:
        symbol = text if any(x in text for x in [".NS", "=", "^"]) else f"{text}.NS"
        result = get_trading_signal(symbol)
        if "വിവരങ്ങൾ ലഭ്യമല്ല" in result:
            try:
                completion = client.chat.completions.create(model="llama3-70b-8192", messages=[{"role": "user", "content": message.text}])
                bot.reply_to(message, completion.choices[0].message.content)
            except: bot.reply_to(message, result)
        else:
            bot.reply_to(message, result, parse_mode='Markdown')

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    
    # Keep Alive ത്രെഡ് സ്റ്റാർട്ട് ചെയ്യുന്നു
    threading.Thread(target=keep_alive, daemon=True).start()
    
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
