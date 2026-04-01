import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# ആപ്പ് കോൺഫിഗറേഷൻ
st.set_page_config(page_title="Upstox Pro", layout="wide")

# --- സെഷൻ സ്റ്റേറ്റ് (ഡാറ്റ സൂക്ഷിക്കാൻ) ---
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'positions' not in st.session_state: st.session_state.positions = []
if 'page' not in st.session_state: st.session_state.page = "Home"

# --- സൂപ്പർട്രെൻഡ് കാൽക്കുലേഷൻ (Error-Free Version) ---
def calculate_supertrend(df, period=7, multiplier=3):
    df = df.copy()
    # ഇൻഡക്സ് റീസെറ്റ് ചെയ്ത് എറർ ഒഴിവാക്കുന്നു
    df = df.reset_index()
    
    # ATR കണക്കാക്കുന്നു
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(period).mean()

    hl2 = (df['High'] + df['Low']) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    
    # സൂപ്പർട്രെൻഡ് ലോജിക്
    supertrend = [True] * len(df)
    final_bands = [0.0] * len(df)
    
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upperband.iloc[i-1]:
            supertrend[i] = True
        elif df['Close'].iloc[i] < lowerband.iloc[i-1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i-1]
            
        final_bands[i] = lowerband.iloc[i] if supertrend[i] else upperband.iloc[i]
            
    df['st_line'] = final_bands
    return df.set_index('Date')

# --- പേജ് നാവിഗേഷൻ ---
if st.session_state.page == "Home":
    st.markdown("### 📈 Live Terminal")
    symbol = st.text_input("Enter Symbol (eg: RELIANCE.NS, CL=F)", "RELIANCE.NS")
    
    try:
        # ഡാറ്റ ഫെച്ചിംഗ്
        df = yf.download(symbol, period="5d", interval="5m")
        if not df.empty:
            df = calculate_supertrend(df)
            last_price = df['Close'].iloc[-1]
            
            st.subheader(f"Current Price: ₹{last_price:,.2f}")
            
            # ചാർട്ട് നിർമ്മാണം
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
            fig.add_trace(go.Scatter(x=df.index, y=df['st_line'], line=dict(color='orange', width=2), name="Supertrend"))
            
            fig.update_layout(template="plotly_white", height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # ഡെമോ ട്രേഡിംഗ് പാനൽ
            st.divider()
            c1, c2, c3 = st.columns([1,1,1])
            qty = c1.number_input("Quantity", min_value=1, value=1)
            
            if c2.button("🟢 BUY", use_container_width=True):
                if st.session_state.balance >= (last_price * qty):
                    st.session_state.balance -= (last_price * qty)
                    st.session_state.positions.append({'Sym': symbol, 'Qty': qty, 'Price': last_price, 'Type': 'BUY'})
                    st.success(f"Bought {qty} shares of {symbol}")
                else: st.error("Insufficient Funds!")

            if c3.button("🔴 SELL", use_container_width=True):
                st.session_state.balance += (last_price * qty)
                st.session_state.positions.append({'Sym': symbol, 'Qty': qty, 'Price': last_price, 'Type': 'SELL'})
                st.warning(f"Sold {qty} shares of {symbol}")

    except Exception as e:
        st.error(f"Error: {e}")

elif st.session_state.page == "Portfolio":
    st.title("💰 Portfolio & Trades")
    st.metric("Virtual Balance", f"₹{st.session_state.balance:,.2f}")
    if st.session_state.positions:
        st.table(pd.DataFrame(st.session_state.positions))
    else:
        st.info("No active trades.")

# --- BOTTOM NAV BAR ---
st.markdown("<br><br>", unsafe_allow_html=True)
n1, n2, n3 = st.columns(3)
if n1.button("🏠 Home"): st.session_state.page = "Home"; st.rerun()
if n2.button("📑 Portfolio"): st.session_state.page = "Portfolio"; st.rerun()
if n3.button("👤 Profile"): st.write("User: Faisal")
