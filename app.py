import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. Page Settings
st.set_page_config(page_title="FTB PRO TERMINAL", layout="wide")

# CSS: മുകളിലെ ടിക്കറിനും ഡാർക്ക് ലുക്കിനും വേണ്ടി
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    /* ടിക്കർ ഡിസൈൻ */
    .ticker-wrap { background: #1e222d; padding: 10px; border-bottom: 1px solid #2a2e39; margin-bottom: 20px; }
    .ticker-item { display: inline-block; padding: 0 20px; border-right: 1px solid #363c4e; }
    .price-up { color: #089981; }
    .price-down { color: #f23645; }
    </style>
    """, unsafe_allow_html=True)

# --- MARKET DATA FETCHING ---
def get_live_mini_data():
    symbols = {
        "NIFTY": "^NSEI",
        "BANK NIFTY": "^NSEBANK",
        "SENSEX": "^BSESN",
        "CRUDE OIL": "CL=F" # MCX Crude Oil International Lead
    }
    data_list = []
    for name, sym in symbols.items():
        try:
            ticker = yf.Ticker(sym).history(period="1d")
            price = ticker['Close'].iloc[-1]
            change = price - ticker['Open'].iloc[0]
            data_list.append({"name": name, "price": price, "change": change})
        except:
            continue
    return data_list

# --- TOP TICKER SECTION (43632.jpg ലുക്ക്) ---
market_data = get_live_mini_data()
ticker_html = '<div class="ticker-wrap">'
for item in market_data:
    color_class = "price-up" if item['change'] >= 0 else "price-down"
    ticker_html += f'<div class="ticker-item"><b>{item["name"]}</b>: <span class="{color_class}">₹ {item["price"]:,.2f}</span></div>'
ticker_html += '</div>'
st.markdown(ticker_html, unsafe_allow_html=True)

# --- NAVIGATION MENU ---
if 'page' not in st.session_state:
    st.session_state.page = "🏠 Home"

col1, col2, col3 = st.columns(3)
if col1.button("🏠 Home"): st.session_state.page = "Home"
if col2.button("📈 Chart"): st.session_state.page = "Chart"
if col3.button("👤 Profile"): st.session_state.page = "Profile"

st.divider()

# --- PAGE LOGIC ---

if st.session_state.page == "Home":
    st.subheader("📊 Indian Market Overview")
    for item in market_data:
        # ഓരോ ഇൻഡക്സും കാർഡുകളായി കാണിക്കുന്നു (43649.jpg പോലെ)
        with st.container():
            st.markdown(f"""
                <div style="background-color: #1e222d; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #2962ff;">
                    <h4 style="margin:0;">{item['name']}</h4>
                    <h2 style="margin:5px 0; color: white;">₹ {item['price']:,.2f}</h2>
                </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "Chart":
    st.subheader("📈 Live Technical Chart")
    selected = st.selectbox("Select Asset", ["^NSEI", "^NSEBANK", "^BSESN", "CL=F"])
    
    df = yf.download(selected, period="2d", interval="5m", multi_level_index=False)
    if not df.empty:
        # പ്രൊഫഷണൽ കാൻഡിൽസ്റ്റിക് (43641.jpg ലുക്ക്)
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template='plotly_dark', height=500, paper_bgcolor='#131722', plot_bgcolor='#131722', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Profile":
    st.title("👤 Trader Profile")
    st.write("**Name:** Faisal")
    st.write("**Account:** Indian Market Pro")
