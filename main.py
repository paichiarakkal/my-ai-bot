import telebot
import os
from flask import Flask, request
import yfinance as yf
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)
TELEGRAM_BOT_TOKEN = "8638662433:AAEI4BwJuO7Bg8XTEv8OHmfP6CexFe2SiwA"
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, threaded=False)

def get_market_analysis():
    try:
        # പ്രധാന ഇൻഡക്സുകളും സ്റ്റോക്കുകളും
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
            df = ticker.history(period="2d", interval="5m")
            if df.empty: continue
            
            last_price = df['Close'].iloc[-1]
            high = df['High'].iloc[-2]
            low = df['Low'].iloc[-2]
            close = df['Close'].iloc[-2]
            
            # Pivot Point Calculation
            pivot = (high + low + close) / 3
            r1 = (2 * pivot) - low
            s1 = (2 * pivot) - high
            
            # Simple Signal
            signal = "🟢 BULLISH" if last_price > pivot else "🔴 BEARISH"
            
            if name == "Crude Fut":
                price = last_price * 83.5 * 1.15
                output += f"🛢️ *{name}*: ₹{price:,.0f}\n"
            else:
                output += f"📈 *{name}*: {last_price:,.2f}\n"
            
            output += f"ST: {signal} | S1: {s1:.0f} | R1: {r1:.0f}\n"
            output += "------------------\n"
            
        return output + "\n`calc [Buy] [Sell] [Qty]` for P&L"
    except:
        return "⚠️ ഡാറ്റ ലഭ്യമല്ല."

# WhatsApp & Telegram Handlers (നമ്മൾ നേരത്തെ ചെയ്തത് പോലെ)
@app.route("/whatsapp", methods=['POST'])
def whatsapp_reply():
    body = request.values.get('Body', '').lower()
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
