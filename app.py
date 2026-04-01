import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. App Settings
st.set_page_config(page_title="FTB PRO 🚀", layout="wide")

# CSS: Button-ukal grid aayi set cheyyan (43653.jpg look)
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    .stButton>button { 
        width: 100%; border-radius: 10px; height: 60px; 
        background-color: #1e222d; color: white; 
        border: 1px solid #363c4e; font-size: 16px; margin-bottom: 5px;
    }
    .stButton>button:hover { border-color: #2962ff; background-color: #2a2e39; }
    </style>
    """, unsafe_allow_html=True)

# Navigation Logic
if 'page' not in st.session_state:
    st.session_state.page = "Main_Menu"

# --- 1. MAIN MENU (Buttons Section) ---
if st.session_state.page == "Main_Menu":
    # Top Ticker (43653.jpg pole)
    st.markdown("""
        <div style="background-color: #1e222d; padding: 12px; border-radius: 5px; text-align: center; margin-bottom: 20px;">
            <span style="color: #f23645;">NIFTY: ₹ 22,679</span> | <span style="color: #089981;">BANK NIFTY: ₹ 51,448</span>
        </div>
    """, unsafe_allow_html=True)

    # 2 Columns grid for buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 Home"): st.session_state.page = "Home"
        if st.button("📊 Indices"): st.session_state.page = "Indices"
        if st.button("💱 Currency"): st.session_state.page = "Currency"
        
    with col2:
        if st.button("📈 Chart"): st.session_state.page = "Chart"
        if st.button("🛢️ Commodity"): st.session_state.page = "Commodity"
        if st.button("👤 Profile"): st.session_state.page = "Profile"

# --- 2. INDICES PAGE (Nifty, Bank Nifty, Sensex) ---
elif st.session_state.page == "Indices":
    st.title("📊 Market Indices")
    indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "SENSEX": "^BSESN", "GIFT NIFTY": "GIFTY.NS"}
    for name, sym in indices.items():
        val = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
        st.info(f"**{name}**: ₹ {val:,.2f}")
    if st.button("⬅️ Back"): st.session_state.page = "Main_Menu"

# --- 3. COMMODITY PAGE (Crude Oil MCX) ---
elif st.session_state.page == "Commodity":
    st.title("🛢️ MCX & Commodities")
    crude = yf.Ticker("CL=F").history(period="1d")['Close'].iloc[-1]
    st.success(f"**CRUDE OIL (Live)**: $ {crude:,.2f}")
    st.write("MCX live rates load cheyyunnu...")
    if st.button("⬅️ Back"): st.session_state.page = "Main_Menu"

# --- 4. CURRENCY PAGE (Exchange & Calculator) ---
elif st.session_state.page == "Currency":
    st.title("💱 Currency Exchange")
    # Exchange rate USD to INR
    rate = yf.Ticker("INR=X").history(period="1d")['Close'].iloc[-1]
    st.metric("USD to INR", f"₹ {rate:.2f}")
    
    # Simple Calculator
    st.subheader("Calculator")
    usd_input = st.number_input("Enter USD amount", value=1.0)
    st.write(f"In Indian Rupees: **₹ {usd_input * rate:.2f}**")
    
    if st.button("⬅️ Back"): st.session_state.page = "Main_Menu"

# --- (Bakki Pages: Home, Chart, Profile thudarnnu pokum) ---
elif st.session_state.page == "Home":
    st.title("🏠 Home")
    st.write("Welcome to FTB PRO!")
    if st.button("⬅️ Back"): st.session_state.page = "Main_Menu"

elif st.session_state.page == "Chart":
    st.title("📈 Live Chart")
    st.write("Chart loading...")
    if st.button("⬅️ Back"): st.session_state.page = "Main_Menu"

elif st.session_state.page == "Profile":
    st.title("👤 My Profile")
    st.write("**Name:** Faisal")
    st.write("**Location:** Al Barsha, Dubai")
    if st.button("⬅️ Back"): st.session_state.page = "Main_Menu"
