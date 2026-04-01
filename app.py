import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. Page Settings (Sidebar എപ്പോഴും തുറന്നിരിക്കാൻ 'expanded' നൽകി)
st.set_page_config(
    page_title="FTB PRO 🚀", 
    layout="wide", 
    initial_sidebar_state="expanded" 
)

# Dark Theme CSS
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    [data-testid="stSidebar"] { background-color: #171b26; border-right: 1px solid #2a2e39; min-width: 250px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("FTB PRO 🚀")
st.sidebar.write("Go to")

# സൈഡ്‌ബാറിലെ പേജുകൾ
page = st.sidebar.radio("", ["🏠 Home", "📊 Watchlist", "📈 Chart", "👤 Profile"])

# --- PAGE LOGIC ---

if page == "🏠 Home":
    st.title("🏠 Market Overview")
    st.write("ഇവിടെ നിനക്ക് പ്രധാന മാർക്കറ്റ് അപ്‌ഡേറ്റുകൾ കാണാം.")
    # Nifty & Bank Nifty Metrics
    c1, c2 = st.columns(2)
    nifty = yf.Ticker("^NSEI").history(period="1d")['Close'].iloc[-1]
    banknifty = yf.Ticker("^NSEBANK").history(period="1d")['Close'].iloc[-1]
    c1.metric("NIFTY 50", f"₹ {nifty:,.2f}")
    c2.metric("BANK NIFTY", f"₹ {banknifty:,.2f}")

elif page == "📊 Watchlist":
    st.title("📑 My Watchlist")
    stocks = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE OIL": "CL=F", "RELIANCE": "RELIANCE.NS"}
    for name, sym in stocks.items():
        price = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
        st.info(f"**{name}**: ₹ {price:,.2f}")

elif page == "📈 Chart":
    st.title("📈 Live Chart & Signals")
    selected = st.selectbox("Select Asset", ["^NSEI", "^NSEBANK", "CL=F"])
    df = yf.download(selected, period="2d", interval="5m", multi_level_index=False)
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template='plotly_dark', height=500, paper_bgcolor='#131722', plot_bgcolor='#131722')
        st.plotly_chart(fig, use_container_width=True)

elif page == "👤 Profile":
    st.title("👤 Profile")
    st.write("**Name:** Faisal")
    st.write("**Status:** Active Trader 🦾")
