import telebot
import os
from flask import Flask, request
from groq import Groq
import pandas as pd
import yfinance as yf
import threading
import time
import requests

# API KEYS (Render-ലെ Environment Variables-ൽ ഇവ ഉണ്ടെന്ന് ഉറപ്പാക്കുക)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

client = Groq(api_key=GROQ_API_KEY)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
app = Flask(__name__)

# സൂപ്പർട്രെൻഡ് സിഗ്നൽ കണക്കാക്കുന്ന ഫംഗ്ഷൻ
def get_supertrend_signal(symbol):
    try:
        # 5 മിനിറ്റ് കാൻഡിലിൽ ഡാറ്റ എടുക്കുന്നു
        df = yf.download(symbol, interval="5m", period="1d", progress=False)
        if df.empty: return "ഡാറ്റ ലഭ്യമല്ല."
        
        high, low, close = df['High'], df['Low'], df['Close']
        atr = (high - low).rolling(10).mean() # ATR കണക്കാക്കുന്നു
        upper_band = (high + low) / 2 + 3 * atr
        
        last_close = float(close.iloc[-1])
        last_upper = float(upper_band.iloc[-1])
        
        signal = "BUY 🟢" if last_close > last_upper else "SELL 🔴"
        
        # പേര് ഭംഗിയായി കാണിക്കാൻ
        names = {
            "QM=F": "Crude Oil", 
            "^NSEI": "Nifty 50", 
            "^NSEBANK": "Bank Nifty", 
            "NIFTY_FIN_SERVICE.NS": "Fin Nifty"
        }
        disp_name = names.get(symbol, symbol.replace(".NS", ""))
        
        return f"📊 *({disp_name})*\n💰 വില: {last_close:.2f}\n⚡️ സിഗ്നൽ: {signal}"
    except Exception as e:
        return f"Error: {str(e)}"

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

# മെസ്സേജുകൾ കൈകാര്യം ചെയ്യുന്ന ഭാഗം
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.upper().strip() # മെസ്സേജ് വലിയ അക്ഷരത്തിലേക്ക് മാറ്റുന്നു
    
    # പ്രധാന ഇൻഡക്സുകൾ
    if text == "CRUDE":
        bot.reply_to(message, get_supertrend_signal("QM=F"), parse_mode='Markdown')
    elif text == "NIFTY":
        bot.reply_to(message, get_supertrend_signal("^NSEI"), parse_mode='Markdown')
    elif text == "BANK":
        bot.reply_to(message, get_supertrend_signal("^NSEBANK"), parse_mode='Markdown')
    elif text == "FIN":
        bot.reply_to(message, get_supertrend_signal("NIFTY_FIN_SERVICE.NS"), parse_mode='Markdown')
    
    # ഏതൊരു സ്റ്റോക്ക് പേര് അയച്ചാലും (ഉദാഹരണത്തിന്: SBIN, TATASTEEL)
    else:
        # ഇന്ത്യൻ സ്റ്റോക്കുകൾക്ക് തനിയെ .NS ചേർക്കുന്നു
        symbol = text if ".NS" in text or "=" in text or "^" in text else f"{text}.NS"
        signal_result = get_supertrend_signal(symbol)
        
        # സിഗ്നൽ ലഭിച്ചാൽ അത് അയക്കുന്നു, അല്ലെങ്കിൽ AI വഴി മറുപടി നൽകുന്നു
        if "ലഭ്യമല്ല" in signal_result or "Error" in signal_result:
            try:
                completion = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[{"role": "user", "content": message.text}]
                )
                bot.reply_to(message, completion.choices[0].message.content)
            except:
                bot.reply_to(message, "വിവരങ്ങൾ ലഭ്യമല്ല.")
        else:
            bot.reply_to(message, signal_result, parse_mode='Markdown')

if __name__ == "__main__":
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
