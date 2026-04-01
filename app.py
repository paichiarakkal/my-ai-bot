import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

# 1. Page Settings
st.set_page_config(page_title="FTB PRO TERMINAL", layout="wide")

# Dark Theme CSS (43641.jpg ലുക്ക്)
st.markdown("""
    <style>
    .main { background-color: #131722; color: white; }
    header { visibility: hidden; }
    .stSelectbox { margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER & NAVIGATION ---
st.title("🚀 FTB PRO TERMINAL")

# വാച്ച്‌ലിസ്റ്റ് ചാർട്ടിന് മുകളിലായി നൽകുന്നു (മൊബൈലിൽ എളുപ്പത്തിൽ കാണാൻ)
watchlist = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "CRUDE OIL": "CL=F",
    "RELIANCE": "RELIANCE.NS",
    "SBIN": "SBIN.NS"
}

# 43632.jpg പോലെ സ്റ്റോക്ക് തിരഞ്ഞെടുക്കാൻ
selected_name = st.selectbox("Select Asset from Watchlist", list(watchlist.keys()))
ticker = watchlist[selected_name]

# --- CHART SECTION ---
try:
    df = yf.download(ticker, period="2d", interval="5m", multi_level_index=False)
    
    if not df.empty:
        # പ്രൊഫഷണൽ കാൻഡിൽസ്റ്റിക് (43633.jpg ലുക്ക്)
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'], high=df['High'],
            low=df['Low'], close=df['Close'],
            increasing_line_color='#089981', decreasing_line_color='#f23645'
        )])

        fig.update_layout(
            template='plotly_dark',
            xaxis_rangeslider_visible=False,
            height=500,
            paper_bgcolor='#131722',
            plot_bgcolor='#131722',
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # ലൈവ് പ്രൈസ് (43632.jpg പോലെ കൃത്യമായി കാണാൻ)
        curr_price = df['Close'].iloc[-1]
        st.markdown(f"<h2 style='text-align: center; color: #2962ff;'>₹ {curr_price:,.2f}</h2>", unsafe_allow_html=True)

except:
    st.error("Market Data ലോഡ് ആവുന്നില്ല. ഇന്റർനെറ്റ് ചെക്ക് ചെയ്യൂ.")

# ചുവടെ മറ്റ് മെനുകൾ നൽകാം
st.divider()
cols = st.columns(3)
cols[0].button("🏠 Home")
cols[1].button("📈 Explore")
cols[2].button("👤 Profile")
