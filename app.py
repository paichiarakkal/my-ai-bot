import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai

# 1. Gemini AI Config
genai.configure(api_key="AIzaSyCanT29LeVv_9031swUtfXQcS3FLPemi3A")
model = genai.GenerativeModel('gemini-pro')

# 2. Page Config
st.set_page_config(page_title="FTB PRO TRADER", page_icon="📈", layout="wide")

# Custom CSS for Deep Blue Theme
st.markdown("""
    <style>
    .main { background-color: #0e1629; color: white; }
    .stMetric { background-color: #1a223f; border-radius: 10px; padding: 15px; border: 1px solid #2b3766; }
    .stSidebar { background-color: #141c34; }
    div[data-testid="stExpander"] { background-color: #1a223f; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h1 style='text-align: center; color: #00E676;'>🚀 FTB PRO</h1>", unsafe_allow_html=True)
page = st.sidebar.radio("MENU", ["📊 Trading Terminal", "🤖 FTB AI Assistant", "💰 Expense Manager"])

st.sidebar.divider()

# Currency Converter
st.sidebar.subheader("💰 Currency Converter")
try:
    rate_data = yf.Ticker("AEDINR=X").history(period="1d")
    if not rate_data.empty:
        rate = rate_data['Close'].iloc[-1]
        aed_input = st.sidebar.number_input("Enter AED", value=1.0, step=1.0)
        st.sidebar.success(f"₹ {aed_input * rate:,.2f} INR")
except:
    st.sidebar.error("Rates offline")

# --- SMART TICKER FUNCTION ---
def get_ticker(name):
    mapping = {"nifty": "^NSEI", "bank nifty": "^NSEBANK", "crude": "CL=F", "crude oil": "CL=F", "gold": "GC=F"}
    name = name.lower().strip()
    return mapping.get(name, f"{name.upper()}.NS")

# --- PAGE 1: TRADING TERMINAL ---
if page == "📊 Trading Terminal":
    st.markdown("<h2 style='color: #00E676;'>📉 FTB Live Terminal</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        search = st.text_input("Symbol (Nifty, Crude, etc.)", value="Nifty")
        interval = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"], index=1)
        ma_period = st.slider("Moving Average Period", 5, 50, 20)
    
    ticker_sym = get_ticker(search)
    
    with col1:
        try:
            df = yf.download(ticker_sym, period="5d", interval=interval, multi_level_index=False)
            
            if not df.empty:
                # Calculations
                df['MA'] = df['Close'].rolling(window=ma_period).mean()
                
                curr_p = df['Close'].iloc[-1]
                prev_p = df['Close'].iloc[-2]
                change = curr_p - prev_p
                
                st.metric(label=f"{search.upper()} LIVE", value=f"₹ {curr_p:,.2f}", delta=f"{change:.2f}")

                # Chart with Indicators
                fig = go.Figure()
                # Candlestick
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
                # Moving Average
                fig.add_trace(go.Scatter(x=df.index, y=df['MA'], line=dict(color='#FFEB3B', width=1.5), name=f"MA {ma_period}"))
                # Volume
                fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name="Volume", opacity=0.3, yaxis="y2"))

                # Buy/Sell Logic (Simple MA Crossover)
                if curr_p > df['MA'].iloc[-1]:
                    st.sidebar.success("🚀 SIGNAL: BUY / BULLISH")
                else:
                    st.sidebar.error("🔻 SIGNAL: SELL / BEARISH")

                fig.update_layout(
                    height=600, template='plotly_dark',
                    xaxis_rangeslider_visible=False,
                    yaxis2=dict(title="Volume", overlaying="y", side="right", showgrid=False),
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("No data found.")
        except:
            st.error("Connection error. Please refresh.")

# --- OTHER PAGES (AI & EXPENSE) ---
elif page == "🤖 FTB AI Assistant":
    st.markdown("<h2 style='color: #00E676;'>🤖 AI Support</h2>", unsafe_allow_html=True)
    prompt = st.chat_input("Ask Faisal's AI...")
    if prompt:
        with st.chat_message("assistant"):
            response = model.generate_content(f"Answer in Malayalam as a trading expert for Faisal: {prompt}")
            st.write(response.text)

elif page == "💰 Expense Manager":
    st.markdown("<h2 style='color: #00E676;'>📥 Expenses</h2>", unsafe_allow_html=True)
    item = st.text_input("Item")
    amt = st.number_input("Amount", min_value=0.0)
    if st.button("Save"): st.success(f"Saved: {item} - ₹{amt}")
