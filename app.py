import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="FTB PRO 🚀", layout="wide")

# CSS: ലുക്ക് നന്നാക്കാൻ
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1e222d; color: white; border: 1px solid #363c4e; height: 50px; font-size: 18px;}
    .stButton>button:hover { background-color: #2962ff; }
    [data-testid="stMetricValue"] { color: #2962ff; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION LOGIC ---
if 'page' not in st.session_state:
    st.session_state.page = 'Home'
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = '^NSEI'

# --- DATA HELPERS ---
def get_chart_data(symbol):
    df = yf.download(symbol, period="2d", interval="5m", multi_level_index=False)
    # Supertrend / Moving Average (Buy/Sell സിഗ്നലിനായി)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['Signal'] = "HOLD"
    df.loc[df['Close'] > df['MA20'], 'Signal'] = "BUY"
    df.loc[df['Close'] < df['MA20'], 'Signal'] = "SELL"
    return df

# --- 1. HOME PAGE (Watchlist) ---
if st.session_state.page == 'Home':
    st.title("🏠 Home - Market Overview")
    stocks = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE OIL": "CL=F", "RELIANCE": "RELIANCE.NS"}
    
    for name, sym in stocks.items():
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(f"📊 {name}"):
                st.session_state.selected_stock = sym
                st.session_state.page = 'Explore'
                st.rerun()
        with col2:
            data = yf.Ticker(sym).history(period="1d")
            price = data['Close'].iloc[-1]
            st.metric("", f"₹{price:,.1f}")

# --- 2. EXPLORE PAGE (The Real Chart) ---
elif st.session_state.page == 'Explore':
    st.title(f"📈 Chart: {st.session_state.selected_stock}")
    
    df = get_chart_data(st.session_state.selected_stock)
    
    if not df.empty:
        fig = go.Figure()
        # Candlestick
        fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Market"))
        
        # Indicator (MA 20)
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="Trend Line", line=dict(color='yellow', width=1.5)))
        
        # Buy/Sell Labels
        last_signal = df['Signal'].iloc[-1]
        last_price = df['Close'].iloc[-1]
        
        fig.add_annotation(x=df.index[-1], y=last_price, text=f"SIGNAL: {last_signal}", 
                           showarrow=True, arrowhead=1, bgcolor="green" if last_signal=="BUY" else "red")

        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=500, paper_bgcolor='#131722', plot_bgcolor='#131722')
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"Current Recommendation: {last_signal}")
    
    if st.button("⬅️ Back to Home"):
        st.session_state.page = 'Home'
        st.rerun()

# --- 3. PROFILE PAGE ---
elif st.session_state.page == 'Profile':
    st.title("👤 Profile")
    st.write("Name: Faisal")
    st.write("Status: Active")
    if st.button("⬅️ Back to Home"):
        st.session_state.page = 'Home'
        st.rerun()

# --- BOTTOM MENU ---
st.markdown("---")
b_col1, b_col2, b_col3 = st.columns(3)
if b_col1.button("🏠"): st.session_state.page = 'Home'; st.rerun()
if b_col2.button("📈"): st.session_state.page = 'Explore'; st.rerun()
if b_col3.button("👤"): st.session_state.page = 'Profile'; st.rerun()
