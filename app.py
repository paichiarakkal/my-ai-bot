import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Upstox Clone", layout="wide")

# CSS: Upstox-ന്റെ കൃത്യമായ ലുക്ക് വരാൻ
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    /* Top Indices Bar */
    .idx-container { display: flex; justify-content: space-around; background: #f8f9fa; padding: 10px; border-bottom: 1px solid #eee; }
    .idx-item { text-align: center; }
    /* Bottom Navigation */
    .bottom-nav { position: fixed; bottom: 0; left: 0; width: 100%; background: white; display: flex; justify-content: space-around; padding: 10px; border-top: 1px solid #ddd; z-index: 100; }
    .symbol-row { display: flex; justify-content: space-between; padding: 12px 15px; border-bottom: 1px solid #f1f1f1; align-items: center; }
    .price-green { color: #089981; font-weight: bold; }
    .price-red { color: #f23645; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ഡാറ്റ എടുക്കാനുള്ള ഫങ്ക്ഷൻ
@st.cache_data(ttl=60)
def get_market_info(symbols):
    try:
        data = yf.download(symbols, period="1d", interval="5m", multi_level_index=False)
        return data['Close']
    except: return None

# --- TOP INDICES SECTION ---
indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
idx_cols = st.columns(2)
for i, (name, sym) in enumerate(indices.items()):
    val = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
    idx_cols[i].metric(name, f"₹{val:,.2f}")

st.divider()

# --- SEARCH & TABS ---
st.text_input("🔍 Search stocks...", placeholder="Search Eg: Reliance, TCS")
tabs = st.tabs(["Watchlist", "Stocks (50)", "F&O", "Commodity"])

# Nifty 50 സ്റ്റോക്കുകൾ
nifty50_list = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "BHARTIARTL.NS", "ITC.NS", "SBIN.NS", "LTIM.NS", "BAJFINANCE.NS",
    "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS", "TITAN.NS", "HCLTECH.NS"
]

with tabs[1]:
    prices = get_market_info(nifty50_list)
    if prices is not None:
        for stock in nifty50_list:
            p = prices[stock].iloc[-1]
            st.markdown(f"""
                <div class="symbol-row">
                    <div><b>{stock.replace('.NS', '')}</b><br><small>NSE</small></div>
                    <div class="price-green">₹ {p:,.2f}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"View {stock}", key=stock):
                st.session_state.chart_sym = stock

# --- CHART SECTION ---
if 'chart_sym' in st.session_state:
    st.subheader(f"📊 {st.session_state.chart_sym} Chart")
    c_df = yf.download(st.session_state.chart_sym, period="1d", interval="1m")
    if not c_df.empty:
        fig = go.Figure(data=[go.Candlestick(x=c_df.index, open=c_df['Open'], high=c_df['High'], low=c_df['Low'], close=c_df['Close'])])
        fig.update_layout(template="plotly_white", height=400, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# --- BOTTOM NAVIGATION ---
st.markdown("""
    <div class="bottom-nav">
        <div style="color: blue;">🏠<br><small>Home</small></div>
        <div>📑<br><small>Orders</small></div>
        <div>👤<br><small>Account</small></div>
    </div>
    """, unsafe_allow_html=True)
