import time
import urllib.parse
import pandas as pd
import pandas_ta as ta
import requests
import yfinance as yf


def send_algo_alert(message_text):
    """CallMeBot വഴി വാട്സ്ആപ്പിലേക്ക് മെസ്സേജ് അയക്കുന്നു"""
    phone = "971551347989"
    apikey = "7463030"

    encoded_message = urllib.parse.quote(message_text)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded_message}&apikey={apikey}"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("📲 സിഗ്നൽ വാട്സ്ആപ്പിലേക്ക് അയച്ചു, ബോട്ട്!")
        else:
            print(f"❌ WhatsApp Error: {response.text}")
    except Exception as e:
        print(f"❌ നെറ്റ്വർക്ക് പ്രശ്നം: {e}")


def run_trading_bot():
    # 1. ടാറ്റാ മോട്ടോഴ്‌സിന്റെ ഡാറ്റ എടുക്കുന്നു (നിഫ്റ്റിക്ക് ആണെങ്കിൽ '^NSEI' എന്ന് നൽകാം)
    ticker = "TATAMOTORS.NS"

    print(f"🔄 {ticker} മാർക്കറ്റ് ഡാറ്റ പരിശോധിക്കുന്നു...")

    # Yahoo Finance-ൽ നിന്ന് കഴിഞ്ഞ 5 ദിവസത്തെ 5 മിനിറ്റ് ക്യാൻഡിൽ ഡാറ്റ എടുക്കുന്നു
    df = yf.download(tickers=ticker, period="5d", interval="5m", progress=False)

    if df.empty:
        print("❌ ഡാറ്റ എടുക്കാൻ പറ്റിയില്ല. മാർക്കറ്റ് ടൈം ആണോ എന്ന് പരിശോധിക്കുക.")
        return

    # 2. ഇൻഡിക്കേറ്ററുകൾ കണക്കാക്കുന്നു (Supertrend & RSI)
    sti = ta.supertrend(df["High"], df["Low"], df["Close"], length=7, multiplier=3)
    df["ST_Direction"] = sti["SUPERTd_7_3.0"]
    df["RSI"] = ta.rsi(df["Close"], length=14)

    # 3. ഏറ്റവും പുതിയ ലൈവ് ക്യാൻഡിൽ ഡാറ്റ എടുക്കുന്നു
    last_row = df.iloc[-1]
    current_close = float(last_row["Close"])
    current_rsi = float(last_row["RSI"])
    current_trend = int(last_row["ST_Direction"])

    print(
        f"📊 Current Close: {round(current_close, 2)} | RSI: {round(current_rsi, 2)} | Trend: {'GREEN' if current_trend == 1 else 'RED'}"
    )

    # 4. അൽഗോരിതം കണ്ടീഷൻ ചെക്കിങ്
    if current_trend == 1 and current_rsi > 50:
        msg = f"🔥 ALGO ALERT: {ticker} 🔥\n\n🟢 STRONG BUY SIGNAL\n📈 Price: {round(current_close, 2)}\n📊 RSI: {round(current_rsi, 2)}"
        send_algo_alert(msg)

    elif current_trend == -1 and current_rsi < 40:
        msg = f"📉 ALGO ALERT: {ticker} 📉\n\n🔴 STRONG SELL SIGNAL\n📉 Price: {round(current_close, 2)}\n📊 RSI: {round(current_rsi, 2)}"
        send_algo_alert(msg)
    else:
        print("⌛ സ്ട്രോങ്ങ് സിഗ്നലുകൾ ഇല്ല. അടുത്ത ക്യാൻഡിലിനായി കാത്തിരിക്കുന്നു...")


# ബോട്ട് റൺ ചെയ്യുന്നു
if __name__ == "__main__":
    print("🤖 അൽഗോരിതം ബോട്ട് സ്റ്റാർട്ട് ചെയ്തു ബോട്ട്...")
    run_trading_bot()
