import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. Page Settings
st.set_page_config(page_title="FTB PRO TERMINAL", layout="wide")

# Dark Theme CSS
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1e222d; color: white; border: 1px solid #363c4e; }
    .stButton>button:hover { background-color: #2962ff; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION LOGIC ---
# ഏത് പേജിലാണെന്ന് ഓർത്തു വെക്കാൻ (Session State)
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

# താഴെയുള്ള ബട്ടണുകളുടെ ഫങ്ക്ഷൻ
def set_page(page_name):
    st.session_state.page = page_name

# --- SIDEBAR (WATCHLIST) ---
st.sidebar.title("🚀 FTB PRO")
watchlist = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "CRUDE OIL": "CL=F",
    "RELIANCE": "RELIANCE.NS"
}
selected_stock = st.sidebar.selectbox("Quick Watchlist", list(watchlist.keys()))

# --- MAIN CONTENT AREA ---

# 1. HOME PAGE (Watchlist & Live Prices)
if st.session_state.page == 'Home':
    st.subheader("🏠 Home - Market Overview")
    for name, sym in watchlist.items():
        data = yf.Ticker(sym).history(period="1d")
        price = data['Close'].iloc[-1]
        st.info(f"**{name}**: ₹ {price:,.2f}")

# 2. EXPLORE PAGE (Full Chart)
elif st.session_state.page == 'Explore':
    st.subheader(f"📈 Explore - {selected_stock} Chart")
    try:
        df = yf.download(watchlist[selected_stock], period="2d", interval="5m", multi_level_index=False)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template='plotly_dark', xaxis_rangeslider_visible=False, height=500, paper_bgcolor='#131722', plot_bgcolor='#131722')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(f"<h2 style='text-align: center;'>₹ {df['Close'].iloc[-1]:,.2f}</h2>", unsafe_allow_html=True)
    except:
        st.error("Data load ചെയ്യാൻ കഴിഞ്ഞില്ല.")

# 3. PROFILE PAGE
elif st.session_state.page == 'Profile':
    st.subheader("👤 My Profile")
    st.write("**Name:** Faisal")
    st.write("**Account:** Pro Trader")
    st.success("Your trading bot is active! 🦾")

# --- BOTTOM NAVIGATION BAR ---
st.divider()
col1, col2, col3 = st.columns(3)

# ഓരോ ബട്ടണിലും ക്ലിക്ക് ചെയ്യുമ്പോൾ പേജ് മാറും
if col1.button("🏠 Home"):
    set_page('Home')
    st.rerun()

if col2.button("📈 Explore"):
    set_page('Explore')
    st.rerun()

if col3.button("👤 Profile"):
    set_page('Profile')
    st.rerun()
