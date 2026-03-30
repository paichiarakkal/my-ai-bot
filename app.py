import streamlit as st
import yfinance as yf
from PIL import Image
import os
import plotly.graph_objects as go

# 1. പേജ് സെറ്റപ്പ്
st.set_page_config(page_title="Faisal Pro Smart Bot", layout="wide")

# 2. ഹെഡർ
cols = st.columns([1, 4, 1])
with cols[1]:
    if os.path.exists("image_12.png"):
        st.image(Image.open("image_12.png"), width=150)
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📊 ഫൈസൽസ് പ്രോ ട്രേഡിംഗ് ചാർട്ട്സ്</h1>", unsafe_allow_html=True)

# 3. കറൻസി കൺവെർട്ടർ (Sidebar)
st.sidebar.header("💰 AED to INR")
currency_data = yf.Ticker("AEDINR=X").history(period="1d")
live_rate = currency_data['Close'].iloc[-1]
aed = st.sidebar.number_input("ദിർഹം (AED)", min_value=0.0, value=1000.0)
st.sidebar.success(f"നാട്ടിലെ തുക: ₹{aed * live_rate:,.2f}")

# 4. Candlestick Chart ഉണ്ടാക്കുന്ന ഫങ്ക്ഷൻ
def draw_upstox_chart(name, sym, multi):
    df = yf.Ticker(sym).history(period="1d", interval="5m")
    if not df.empty:
        # വില കറക്റ്റ് ചെയ്യുന്നു
        df['Open'] *= multi
        df['High'] *= multi
        df['Low'] *= multi
        df['Close'] *= multi
        
        fig = go.Figure(data=[go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            increasing_line_color= '#26a69a', decreasing_line_color= '#ef5350'
        )])
        
        fig.update_layout(
            title=f"{name} ലൈവ് ചാർട്ട് (5 min)",
            xaxis_rangeslider_visible=False,
            template="plotly_dark",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error(f"{name} ഡാറ്റ കിട്ടിയില്ല")

# 5. മെയിൻ ഡിസ്‌പ്ലേ
symbols = {
    "Nifty 50": {"sym": "^NSEI", "multi": 1},
    "Crude Oil (INR)": {"sym": "CL=F", "multi": 83.30}
}

for name, info in symbols.items():
    draw_upstox_chart(name, info["sym"], info["multi"])

st.info("💡 Upstox-ൽ കാണുന്നതുപോലെ ചാർട്ടിൽ തൊട്ടാൽ നിങ്ങൾക്ക് വില അറിയാൻ സാധിക്കും.")
