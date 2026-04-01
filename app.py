import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
import pandas_ta as ta

# 1. ആപ്പ് കോൺഫിഗറേഷൻ
st.set_page_config(page_title="Upstox Pro Terminal", layout="wide")

# --- സെഷൻ സ്റ്റേറ്റ് (Demo Trading & Navigation) ---
if 'balance' not in st.session_state: st.session_state.balance = 100000.0  # 1 ലക്ഷം ഡെമോ മണി
if 'positions' not in st.session_state: st.session_state.positions = []
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'symbol' not in st.session_state: st.session_state.symbol = "CRUDEOIL24APR1000.BE" # Crude Oil Default

# --- സൂപ്പർട്രെൻഡ് കാൽക്കുലേഷൻ ---
def add_indicators(df):
    # Supertrend (7, 3) - അപ്സ്റ്റോക്സിലെ സ്റ്റാൻഡേർഡ് സെറ്റിംഗ്സ്
    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
    df = pd.concat([df, sti], axis=1)
    return df

# --- ഡാറ്റ ഫെച്ചിംഗ് ---
def get_data(ticker):
    try:
        data = yf.download(ticker, period="2d", interval="5m")
        return data if not data.empty else None
    except: return None

# --- UI STYLING ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .price-card { background: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #5a2d82; }
    .buy-btn { background-color: #089981 !important; color: white !important; }
    .sell-btn { background-color: #f23645 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- പേജ് ലോജിക് ---

# 1. HOME & CHART PAGE
if st.session_state.page == "Home":
    st.title("📈 Upstox Live Terminal")
    st.write(f"💰 **Demo Balance: ₹{st.session_state.balance:,.2f}**")
    
    symbol = st.text_input("Enter Symbol (eg: RELIANCE.NS, CL=F)", st.session_state.symbol)
    df = get_data(symbol)

    if df is not None:
        df = add_indicators(df)
        last_price = df['Close'].iloc[-1]
        
        # ചാർട്ട് നിർമ്മാണം
        fig = go.Figure()
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
        
        # Supertrend ലൈൻ ചേർക്കുന്നു
        fig.add_trace(go.Scatter(x=df.index, y=df['SUPERT_7_3.0'], line=dict(color='orange', width=2), name="Supertrend"))
        
        fig.update_layout(template="plotly_white", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # --- DEMO TRADING BUTTONS ---
        col1, col2, col3 = st.columns([1,1,2])
        qty = col1.number_input("Quantity", min_value=1, value=1)
        
        if col2.button("🟢 BUY", use_container_width=True):
            cost = last_price * qty
            if st.session_state.balance >= cost:
                st.session_state.balance -= cost
                st.session_state.positions.append({'sym': symbol, 'qty': qty, 'price': last_price, 'type': 'BUY'})
                st.success(f"Bought {qty} shares of {symbol}")
            else: st.error("Insufficient Funds!")

        if col3.button("🔴 SELL", use_container_width=True):
            # സിമ്പിൾ സെൽ ലോജിക് (Shorting or exiting)
            st.session_state.balance += (last_price * qty)
            st.session_state.positions.append({'sym': symbol, 'qty': qty, 'price': last_price, 'type': 'SELL'})
            st.warning(f"Sold {qty} shares of {symbol}")

# 2. PORTFOLIO & ORDERS
elif st.session_state.page == "Portfolio":
    st.title("💰 Portfolio & Positions")
    if not st.session_state.positions:
        st.info("No active positions.")
    else:
        st.table(pd.DataFrame(st.session_state.positions))
    
    if st.button("Reset Demo Account"):
        st.session_state.balance = 100000.0
        st.session_state.positions = []
        st.rerun()

# --- BOTTOM NAVIGATION ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
n1, n2, n3 = st.columns(3)
if n1.button("🏠 Home"): st.session_state.page = "Home"; st.rerun()
if n2.button("💰 Portfolio"): st.session_state.page = "Portfolio"; st.rerun()
if n3.button("👤 Account"): st.write(f"User: Faisal | Al Barsha, Dubai")
