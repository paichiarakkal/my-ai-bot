import telebot
import os
from flask import Flask, request
import yfinance as yf
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

def get_market_analysis():
    try:
        # India VIX
        vix = yf.Ticker("^INDIAVIX").history(period="1d")['Close'].iloc[-1]
        
        symbols = {
            "Nifty 50": "^NSEI",
            "Bank Nifty": "^NSEBANK",
            "Fin Nifty": "NIFTY_FIN_SERVICE.NS",
            "Crude Fut": "CL=F"
        }
        
        output = f"📊 *TRADE ASSISTANT LIVE*\n⚠️ VIX: {vix:.2f}\n\n"
        
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            
            last_price = df['Close'].iloc[-1]
            ema_20 = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            
            # RSI Calculation
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            
            # --- BUY/SELL LOGIC ---
            signal = "⚖️ WAIT"
            if last_price > ema_20 and rsi > 50:
                signal = "🚀 BUY CALL"
            elif last_price < ema_20 and rsi < 50:
                signal = "📉 BUY PUT"
            
            if name == "Crude Fut":
                mcx = last_price * 83.5 * 1.15
                output += f"🛢️ *{name}*: ₹{mcx:,.0f}\n"
            else:
                output += f"📈 *{name}*: {last_price:,.2f}\n"
            
            output += f"RSI: {rsi:.1f} | EMA: {'Above' if last_price > ema_20 else 'Below'}\n"
            output += f"💡 SIGNAL: *{signal}*\n"
            output += "------------------\n"
            
        return output + "\nReady to Trade, Faisal! 🚀"
    except:
        return "⚠️ ഡാറ്റ ലഭ്യമല്ല. ഒന്ന് കൂടി ശ്രമിക്കൂ."

# Handlers (WhatsApp & Telegram)
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
