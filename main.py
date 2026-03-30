import telebot
import os
import yfinance as yf
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

# 1. Market News Fetcher
def get_latest_news():
    try:
        # Nifty വാർത്തകൾ ലഭിക്കാൻ
        ticker = yf.Ticker("^NSEI")
        news = ticker.news
        if news:
            title = news[0]['title']
            return f"📰 *LATEST NEWS:*\n{title}"
        return "📰 *NEWS:* No major updates right now."
    except:
        return "📰 *NEWS:* Stay tuned for updates!"

# 2. Market Analysis (Old features + News)
def get_market_analysis():
    try:
        symbols = {
            "Nifty 50": "^NSEI", "Bank Nifty": "^NSEBANK", 
            "Crude Fut": "CL=F", "HDFC Bank": "HDFCBANK.NS", "Reliance": "RELIANCE.NS"
        }
        output = "🚀 *FAISAL'S PRO TERMINAL*\n\n"
        
        for name, sym in symbols.items():
            df = yf.Ticker(sym).history(period="2d", interval="5m")
            if df.empty: continue
            last_price = df['Close'].iloc[-1]
            high, low, close = df['High'].iloc[-2], df['Low'].iloc[-2], df['Close'].iloc[-2]
            pivot = (high + low + close) / 3
            r1, s1 = (2 * pivot) - low, (2 * pivot) - high
            signal = "🚀 BUY CALL" if last_price > pivot else "📉 BUY PUT"
            
            if name == "Crude Fut":
                price = last_price * 83.5 * 1.15
                output += f"🛢️ *{name}*: ₹{price:,.0f}\n"
            else:
                output += f"📈 *{name}*: {last_price:,.2f}\n"
            output += f"💡 *{signal}* | S1:{s1:.0f} R1:{r1:.0f}\n---\n"
            
        # വാർത്തകൾ അവസാനം ചേർക്കുന്നു
        return output + get_latest_news() + "\n\nCommands: `lot`, `calc`, `sl`"
    except:
        return "⚠️ ഡാറ്റ ലഭ്യമല്ല."

# WhatsApp & Telegram Handlers
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    body = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    # P&L, Lot, SL logic remains same
    if body.startswith('sl'):
        val = float(body.split()[1])
        resp.message(f"🎯 Entry: ₹{val}\n🛑 SL: ₹{val-20}\n✅ Target: ₹{val+40}")
    elif body.startswith('lot'):
        val = float(body.split()[1])
        resp.message(f"💰 Cost: ₹{val*15:,.2f}")
    else:
        resp.message(get_market_analysis())
    return str(resp)

@bot.message_handler(func=lambda message: True)
def telegram_reply(message):
    bot.reply_to(message, get_market_analysis())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
