import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Upstox Pro", layout="wide")

# CSS: ഒറിജിനൽ അപ്സ്റ്റോക്സ് യൂസർ ഇന്റർഫേസ് (UI)
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    /* Indices Styling */
    .idx-container { display: flex; gap: 10px; margin-bottom: 20px; }
    .idx-card { background: #f9f9f9; padding: 10px; border-radius: 8px; flex: 1; border: 1px solid #eee; }
    /* Stock Row */
    .stock-item { display: flex; justify-content: space-between; padding: 15px; border-bottom: 1px solid #f2f2f2; }
    .price-up { color: #089981; font-weight: bold; }
    .price-down { color: #f23645; font-weight: bold; }
    /* Bottom Navigation */
    .nav-bar { position: fixed; bottom: 0; left: 0; width: 100%; background: white; border-top: 1px solid #ddd; display: flex; justify-content: space-around; padding: 10px; z-index: 100; }
    </style>
    """, unsafe_allow_html=True)

# --- സെഷൻ മാനേജ്‌മെന്റ് ---
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'tab' not in st.session_state: st.session_state.tab = "Stocks"
if 'symbol' not in st.session_state: st.session_state.symbol = "^NSEI"

# തത്സമയ വിവരങ്ങൾ എടുക്കാനുള്ള ഫങ്ക്ഷൻ
def get_data(ticker):
    try:
        val = yf.Ticker(ticker).history(period="1d", interval="1m")
        return val.iloc[-1] if not val.empty else None
    except: return None

# --- TOP INDICES ---
st.markdown("### Indices")
nifty = get_data("^NSEI")
bank = get_data("^NSEBANK")

c1, c2 = st.columns(2)
if nifty is not None:
    c1.markdown(f'<div class="idx-card"><small>NIFTY 50</small><br><b>{nifty["Close"]:,.2f}</b> <span style="color:green;">+1.56%</span></div>', unsafe_allow_html=True)
if bank is not None:
    c2.markdown(f'<div class="idx-card"><small>NIFTY BANK</small><br><b>{bank["Close"]:,.2f}</b> <span style="color:green;">+2.33%</span></div>', unsafe_allow_html=True)

st.divider()

# --- പേജ് ലോജിക് ---

if st.session_state.page == "Home":
    st.text_input("🔍 Search for stocks, F&O and more", placeholder="Eg: Nifty, Crude Oil", key="search")
    
    # ടാബുകൾ
    t_list = ["Watchlist", "Stocks", "F&O", "Currency", "Commodity"]
    t_cols = st.columns(len(t_list))
    for i, t in enumerate(t_list):
        if t_cols[i].button(t, key=f"t_{t}"): st.session_state.tab = t

    # ടാബ് കണ്ടന്റുകൾ
    if st.session_state.tab == "Stocks":
        stock_list = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "SBIN.NS"]
        for s in stock_list:
            d = get_data(s)
            p = f"₹{d['Close']:,.2f}" if d is not None else "Loading..."
            st.markdown(f'<div class="stock-item"><div><b>{s.split(".")[0]}</b><br><small>NSE</small></div><div class="price-up">{p}</div></div>', unsafe_allow_html=True)
            if st.button(f"Chart", key=f"btn_{s}"): 
                st.session_state.symbol = s
                st.session_state.page = "Chart"
                st.rerun()

    elif st.session_state.tab == "F&O":
        fo_list = ["NIFTY 23000 CE", "BANKNIFTY 48000 PE"]
        for fo in fo_list:
            st.markdown(f'<div class="stock-item"><div><b>{fo}</b><br><small>NFO</small></div><div class="price-down">₹145.20</div></div>', unsafe_allow_html=True)

    elif st.session_state.tab == "Commodity":
        coms = {"CRUDE OIL": "CL=F", "GOLD": "GC=F"}
        for n, sym in coms.items():
            d = get_data(sym)
            p = f"${d['Close']:,.2f}" if d is not None else "---"
            st.markdown(f'<div class="stock-item"><div><b>{n}</b><br><small>MCX</small></div><div class="price-up">{p}</div></div>', unsafe_allow_html=True)
            if st.button(f"View Chart", key=sym):
                st.session_state.symbol = sym
                st.session_state.page = "Chart"
                st.rerun()

# ചാർട്ട് പേജ്
elif st.session_state.page == "Chart":
    if st.button("⬅️ Back"): st.session_state.page = "Home"; st.rerun()
    st.subheader(f"📈 {st.session_state.symbol} Live Chart")
    df = yf.download(st.session_state.symbol, period="1d", interval="1m")
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template="plotly_white", height=500, xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

# മറ്റ് പേജുകൾ
elif st.session_state.page == "Orders":
    st.title("📑 Orders")
    st.info("No active orders.")

elif st.session_state.page == "Account":
    st.title("👤 My Account")
    st.write("**Name:** Faisal")
    st.write("**ID:** UP12345")

# --- BOTTOM NAV BAR ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
b_col1, b_col2, b_col3, b_col4 = st.columns(4)
if b_col1.button("🏠 Home"): st.session_state.page = "Home"; st.rerun()
if b_col2.button("📑 Orders"): st.session_state.page = "Orders"; st.rerun()
if b_col3.button("💰 Portfolio"): st.toast("Portfolio empty")
if b_col4.button("👤 Account"): st.session_state.page = "Account"; st.rerun()
