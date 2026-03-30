import telebot
import os
import time
import threading
from flask import Flask, request
import yfinance as yf
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

def get_market_analysis():
    try:
        symbols = {
            "Nifty 50": "^NSEI", 
            "Bank Nifty": "^NSEBANK", 
            "Crude Fut": "CL=F",
            "HDFC Bank": "HDFCBANK.NS",
            "Reliance": "RELIANCE.NS"
        }
        
        output = "🚀 *FAISAL'S PRO TERMINAL*\n\n"
        
        for name, sym in symbols.items():
            ticker = yf.Ticker(sym)
            df = ticker.history(period="5d", interval="5m")
            if df.empty: continue
            
            last_price = df['Close'].iloc[-1]
            
            # Pivot, RSI & EMA Calculations
            high, low, close = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (high + low + close) / 3
            r1, s1 = (2 * pivot) - low, (2 * pivot) - high
            
            ema_20 = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            
            # --- CLEAR BUY/SELL SIGNAL ---
            if last_price > ema_20 and rsi > 50:
                signal = "🚀 BUY CALL"
            elif last_price < ema_20 and rsi < 50:
                signal = "📉 BUY PUT"
            else:
                signal = "⚖️ WAIT"
            
            if name == "Crude Fut":
                price = last_price * 83.5 * 1.15
                output += f"🛢️ *{name}*: ₹{price:,.0f}\n"
            else:
                output += f"📈 *{name}*: {last_price:,.2f}\n"
            
            output += f"💡 *{signal}* | S1:{s1:.0f} R1:{r1:.0f}\n"
            output += "------------------\n"
            
        return output + "\n`calc [Buy] [Sell] [Qty]` for P&L"
    except:
        return "⚠️ ഡാറ്റ ലഭ്യമല്ല."

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    body = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    if body.startswith('calc'):
        # P&L Calculation logic (നമ്മൾ നേരത്തെ ചെയ്തത്)
        parts = body.split()
        res = f"P&L: ₹{(float(parts[2])-float(parts[1]))*int(parts[3]):.2f}"
        resp.message(res)
    else:
        resp.message(get_market_analysis())
    return str(resp)

@bot.message_handler(func=lambda message: True)
def telegram_reply(message):
    bot.reply_to(message, get_market_analysis())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
