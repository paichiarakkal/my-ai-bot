import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ആപ്പ് കോൺഫിഗറേഷൻ
st.set_page_config(page_title="Upstox Pro", layout="wide")

# --- സെഷൻ സ്റ്റേറ്റ് ---
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'positions' not in st.session_state: st.session_state.positions = []
if 'page' not in st.session_state: st.session_state.page = "Home"

# --- സൂപ്പർട്രെൻഡ് കണക്കാക്കൽ (Error Fixed Version) ---
def get_supertrend(df, period=7, multiplier=3):
    df = df.copy()
    # ഇൻഡക്സ് ടൈംസീരീസ് ആണെന്ന് ഉറപ്പുവരുത്തുന്നു
    df.index = pd.to_datetime(df.index)
    
    # ATR കണക്കാക്കുന്നു
    hl = df['High'] - df['Low']
    hc = np.abs(df['High'] - df['Close'].shift())
    lc = np.abs(df['Low'] - df['Close'].shift())
    tr = pd.concat([hl, hc, lc], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()

    hl2 = (df['High'] + df['Low']) / 2
    upper = hl2 + (multiplier * atr)
    lower = hl2 - (multiplier * atr)
    
    st_line = np.zeros(len(df))
    trend = np.ones(len(df)) # 1 for Buy, 0 for Sell
    
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upper.iloc[i-1]:
            trend[i] = 1
        elif df['Close'].iloc[i] < lower.iloc[i-1]:
            trend[i] = 0
        else:
            trend[i] = trend[i-1]
            
        st_line[i] = lower.iloc[i] if trend[i] == 1 else upper.iloc[i]
            
    df['st_line'] = st_line
    return df

# --- UI ഡിസൈൻ ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .nav-button { border-radius: 10px; padding: 10px; border: 1px solid #ddd; text-align: center; cursor: pointer; }
    </style>
    """, unsafe_allow_html=True)

# --- പേജ് നാവിഗേഷൻ ---
if st.session_state.page == "Home":
    st.markdown("### 📈 Live Terminal")
    sym = st.text_input("Enter Symbol", "RELIANCE.NS")
    
    try:
        data = yf.download(sym, period="2d", interval="5m")
        if not data.empty:
            data = get_supertrend(data)
            curr_price = data['Close'].iloc[-1]
            
            # പ്രൈസ് ഡിസ്‌പ്ലേ
            st.subheader(f"{sym} : ₹{curr_price:,.2f}")
            
            # ചാർട്ട്
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=data.index, open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'], name="Price"))
            fig.add_trace(go.Scatter(x=data.index, y=data['st_line'], line=dict(color='orange', width=2), name="Supertrend"))
            fig.update_layout(height=500, template="plotly_white", xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # ഡെമോ ട്രേഡിംഗ് പാനൽ
            st.divider()
            col1, col2, col3 = st.columns([1,1,1])
            q = col1.number_input("Qty", min_value=1, value=1)
            
            if col2.button("🟢 BUY", use_container_width=True):
                if st.session_state.balance >= (curr_price * q):
                    st.session_state.balance -= (curr_price * q)
                    st.session_state.positions.append({'Sym': sym, 'Qty': q, 'Price': curr_price, 'Type': 'BUY'})
                    st.success("Buy Order Success!")
                else: st.error("No Money!")

            if col3.button("🔴 SELL", use_container_width=True):
                st.session_state.balance += (curr_price * q)
                st.session_state.positions.append({'Sym': sym, 'Qty': q, 'Price': curr_price, 'Type': 'SELL'})
                st.warning("Sell Order Success!")

    except Exception as e:
        st.error(f"Data Error: {e}")

elif st.session_state.page == "Portfolio":
    st.title("📑 My Trades")
    st.metric("Demo Balance", f"₹{st.session_state.balance:,.2f}")
    if st.session_state.positions:
        st.table(pd.DataFrame(st.session_state.positions))
    else:
        st.info("No active trades found.")

# --- Bottom Bar ---
st.markdown("<br><br>", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3)
if b1.button("🏠 Home"): st.session_state.page = "Home"; st.rerun()
if b2.button("💰 Portfolio"): st.session_state.page = "Portfolio"; st.rerun()
if b3.button("👤 Profile"): st.write("Faisal | Al Barsha")
