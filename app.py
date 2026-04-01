import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="FTB PRO 🚀", layout="wide")

# CSS: മുകളിലുള്ള മെനുവിനും ഡാർക്ക് തീമിനും വേണ്ടി
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    /* മുകളിലെ ബട്ടണുകൾ ശരിയാക്കാൻ */
    .stOptionMenu { margin-bottom: 20px; }
    div[data-testid="stHorizontalBlock"] > div {
        background-color: #1e222d;
        border-radius: 10px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# --- TOP NAVIGATION MENU (സൈഡ്‌ബാറിന് പകരമുള്ള മെനു) ---
# സെലക്ഷൻ ഓർത്തു വെക്കാൻ
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Home"

# സ്ക്രീനിന് മുകളിൽ മൂന്ന് ബട്ടണുകൾ നൽകുന്നു
col1, col2, col3 = st.columns(3)

if col1.button("🏠 Home"):
    st.session_state.current_page = "🏠 Home"
if col2.button("📈 Chart"):
    st.session_state.current_page = "📈 Chart"
if col3.button("👤 Profile"):
    st.session_state.current_page = "👤 Profile"

st.divider() # ഒരു ചെറിയ വര

# --- PAGE LOGIC ---

# 1. HOME PAGE
if st.session_state.current_page == "🏠 Home":
    st.title("Market Overview")
    st.write("പ്രധാന മാർക്കറ്റ് അപ്‌ഡേറ്റുകൾ താഴെ കാണാം.")
    
    # Nifty & Bank Nifty വിലകൾ (43651.jpg ലുക്ക്)
    nifty_val = yf.Ticker("^NSEI").history(period="1d")['Close'].iloc[-1]
    bank_val = yf.Ticker("^NSEBANK").history(period="1d")['Close'].iloc[-1]
    
    st.info(f"**NIFTY 50**: ₹ {nifty_val:,.2f}")
    st.info(f"**BANK NIFTY**: ₹ {bank_val:,.2f}")

# 2. CHART PAGE (43641.jpg ലുക്ക്)
elif st.session_state.current_page == "📈 Chart":
    st.title("Live Analysis")
    symbol = st.selectbox("Select Asset", ["^NSEI", "^NSEBANK", "CL=F", "AAPL"])
    
    df = yf.download(symbol, period="2d", interval="5m", multi_level_index=False)
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(
            x=df.index, open=df['Open'], high=df['High'], 
            low=df['Low'], close=df['Close']
        )])
        fig.update_layout(template='plotly_dark', height=500, paper_bgcolor='#131722', plot_bgcolor='#131722')
        st.plotly_chart(fig, use_container_width=True)
        st.subheader(f"Current Price: ₹ {df['Close'].iloc[-1]:,.2f}")

# 3. PROFILE PAGE
elif st.session_state.current_page == "👤 Profile":
    st.title("Trader Profile")
    st.write("**Name:** Faisal")
    st.write("**Account Status:** Pro Active 🦾")
    st.button("Update Profile")
