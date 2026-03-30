import telebot
import os
from flask import Flask, request
import yfinance as yf
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

# Stop Loss & Target Calculator
def calculate_sl_target(text):
    try:
        parts = text.split()
        entry = float(parts[1])
        # 1:2 Risk-Reward (20 pts SL, 40 pts Target for Option)
        sl = entry - 20
        target = entry + 40
        return f"🎯 *TRADE PLAN*\nEntry: ₹{entry}\n🛑 SL (20pts): ₹{sl}\n✅ Target (40pts): ₹{target}"
    except:
        return "⚠️ Format: `sl [Entry Price]`\nEx: `sl 350`"

# Lot Cost Calculator
def calculate_lot_cost(text):
    try:
        parts = text.split()
        premium = float(parts[1])
        return f"💰 *BANK NIFTY COST*\nTotal: ₹{premium * 15:,.2f} (15 Qty)"
    except:
        return "⚠️ Format: `lot [Premium]`"

def get_market_analysis():
    try:
        symbols = {"Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", "Crude Fut": "CL=F"}
        output = "🚀 *FAISAL'S PRO TERMINAL*\n\n"
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="5d", interval="5m")
            if df.empty: continue
            last_price = df['Close'].iloc[-1]
            high, low, close = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (high + low + close) / 3
            r1, s1 = (2 * pivot) - low, (2 * pivot) - high
            signal = "🚀 BUY CALL" if last_price > pivot else "📉 BUY PUT"
            output += f"📈 *{name}*: {last_price:,.2f}\n💡 *{signal}* | S1:{s1:.0f} R1:{r1:.0f}\n---\n"
        return output + "\nCommands: `lot`, `calc`, `sl`"
    except:
        return "⚠️ ഡാറ്റ ലഭ്യമല്ല."

@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    body = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    if body.startswith('sl'):
        resp.message(calculate_sl_target(body))
    elif body.startswith('lot'):
        resp.message(calculate_lot_cost(body))
    elif body.startswith('calc'):
        parts = body.split()
        res = f"P&L: ₹{(float(parts[2])-float(parts[1]))*int(parts[3]):.2f}"
        resp.message(res)
    else:
        resp.message(get_market_analysis())
    return str(resp)

@bot.message_handler(func=lambda message: True)
def telegram_reply(message):
    text = message.text.lower()
    if text.startswith('sl'):
        bot.reply_to(message, calculate_sl_target(text))
    elif text.startswith('lot'):
        bot.reply_to(message, calculate_lot_cost(text))
    else:
        bot.reply_to(message, get_market_analysis())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
