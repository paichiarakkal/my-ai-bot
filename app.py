import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import time
import os

# --- Page Config ---
st.set_page_config(page_title="Faisal's Dubai Pro Terminal", layout="wide")

# --- 1. Data Management ---
DATA_FILE = 'faisal_pro_log.csv'
if 'balance' not in st.session_state:
    st.session_state.balance = 471435.50  # നിന്റെ പുതിയ ബാലൻസ് ഇവിടെ അപ്ഡേറ്റ് ചെയ്തു
if 'auto_mode' not in st.session_state:
    st.session_state.auto_mode = False

def log_trade(sym, price, qty, t_type, reason):
    df = pd.DataFrame([{'Time': pd.Timestamp.now().strftime('%H:%M:%S'), 'Asset': sym, 'Price': price, 
                        'Qty': qty, 'Type': t_type, 'Reason': reason, 'Bal': round(st.session_state.balance, 2)}])
    df.to_csv(DATA_FILE, mode='a', header=not os.path.exists(DATA_FILE), index=False)

# --- 2. Live Exchange Rates ---
def get_exchange_rates():
    try:
        # USD to INR & USD to AED for gold conversion
        inr_data = yf.download("INR=X", period="1d", progress=False)
        aed_data = yf.download("AED=X", period="1d", progress=False)
        return float(inr_data['Close'].iloc[-1]), float(aed_data['Close'].iloc[-1])
    except:
        return 83.30, 3.67

# --- 3. AI Assistant Advice Logic ---
def get_ai_advice(df, asset_name):
    close = df['Close']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = float((100 - (100 / (1 + rs))).iloc[-1])
    ema = float(close.ewm(span=20, adjust=False).mean().iloc[-1])
    price = float(close.iloc[-1])

    if rsi < 35:
        return "🔵 AI BUY: മാർക്കറ്റ് താഴെയാണ്. വാങ്ങാൻ അനുയോജ്യമായ സമയം.", "#00ccff"
    elif rsi > 65:
        return "🔴 AI SELL: വില അമിതമായി ഉയർന്നു. വിൽക്കുന്നത് ലാഭകരമാകും.", "#ff4b4b"
    elif price > ema:
        return f"🟢 TREND: {asset_name} മുകളിലോട്ട് പോകുന്നു (Uptrend).", "#28a745"
    return "⚖️ WAIT: മാർക്കറ്റ് സ്ഥിരത കൈവരിക്കാൻ കാത്തിരിക്കുക.", "#ffa500"

# --- 4. Sidebar & Controls ---
st.sidebar.title("🤖 Faisal's AI Bot")
st.session_state.auto_mode = st.sidebar.toggle("Activate Auto-Trading", value=st.session_state.auto_mode)
asset_choice = st.sidebar.selectbox("Select Asset", ["Gold (Dubai/AED)", "Nifty 50", "Crude Oil"])

inr_rate, aed_rate = get_exchange_rates()

# Currency Converter Section
st.sidebar.divider()
st.sidebar.subheader("💱 Exchange Calculator")
conv_type = st.sidebar.selectbox("Select Pair", ["INR to AED", "AED to INR", "USD to INR", "USD to AED"])
amt_input = st.sidebar.number_input("Amount", value=1.0)

ticker_map = {"INR to AED": "INRAED=X", "AED to INR": "AEDINR=X", "USD to INR": "INR=X", "USD to AED": "AED=X"}
try:
    c_data = yf.download(ticker_map[conv_type], period="1d", progress=False)
    if not c_data.empty:
        rate = float(c_data['Close'].iloc[-1])
        st.sidebar.success(f"Rate: {rate:.4f}")
        st.sidebar.write(f"Total: **{amt_input * rate:,.2f}**")
except: pass

# --- 5. Main App Logic ---
placeholder = st.empty()
asset_map = {"Gold (Dubai/AED)": "GC=F", "Nifty 50": "^NSEI", "Crude Oil": "CL=F"}
ticker = asset_map[asset_choice]

if st.session_state.auto_mode:
    try:
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            advice, color = get_ai_advice(df, asset_choice)
            last_p = float(df['Close'].iloc[-1])
            
            with placeholder.container():
                st.metric("Live Wallet Balance", f"₹{st.session_state.balance:,.2f}")
                
                # AI Assistant Box
                st.markdown(f'<div style="background:#1e1e1e;padding:15px;border-left:8px solid {color};border-radius:10px;">'
                            f'<h4 style="color:{color};margin:0;">🤖 AI Assistant</h4><p style="margin:0;">{advice}</p></div>', unsafe_allow_html=True)
                
                # Gold Details (AED & 8 Gram)
                if "Gold" in asset_choice:
                    gram_aed = (last_p / 31.1035) * aed_rate # 1 Ounce = 31.1035 Grams
                    pavan_aed = gram_aed * 8
                    st.write("---")
                    c1, c2 = st.columns(2)
                    c1.metric("1 Gram (AED)", f"{gram_aed:.2f}")
                    c2.metric("8 Gram / 1 Pavan (AED)", f"{pavan_aed:.2f}")
                
                # Chart
                fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
                fig.update_layout(template="plotly_dark", height=400, title=f"{asset_choice} Live")
                st.plotly_chart(fig, use_container_width=True)

            time.sleep(30)
            st.rerun()
    except Exception as e: st.error(f"Syncing Data... {e}")
else:
    st.info("🤖 ബോട്ട് ഇപ്പോൾ ഓഫ് ആണ്. സൈഡ്‌ബാർ ഉപയോഗിച്ച് ഓൺ ചെയ്യുക.")
    if os.path.exists(DATA_FILE):
        st.write("### 📜 Recent Trades")
        st.table(pd.read_csv(DATA_FILE).tail(5))
