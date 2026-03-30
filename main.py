import telebot
import os
from flask import Flask, request
import yfinance as yf
import pandas as pd
import requests
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

def get_market_analysis():
    try:
        # India VIX (Fear Index)
        vix = yf.Ticker("^INDIAVIX").history(period="1d")['Close'].iloc[-1]
        
        symbols = {
            "Nifty 50": "^NSEI",
            "Bank Nifty": "^NSEBANK",
            "Fin Nifty": "NIFTY_FIN_SERVICE.NS",
            "Crude Fut": "CL=F"
        }
        
        output = f"📊 *PROFESSIONAL ANALYSIS*\n⚠️ VIX: {vix:.2f} (Volatility)\n\n"
        
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="1mo", interval="5m")
            if df.empty: continue
            
            last_price = df['Close'].iloc[-1]
            
            # 1. MOVING AVERAGE (20 EMA)
            ema_20 = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            ma_signal = "🟢 ABOVE EMA" if last_price > ema_20 else "🔴 BELOW EMA"
            
            # 2. RSI (14) - Relative Strength Index
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs.iloc[-1]))
            
            # 3. PCR (Put Call Ratio) - ഏകദേശ കണക്ക്
            # (യഥാർത്ഥ PCR-ന് NSE ഓപ്ഷൻ ചെയിൻ ഡാറ്റ വേണം, ഇവിടെ നമ്മൾ ട്രെൻഡ് സിഗ്നൽ നൽകുന്നു)
            pcr_status = "Neutral"
            if rsi > 70: pcr_status = "Overbought"
            elif rsi < 30: pcr_status = "Oversold"

            if name == "Crude Fut":
                mcx = last_price * 83.5 * 1.15
                output += f"🛢️ *{name}*: ₹{mcx:,.0f}\n"
            else:
                output += f"📈 *{name}*: {last_price:,.2f}\n"
            
            output += f"RSI: {rsi:.1f} | {ma_signal}\n"
            output += f"Status: {pcr_status}\n"
            output += "------------------\n"
            
        return output + "\nAnalyze before entry, Faisal! 🚀"
    except:
        return "⚠️ ഡാറ്റ ലഭ്യമല്ല. ഒന്ന് കൂടി ശ്രമിക്കൂ."

# Handlers
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    resp = MessagingResponse()
    resp.message(get_market_analysis())
    return str(resp)

@bot.message_handler(func=lambda message: True)
def telegram_reply(message):
    bot.reply_to(message, get_market_analysis())

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
