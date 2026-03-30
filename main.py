import telebot
import os
from flask import Flask, request
import yfinance as yf
import pandas as pd
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

def calculate_pnl(text):
    try:
        # Format: calc 500 550 15 (Buy Sell Qty)
        parts = text.split()
        buy = float(parts[1])
        sell = float(parts[2])
        qty = int(parts[3])
        
        pnl = (sell - buy) * qty
        status = "💰 PROFIT" if pnl > 0 else "📉 LOSS"
        return f"{status}: ₹{abs(pnl):,.2f}\nPoints: {sell-buy:.2f}"
    except:
        return "⚠️ Format: `calc [Buy] [Sell] [Qty]`\nEx: `calc 450 480 15`"

def get_market_analysis():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Fin Nifty": "NIFTY_FIN_SERVICE.NS", "Crude Fut": "CL=F"}
        output = "📊 *TRADE ASSISTANT LIVE*\n\n"
        
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="2d", interval="5m")
            if df.empty: continue
            
            last_price = df['Close'].iloc[-1]
            ema_20 = df['Close'].ewm(span=20, adjust=False).mean().iloc[-1]
            
            # RSI
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss).iloc[-1]))
            
            signal = "🚀 BUY CALL" if last_price > ema_20 and rsi > 50 else "📉 BUY PUT" if last_price < ema_20 and rsi < 50 else "⚖️ WAIT"
            
            if name == "Crude Fut":
                price = last_price * 83.5 * 1.15
                output += f"🛢️ *{name}*: ₹{price:,.0f}\n"
            else:
                output += f"📈 *{name}*: {last_price:,.2f}\n"
            
            output += f"💡 SIGNAL: *{signal}*\n------------------\n"
            
        return output + "\nUse `calc 100 120 15` for P&L"
    except:
        return "⚠️ ഡാറ്റ ലഭ്യമല്ല."

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    body = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    if body.startswith('calc'):
        resp.message(calculate_pnl(body))
    else:
        resp.message(get_market_analysis())
    return str(resp)

@bot.message_handler(func=lambda message: True)
def telegram_reply(message):
    text = message.text.lower()
    if text.startswith('calc'):
        bot.reply_to(message, calculate_pnl(text))
    else:
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
