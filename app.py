import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. ആപ്പ് സെറ്റിംഗ്സ് & ലുക്ക്
st.set_page_config(page_title="Upstox Pro Terminal", layout="wide")

# CSS: ഒറിജിനൽ അപ്സ്റ്റോക്സ് സ്റ്റൈൽ (White & Purple theme)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    header { visibility: hidden; }
    /* Top Bar Indices */
    .idx-box { background: #f8f9fa; padding: 10px; border-radius: 8px; border: 1px solid #eee; text-align: center; }
    /* Stock List Styling */
    .symbol-row { display: flex; justify-content: space-between; padding: 15px; border-bottom: 1px solid #f1f1f1; align-items: center; }
    .price-green { color: #089981; font-weight: bold; }
    .price-red { color: #f23645; font-weight: bold; }
    /* Bottom Navigation Bar */
    .stButton>button { width: 100%; border: none; background: transparent; color: #666; font-size: 20px; }
    .stButton>button:hover { color: #5a2d82; }
    </style>
    """, unsafe_allow_html=True)

# --- SESSION STATE (പേജുകൾ നിയന്ത്രിക്കാൻ) ---
if 'main_page' not in st.session_state:
    st.session_state.main_page = "Home"
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Stocks"
if 'chart_symbol' not in st.session_state:
    st.session_state.chart_symbol = "^NSEI"

# --- DATA FETCHING ---
@st.cache_data(ttl=30)
def get_live_quote(symbol):
    try:
        data = yf.Ticker(symbol).history(period="1d", interval="1m")
        return data.iloc[-1] if not data.empty else None
    except: return None

# --- TOP INDICES SECTION ---
idx_col1, idx_col2 = st.columns(2)
nifty = get_live_quote("^NSEI")
banknifty = get_live_quote("^NSEBANK")

with idx_col1:
    if nifty is not None:
        st.markdown(f'<div class="idx-box"><small>NIFTY 50</small><br><b>{nifty["Close"]:,.2f}</b> <small style="color:green;">+0.45%</small></div>', unsafe_allow_html=True)
with idx_col2:
    if banknifty is not None:
        st.markdown(f'<div class="idx-box"><small>NIFTY BANK</small><br><b>{banknifty["Close"]:,.2f}</b> <small style="color:green;">+0.82%</small></div>', unsafe_allow_html=True)

# --- MAIN PAGE LOGIC ---

# 1. HOME PAGE (ഇവിടെയാണ് സ്റ്റോക്കുകളും ടാബുകളും ഉള്ളത്)
if st.session_state.main_page == "Home":
    st.text_input("🔍 Search stocks, F&O, etc.", placeholder="Eg: Reliance, Crude Oil")
    
    # ടാബുകൾ (Watchlist, Stocks, F&O, Commodity)
    tab_list = ["Watchlist", "Stocks", "F&O", "Commodity"]
    cols = st.columns(len(tab_list))
    for i, t in enumerate(tab_list):
        if cols[i].button(t, key=f"tab_{t}"):
            st.session_state.active_tab = t

    st.divider()

    # ടാബ് കണ്ടന്റുകൾ
    if st.session_state.active_tab == "Stocks":
        stocks = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS", "TATAMOTORS.NS", "ITC.NS"]
        for s in stocks:
            st.markdown(f'<div class="symbol-row"><div><b>{s.replace(".NS","")}</b><br><small>NSE</small></div><div class="price-green">₹ {get_live_quote(s)["Close"]:,.2f}</div></div>', unsafe_allow_html=True)
            if st.button(f"Chart: {s}", key=f"btn_{s}"):
                st.session_state.chart_symbol = s
                st.session_state.main_page = "Chart"
                st.rerun()

    elif st.session_state.active_tab == "F&O":
        fo_list = ["NIFTY 23000 CE", "BANKNIFTY 48000 PE", "FINNIFTY 21000 CE"]
        for fo in fo_list:
            st.markdown(f'<div class="symbol-row"><div><b>{fo}</b><br><small>NFO</small></div><div class="price-red">₹ 142.50</div></div>', unsafe_allow_html=True)

    elif st.session_state.active_tab == "Commodity":
        coms = {"CRUDE OIL": "CL=F", "GOLD": "GC=F", "SILVER": "SI=F"}
        for name, sym in coms.items():
            st.markdown(f'<div class="symbol-row"><div><b>{name}</b><br><small>MCX</small></div><div class="price-green">$ {get_live_quote(sym)["Close"]:,.2f}</div></div>', unsafe_allow_html=True)
            if st.button(f"Chart: {name}", key=f"btn_{sym}"):
                st.session_state.chart_symbol = sym
                st.session_state.main_page = "Chart"
                st.rerun()

# 2. CHART PAGE (ഫുൾ സ്ക്രീൻ ചാർട്ട്)
elif st.session_state.main_page == "Chart":
    st.button("⬅️ Back", on_click=lambda: st.session_state.update({"main_page": "Home"}))
    st.subheader(f"📈 {st.session_state.chart_symbol} Live")
    df = yf.download(st.session_state.chart_symbol, period="1d", interval="1m")
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_white", height=600, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# 3. ORDERS PAGE
elif st.session_state.main_page == "Orders":
    st.title("📑 Orders")
    st.info("നിങ്ങൾ നിലവിൽ ഓർഡറുകൾ ഒന്നും നൽകിയിട്ടില്ല.")
    st.button("Back to Home", on_click=lambda: st.session_state.update({"main_page": "Home"}))

# 4. ACCOUNT PAGE
elif st.session_state.main_page == "Account":
    st.title("👤 My Account")
    st.write(f"**Name:** Faisal")
    st.write("**Account ID:** FTB8899")
    st.button("Logout", type="primary")
    st.button("Back to Home", on_click=lambda: st.session_state.update({"main_page": "Home"}))

# --- BOTTOM NAVIGATION BAR ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)

if nav_col1.button("🏠\nHome"): st.session_state.main_page = "Home"; st.rerun()
if nav_col2.button("📑\nOrders"): st.session_state.main_page = "Orders"; st.rerun()
if nav_col3.button("💰\nPortfolio"): st.toast("Portfolio empty")
if nav_col4.button("👤\nAccount"): st.session_state.main_page = "Account"; st.rerun()
