import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import urllib.parse
import pandas_ta as ta

# 1. Gemini AI Config (Updated with your key)
genai.configure(api_key="AIzaSyAVpgLWVDYglDw59PPADTrNM0_AYLT66Rc")
model = genai.GenerativeModel('gemini-pro')

# 2. Page Config
st.set_page_config(page_title="FTB PRO TRADER", page_icon="📈", layout="wide")

# Custom CSS for Light Professional Theme
st.markdown("""
    <style>
    .main { background-color: #F0F2F6; color: #1F2937; } 
    div[data-testid="stMetric"] { 
        background-color: #FFFFFF; border-radius: 12px; padding: 20px; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #E5E7EB;
    }
    .stSidebar { background-color: #FFFFFF; border-right: 1px solid #E5E7EB; }
    .whatsapp-btn {
        background-color: #25D366; color: white; padding: 12px 24px;
        border-radius: 8px; display: block; text-align: center;
        font-weight: bold; text-decoration: none; margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SMART TICKER FUNCTION ---
def get_ticker(name):
    name = name.upper().strip()
    mapping = {"NIFTY": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE": "CL=F", "GOLD": "GC=F"}
    if name in mapping:
        return mapping[name]
    return name if "." in name else f"{name}.NS"

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h1 style='text-align: center; color: #2563EB;'>🚀 FTB PRO</h1>", unsafe_allow_html=True)
page = st.sidebar.radio("MENU", ["📊 Trading Terminal", "🤖 AI Trading Assistant", "💰 Expense Manager"])

# --- PAGE 1: TRADING TERMINAL ---
if page == "📊 Trading Terminal":
    st.markdown("<h2 style='color: #2563EB;'>📉 Live Market Terminal</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col2:
        search = st.text_input("Symbol", value="Nifty")
        interval = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"], index=1)
        
        st.subheader("🛠 Indicators Settings")
        show_ma = st.checkbox("Moving Average (MA)", value=True)
        ma_val = st.number_input("MA Period", value=20, min_value=1)
        
        show_st = st.checkbox("Supertrend", value=True)
        st_period = st.number_input("ST Period", value=7)
        st_mult = st.number_input("ST Multiplier", value=3.0)
        
        # WhatsApp Share
        whatsapp_url = f"https://wa.me/?text={urllib.parse.quote('Check FTB PRO Analysis: https://upqvdh.streamlit.app')}"
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📲 Share on WhatsApp</a>', unsafe_allow_html=True)

    ticker_sym = get_ticker(search)
    with col1:
        try:
            df = yf.download(ticker_sym, period="5d", interval=interval, multi_level_index=False)
            if not df.empty:
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
                
                # Indicators
                if show_ma:
                    df['MA'] = ta.sma(df['Close'], length=ma_val)
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA'], line=dict(color='#2563EB', width=1.5), name=f"MA {ma_val}"))
                
                if show_st:
                    sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=st_period, multiplier=st_mult)
                    df['ST'] = sti[f'SUPERT_{st_period}_{st_mult}']
                    fig.add_trace(go.Scatter(x=df.index, y=df['ST'], line=dict(color='#FF9800', width=2), name="Supertrend"))

                fig.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                curr_p = df['Close'].iloc[-1]
                st.metric(f"{search.upper()} LIVE PRICE", f"₹ {curr_p:,.2f}")
            else:
                st.error("No data found.")
        except Exception as e:
            st.error(f"Error: {e}")

# --- PAGE 2: AI TRADING ASSISTANT (Smart Advisor) ---
elif page == "🤖 AI Trading Assistant":
    st.markdown("<h2 style='color: #2563EB;'>🤖 FTB Smart Advisor</h2>", unsafe_allow_html=True)
    stock_to_analyze = st.text_input("ഏത് സ്റ്റോക്കിനെ കുറിച്ചാണ് ചോദിക്കേണ്ടത്?", value="Nifty")
    user_q = st.chat_input("നിങ്ങളുടെ സംശയം ഇവിടെ ടൈപ്പ് ചെയ്യൂ (eg: Can I buy now?)")

    if user_q:
        with st.spinner("വിപണി വിശകലനം ചെയ്യുന്നു..."):
            t_sym = get_ticker(stock_to_analyze)
            data = yf.download(t_sym, period="5d", interval="15m")
            
            if not data.empty:
                cp = data['Close'].iloc[-1]
                # Simple Technical Context for AI
                prompt = f"User asks: '{user_q}' about {stock_to_analyze}. Current price is {cp}. Analyze the market and give a detailed professional answer in Malayalam with a Buy/Sell/Wait recommendation."
                
                response = model.generate_content(prompt)
                with st.chat_message("assistant"):
                    st.write(f"**Current Status of {stock_to_analyze}: ₹{cp:,.2f}**")
                    st.write(response.text)
            else:
                st.error("ഡാറ്റ ലഭ്യമല്ല.")

# --- PAGE 3: EXPENSE MANAGER ---
elif page == "💰 Expense Manager":
    st.markdown("<h2 style='color: #2563EB;'>📥 Expense Tracker</h2>", unsafe_allow_html=True)
    item = st.text_input("Item Name")
    amt = st.number_input("Amount", min_value=0.0)
    if st.button("Save"):
        st.success(f"Saved: {item} - ₹{amt}")
