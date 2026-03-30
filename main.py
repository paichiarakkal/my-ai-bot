import telebot
import os
from flask import Flask, request
import yfinance as yf
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

# 1. Stop Loss & Target Calculator
def calculate_sl_target(text):
    try:
        entry = float(text.split()[1])
        return f"🎯 *TRADE PLAN*\nEntry: ₹{entry}\n🛑 SL: ₹{entry-20}\n✅ Target: ₹{entry+40}"
    except: return "⚠️ Format: `sl [Price]`"

# 2. Lot Cost Calculator
def calculate_lot_cost(text):
    try:
        premium = float(text.split()[1])
        return f"💰 *BANK NIFTY COST*\nTotal: ₹{premium * 15:,.2f}"
    except: return "⚠️ Format: `lot [Premium]`"

# 3. Market Analysis Engine
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
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            
            last_price = df['Close'].iloc[-1]
            high, low, close = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            
            # Pivot & RSI Logic
            pivot = (high + low + close) / 3
            r1, s1 = (2 * pivot) - low, (2 * pivot) - high
            ema_20 = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            
            # Signal
            if last_price > ema_20 and rsi > 50: signal = "🚀 BUY CALL"
            elif last_price < ema_20 and rsi < 50: signal = "📉 BUY PUT"
            else: signal = "⚖️ WAIT"
            
            # Price Formatting
            if name == "Crude Fut":
                final_price = last_price * 83.5 * 1.15 # പഴയ റേഞ്ചിലേക്ക് മാറ്റാൻ
                output += f"🛢️ *{name}*: ₹{final_price:,.0f}\n"
            else:
                output += f"📈 *{name}*: {last_price:,.2f}\n"
            
            output += f"💡 *{signal}* | S1:{s1:.0f} R1:{r1:.0f}\n"
            output += "------------------\n"
            
        return output + "\nCommands: `lot`, `calc`, `sl`"
    except: return "⚠️ ഡാറ്റ ലഭ്യമല്ല."

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    body = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    if body.startswith('sl'): resp.message(calculate_sl_target(body))
    elif body.startswith('lot'): resp.message(calculate_lot_cost(body))
    elif body.startswith('calc'):
        p = body.split()
        resp.message(f"P&L: ₹{(float(p[2])-float(p[1]))*int(p[3]):.2f}")
    else: resp.message(get_market_analysis())
    return str(resp)

@bot.message_handler(func=lambda message: True)
def telegram_reply(message):
    t = message.text.lower()
    if t.startswith('sl'): bot.reply_to(message, calculate_sl_target(t))
    elif t.startswith('lot'): bot.reply_to(message, calculate_lot_cost(t))
    else: bot.reply_to(message, get_market_analysis())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
