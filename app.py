import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="FTB PRO 🚀", layout="wide")

# CSS: ലുക്ക് ശരിയാക്കാൻ (43652.jpg പോലെ ഡാർക്ക് തീം)
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    .stButton>button { width: 100%; border-radius: 10px; background-color: #1e222d; color: white; border: 1px solid #363c4e; height: 50px; font-size: 18px; margin-bottom: 10px;}
    .stButton>button:hover { background-color: #2962ff; }
    </style>
    """, unsafe_allow_html=True)

# --- NAVIGATION LOGIC ---
# ഏത് പേജിലാണെന്ന് ഓർത്തു വെക്കാൻ
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Main_Menu"

# --- 1. MAIN MENU (നിന്റെ ഹോം സ്ക്രീൻ - 43652.jpg പോലെ) ---
if st.session_state.current_page == "Main_Menu":
    # മുകളിലെ ടിക്കർ (43652.jpg ലുക്ക്)
    st.markdown("""
        <div style="background-color: #1e222d; padding: 15px; border-radius: 5px; margin-bottom: 20px; text-align: center;">
            <span style="color: #f23645;">NIFTY: ₹ 22,679.40</span> | 
            <span style="color: #089981;">BANK NIFTY: ₹ 51,448.65</span>
        </div>
    """, unsafe_allow_html=True)

    # മെനു ബട്ടണുകൾ
    if st.button("🏠 Home"):
        st.session_state.current_page = "Home_Page"
        st.rerun()
    
    if st.button("📈 Chart"):
        st.session_state.current_page = "Chart_Page"
        st.rerun()
        
    if st.button("👤 Profile"):
        st.session_state.current_page = "Profile_Page"
        st.rerun()

# --- 2. HOME PAGE (മാർക്കറ്റ് വിവരങ്ങൾ മാത്രം - 43651.jpg പോലെ) ---
elif st.session_state.current_page == "Home_Page":
    st.title("🏠 Market Overview")
    st.write("ഇന്ത്യൻ മാർക്കറ്റിലെ പ്രധാന വിവരങ്ങൾ ഇവിടെ കാണാം.")
    
    # Nifty & Bank Nifty Cards (43649.jpg ലുക്ക്)
    indices = {"NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK", "SENSEX": "^BSESN", "CRUDE OIL": "CL=F"}
    for name, sym in indices.items():
        price = yf.Ticker(sym).history(period="1d")['Close'].iloc[-1]
        st.info(f"**{name}**: ₹ {price:,.2f}")
    
    if st.button("⬅️ Back to Menu"):
        st.session_state.current_page = "Main_Menu"
        st.rerun()

# --- 3. CHART PAGE (ചാർട്ട് മാത്രം - 43641.jpg പോലെ) ---
elif st.session_state.current_page == "Chart_Page":
    st.title("📈 Advanced Chart")
    selected = st.selectbox("Select Asset", ["^NSEI", "^NSEBANK", "CL=F"])
    
    df = yf.download(selected, period="2d", interval="5m", multi_level_index=False)
    if not df.empty:
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
        fig.update_layout(template='plotly_dark', height=500, paper_bgcolor='#131722', plot_bgcolor='#131722', xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)
        st.success(f"Live Price: ₹ {df['Close'].iloc[-1]:,.2f}")

    if st.button("⬅️ Back to Menu"):
        st.session_state.current_page = "Main_Menu"
        st.rerun()

# --- 4. PROFILE PAGE (പ്രൊഫൈൽ വിവരങ്ങൾ മാത്രം) ---
elif st.session_state.current_page == "Profile_Page":
    st.title("👤 My Profile")
    st.write("**Name:** Faisal")
    st.write("**Location:** Al Barsha, Dubai")
    st.write("**Status:** Pro Trader 🦾")
    
    if st.button("⬅️ Back to Menu"):
        st.session_state.current_page = "Main_Menu"
        st.rerun()
