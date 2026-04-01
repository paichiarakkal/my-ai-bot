import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Upstox Pro Terminal", layout="wide")

# --- സെഷൻ സ്റ്റേറ്റ് (ഡാറ്റ സൂക്ഷിക്കാൻ) ---
if 'balance' not in st.session_state: st.session_state.balance = 100000.0
if 'positions' not in st.session_state: st.session_state.positions = []
if 'page' not in st.session_state: st.session_state.page = "Home"

# --- മാനുവൽ സൂപ്പർട്രെൻഡ് ഫങ്ക്ഷൻ (Pandas മാത്രം ഉപയോഗിച്ച്) ---
def compute_supertrend(df, period=7, multiplier=3):
    # ATR കണക്കാക്കുന്നു
    high_low = df['High'] - df['Low']
    high_close = np.abs(df['High'] - df['Close'].shift())
    low_close = np.abs(df['Low'] - df['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(period).mean()

    # Basic Bands
    hl2 = (df['High'] + df['Low']) / 2
    upperband = hl2 + (multiplier * atr)
    lowerband = hl2 - (multiplier * atr)
    
    # Supertrend ലോജിക്
    supertrend = [True] * len(df)
    final_bands = [0.0] * len(df)
    
    for i in range(1, len(df)):
        if df['Close'].iloc[i] > upperband.iloc[i-1]:
            supertrend[i] = True
        elif df['Close'].iloc[i] < lowerband.iloc[i-1]:
            supertrend[i] = False
        else:
            supertrend[i] = supertrend[i-1]
            
        if supertrend[i]:
            final_bands[i] = lowerband.iloc[i]
        else:
            final_bands[i] = upperband.iloc[i]
            
    df['Supertrend'] = final_bands
    return df

# --- പേജ് ലോജിക് ---
if st.session_state.page == "Home":
    st.markdown("### 📈 Live Market")
    symbol = st.text_input("Enter Symbol (eg: CRUDEOIL24APR1000.BE, RELIANCE.NS)", "RELIANCE.NS")
    
    # ഡാറ്റ ഫെച്ചിംഗ്
    try:
        df = yf.download(symbol, period="5d", interval="5m")
        if not df.empty:
            df = compute_supertrend(df)
            last_price = df['Close'].iloc[-1]
            
            st.metric("Current Price", f"₹{last_price:,.2f}", f"Balance: ₹{st.session_state.balance:,.2f}")

            # ചാർട്ട് നിർമ്മാണം
            fig = go.Figure()
            fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
            fig.add_trace(go.Scatter(x=df.index, y=df['Supertrend'], line=dict(color='orange', width=2), name="Supertrend"))
            
            fig.update_layout(template="plotly_white", height=500, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)

            # ഡെമോ ട്രേഡിംഗ് ബട്ടണുകൾ
            c1, c2 = st.columns(2)
            qty = st.number_input("Quantity", min_value=1, value=1)
            
            if c1.button("🟢 BUY", use_container_width=True):
                cost = last_price * qty
                if st.session_state.balance >= cost:
                    st.session_state.balance -= cost
                    st.session_state.positions.append({'Symbol': symbol, 'Qty': qty, 'Price': last_price, 'Type': 'BUY'})
                    st.success(f"Bought {qty} of {symbol}")
                else: st.error("Insufficient Balance!")

            if c2.button("🔴 SELL", use_container_width=True):
                st.session_state.balance += (last_price * qty)
                st.session_state.positions.append({'Symbol': symbol, 'Qty': qty, 'Price': last_price, 'Type': 'SELL'})
                st.warning(f"Sold {qty} of {symbol}")

    except Exception as e:
        st.error(f"Error loading data: {e}")

# --- BOTTOM NAVIGATION ---
st.divider()
n1, n2, n3 = st.columns(3)
if n1.button("🏠 Home"): st.session_state.page = "Home"; st.rerun()
if n2.button("💰 Portfolio"): 
    st.write("### Active Positions")
    if st.session_state.positions: st.table(pd.DataFrame(st.session_state.positions))
    else: st.info("No trades yet.")
if n3.button("👤 Profile"): st.write(f"User: Faisal | Account: Demo")
