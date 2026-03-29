import telebot
import os
from flask import Flask, request
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import threading
import time

# API KEYS
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TWILIO_SID = os.environ.get('TWILIO_SID')
TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
MY_NUMBER = os.environ.get('MY_WHATSAPP_NUMBER')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)
twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
app = Flask(__name__)

# താൽക്കാലികമായി അലേർട്ടുകൾ സൂക്ഷിക്കാൻ
alerts = {"CRUDE": 6500, "GOLD": 75000} 

def get_indicators(df):
    # RSI & Supertrend കണക്കാക്കുന്നു
    df['RSI'] = ta.rsi(df['Close'], length=14)
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=10, multiplier=3)
    df = pd.concat([df, sti], axis=1)
    return df

def get_trading_signal(symbol):
    try:
        sym = symbol.upper().strip()
        search_sym = "CL=F" if "CRUDE" in sym else "GC=F" if "GOLD" in sym else "^NSEI" if "NIFTY" in sym else f"{sym}.NS"
        
        df = yf.download(search_sym, interval="5m", period="2d", progress=False)
        if df.empty: return "❌ വിവരങ്ങൾ ലഭ്യമല്ല."

        df = get_indicators(df)
        last_price = float(df['Close'].iloc[-1])
        rsi_val = float(df['RSI'].iloc[-1])
        trend = df['SUPERTd_10_3.0'].iloc[-1] # 1 = BUY, -1 = SELL

        signal = "Strong BUY 🟢🔥" if (trend == 1 and rsi_val > 50) else "Strong SELL 🔴🔥" if (trend == -1 and rsi_val < 50) else "Neutral ⚪"
        
        return f"📊 *{sym}*\n💰 വില: {last_price:.2f}\n📈 RSI: {rsi_val:.1f}\n⚡ സിഗ്നൽ: {signal}"
    except: return "⚠️ Error!"

# 1. ഓട്ടോമാറ്റിക് പ്രൈസ് അലേർട്ട് സിസ്റ്റം (Background Task)
def check_price_alerts():
    while True:
        try:
            # Crude Oil മാത്രം തൽക്കാലം ചെക്ക് ചെയ്യുന്നു
            df = yf.download("CL=F", period="1d", interval="1m", progress=False)
            curr_price = float(df['Close'].iloc[-1])
            
            if curr_price >= alerts["CRUDE"]:
                msg = f"🔔 ALERT: Crude Oil {curr_price} കടന്നു! ഉടൻ ശ്രദ്ധിക്കുക."
                twilio_client.messages.create(from_='whatsapp:+14155238886', body=msg, to=MY_NUMBER)
                time.sleep(300) # 5 മിനിറ്റ് ബ്രേക്ക്
        except: pass
        time.sleep(60) # ഓരോ മിനിറ്റിലും ചെക്ക് ചെയ്യും

# അലേർട്ട് സിസ്റ്റം സ്റ്റാർട്ട് ചെയ്യുന്നു
threading.Thread(target=check_price_alerts, daemon=True).start()

# --- വാട്സാപ്പ് & ടെലിഗ്രാം ഹാൻഡ്ലേഴ്സ് ---
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    msg_body = request.values.get('Body', '').upper().strip()
    
    # 3. പ്രോഫിറ്റ് ട്രാക്കർ (സിമ്പിൾ ലോജിക്)
    if "PROFIT" in msg_body:
        res = "💰 ഇന്നത്തെ ലാഭം: ₹1,500 (Demo)"
    else:
        res = get_trading_signal(msg_body)
        
    resp = MessagingResponse()
    resp.message().body(res)
    return str(resp)

@app.route(f'/{TELEGRAM_BOT_TOKEN}', methods=['POST'])
def telegram_webhook():
    update = telebot.types.Update.de_json(request.get_data().decode('utf-8'))
    bot.process_new_updates([update])
    return '', 200

@bot.message_handler(func=lambda message: True)
def handle_telegram(message):
    res = get_trading_signal(message.text)
    bot.reply_to(message, res, parse_mode='Markdown')

@app.route('/')
def home(): return "All Systems Active!"

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://my-ai-bot-a1d1.onrender.com/{TELEGRAM_BOT_TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
