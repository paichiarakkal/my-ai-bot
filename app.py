import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd

# 1. Page Settings (Dark Theme)
st.set_page_config(page_title="FTB PRO 🚀", layout="wide")

# CSS: സൈഡ്‌ബാറും ബട്ടണുകളും മനോഹരമാക്കാൻ
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    /* സൈഡ്‌ബാർ ഡാർക്ക് ലുക്ക് */
    [data-testid="stSidebar"] { background-color: #171b26; border-right: 1px solid #2a2e39; }
    /* ബട്ടൺ ഡിസൈൻ */
    .stButton>button { width: 100%; border-radius: 8px; background-color: #1e222d; color: white; border: 1px solid #363c4e; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION (43639.jpg ലുക്ക്) ---
st.sidebar.title("FTB PRO 🚀")
st.sidebar.write("Go to")

# സൈഡ്‌ബാറിൽ പേജുകൾ തിരഞ്ഞെടുക്കാൻ (നീ ചോദിച്ച അതേ മെനു)
page = st.sidebar.radio("", ["🏠 Home", "📊 Watchlist", "📈 Chart", "👤 Profile"])

# --- DATA FUNCTION ---
def get_stock_data(symbol):
    df = yf.download(symbol, period="2d", interval="5m", multi_level_index=False)
    # സിഗ്നൽ കാൽക്കുലേഷൻ (MA 20)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    return df

# --- PAGE 1: HOME ---
if page == "🏠 Home":
    st.title("🏠 Market Overview")
    st.markdown("ഇവിടെ നിനക്ക് പ്രധാന മാർക്കറ്റ് അപ്‌ഡേറ്റുകൾ കാണാം.")
    col1, col2 = st.columns(2)
    # പ്രധാന ഇൻഡക്സുകൾ
    indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
    for name, sym in indices.items():
        val = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
        st.metric(name, f"₹ {val:,.2f}")

# --- PAGE 2: WATCHLIST (43649.jpg ലുക്ക്) ---
elif page == "📊 Watchlist":
    st.title("📑 My Watchlist")
    stocks = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE OIL": "CL=F", "RELIANCE": "RELIANCE.NS"}
    
    for name, sym in stocks.items():
        price = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
        st.info(f"**{name}**: ₹ {price:,.2f}")

# --- PAGE 3: CHART (വിശദമായ ചാർട്ടും ഇൻഡിക്കേറ്ററും) ---
elif page == "📈 Chart":
    st.title("📈 Advanced Charting")
    selected = st.selectbox("Select Asset", ["^NSEI", "^NSEBANK", "CL=F", "RELIANCE.NS"])
    
    df = get_stock_data(selected)
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price")])
        # Indicator ചേർക്കുന്നു
        fig.add_trace(go.Scatter(x=df.index, y=df['MA20'], name="MA 20", line=dict(color='yellow', width=1)))
        
        # Buy/Sell സിഗ്നൽ കാണിക്കാൻ
        last_price = df['Close'].iloc[-1]
        last_ma = df['MA20'].iloc[-1]
        signal = "BUY" if last_price > last_ma else "SELL"
        
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=500, plot_bgcolor='#131722', paper_bgcolor='#131722')
        st.plotly_chart(fig, use_container_width=True)
        
        st.success(f"Current Signal for {selected}: **{signal}**")

# --- PAGE 4: PROFILE ---
elif page == "👤 Profile":
    st.title("👤 Trader Profile")
    st.write("**Name:** Faisal")
    st.write("**Status:** Pro Trader 🦾")
    st.write("**Location:** Al Barsha, Dubai")
    st.divider()
    st.button("Edit Profile")
