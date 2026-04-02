import streamlit as st
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="Paichi Trader Pro", layout="wide")

# ഓരോ 1 സെക്കൻഡിലും തനിയെ റിഫ്രഷ് ആകാൻ
st_autorefresh(interval=1000, limit=1000, key="faisal_ultimate_live")

st.sidebar.title("💎 Paichi Menu")
choice = st.sidebar.radio("സേവനം തിരഞ്ഞെടുക്കുക:", ["Indian Indices", "Commodities & Forex", "Quick Links"])

def get_live_analysis(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        result = data['chart']['result'][0]
        price = result['meta']['regularMarketPrice']
        prices = result['indicators']['quote'][0]['close']
        
        df = pd.Series(prices).dropna()
        if len(df) > 20:
            # 1. RSI (14) Calculation
            delta = df.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rsi = 100 - (100 / (1 + (gain / loss)))
            last_rsi = float(rsi.iloc[-1])
            
            # 2. Moving Average (Trend Filter like SuperTrend)
            ma_10 = df.rolling(window=10).mean().iloc[-1]
            trend = "UP 🟢" if price > ma_10 else "DOWN 🔴"
            
            # 3. Buy/Sell Signal Logic
            if last_rsi < 40 and trend == "UP 🟢":
                signal, color = "🔥 STRONG BUY", "green"
            elif last_rsi > 60 and trend == "DOWN 🔴":
                signal, color = "💥 STRONG SELL", "red"
            elif last_rsi < 35:
                signal, color = "BUY 🟢", "green"
            elif last_rsi > 65:
                signal, color = "SELL 🔴", "red"
            else:
                signal, color = "WAIT ⏳", "orange"
                
            return {"price": price, "rsi": last_rsi, "trend": trend, "signal": signal, "color": color}
    except:
        return None

def display_dashboard(data, title, mult=1):
    if data:
        p = data['price'] * mult
        with st.container():
            st.subheader(title)
            c1, c2, c3 = st.columns(3)
            c1.metric("Live Price", f"₹{p:.2f}")
            c2.metric("RSI (14)", f"{data['rsi']:.2f}")
            c3.metric("Trend", data['trend'])
            
            if data['color'] == "green": st.success(data['signal'])
            elif data['color'] == "red": st.error(data['signal'])
            else: st.warning(data['signal'])
    else:
        st.error(f"{title} ഡാറ്റ ലഭ്യമല്ല")

# --- Main Page Logic ---

if choice == "Indian Indices":
    st.title("📊 Indian Stock Market (Live)")
    display_dashboard(get_live_analysis("^NSEI"), "NIFTY 50")
    st.divider()
    display_dashboard(get_live_analysis("^NSEBANK"), "BANK NIFTY")
    st.divider()
    display_dashboard(get_live_analysis("NIFTY_FIN_SERVICE.NS"), "FIN NIFTY")

elif choice == "Commodities & Forex":
    st.title("🛢️ Commodities & Gold")
    
    # Crude Oil: Multiplier set to 93.5 to match Upstox price (₹10,300+ range)
    display_dashboard(get_live_analysis("CL=F"), "CRUDE OIL FUTURE (MCX)", mult=93.5)
    
    st.divider()
    
    # Gold 8 Gram
    g_data = get_live_analysis("GC=F")
    if g_data:
        g_price = ((g_data['price'] / 31.1) * 83.5 * 1.15) * 8
        st.metric("GOLD 8 GRAM (Approx)", f"₹{g_price:.0f}")
    
    st.divider()
    
    # AED to INR
    a_data = get_live_analysis("AEDINR=X")
    if a_data: 
        st.metric("1 DIRHAM (AED) to INR", f"₹{a_data['price']:.2f}")

else:
    st.title("🔗 Quick Access")
    st.markdown("### [🌐 Open Upstox Login](https://upstox.com/)")
    st.markdown("### [📊 TradingView Charts](https://www.tradingview.com/chart/)")
