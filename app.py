import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import urllib.parse

# 1. പുതിയ API Key ഇവിടെ സെറ്റ് ചെയ്തു
genai.configure(api_key="AIzaSyAVpgLWVDYglDw59PPADTrNM0_AYLT66Rc")
model = genai.GenerativeModel('gemini-pro')

# 2. Page Config
st.set_page_config(page_title="FTB PRO TRADER", page_icon="📈", layout="wide")

# Custom CSS for Light Theme
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

# --- SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h1 style='text-align: center; color: #2563EB;'>🚀 FTB PRO</h1>", unsafe_allow_html=True)
page = st.sidebar.radio("MENU", ["📊 Trading Terminal", "🤖 FTB AI Assistant", "💰 Expense Manager"])

# --- SMART TICKER FUNCTION (Stocks & Indices പരിഹരിക്കാൻ) ---
def get_ticker(name):
    name = name.upper().strip()
    mapping = {
        "NIFTY": "^NSEI", 
        "BANK NIFTY": "^NSEBANK", 
        "CRUDE": "CL=F", 
        "GOLD": "GC=F",
        "RELIANCE": "RELIANCE.NS",
        "TATA": "TATAMOTORS.NS"
    }
    if name in mapping:
        return mapping[name]
    elif "." in name: # ഉദാഹരണത്തിന് RELIANCE.NS എന്ന് നേരിട്ട് അടിച്ചാൽ
        return name
    else: # വെറും പേര് അടിച്ചാൽ .NS ചേർക്കും
        return f"{name}.NS"

# --- PAGE 1: TRADING TERMINAL ---
if page == "📊 Trading Terminal":
    st.markdown("<h2 style='color: #2563EB;'>📉 Live Market View</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col2:
        search = st.text_input("Symbol (Nifty, Crude, Reliance...)", value="Nifty")
        interval = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"], index=1)
        ma_period = st.slider("MA Period", 5, 50, 20)
        
        # WhatsApp Share
        app_url = "https://upqvdh.streamlit.app"
        share_text = f"Check FTB Analysis for {search}: {app_url}"
        whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(share_text)}"
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📲 Share on WhatsApp</a>', unsafe_allow_html=True)
    
    ticker_sym = get_ticker(search)
    
    with col1:
        try:
            # ഡാറ്റ ഡൗൺലോഡ് ചെയ്യുന്നു
            df = yf.download(ticker_sym, period="5d", interval=interval, multi_level_index=False)
            if not df.empty:
                df['MA'] = df['Close'].rolling(window=ma_period).mean()
                curr_p = df['Close'].iloc[-1]
                
                # Signal Logic
                if curr_p > df['MA'].iloc[-1]:
                    st.sidebar.success(f"🚀 {search} IS BULLISH")
                else:
                    st.sidebar.error(f"🔻 {search} IS BEARISH")
                
                st.metric(label=f"{search.upper()} PRICE", value=f"₹ {curr_p:,.2f}")

                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
                fig.add_trace(go.Scatter(x=df.index, y=df['MA'], line=dict(color='#2563EB', width=1.5), name=f"MA {ma_period}"))
                fig.update_layout(height=550, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error(f"No data found for {search}. Try adding '.NS' (e.g., RELIANCE.NS)")
        except:
            st.error("Market data connection error")

# --- PAGE 2: AI ASSISTANT ---
elif page == "🤖 FTB AI Assistant":
    st.markdown("<h2 style='color: #2563EB;'>🤖 AI Support</h2>", unsafe_allow_html=True)
    prompt = st.chat_input("Ask Faisal's AI...")
    if prompt:
        with st.chat_message("assistant"):
            try:
                response = model.generate_content(f"Answer in Malayalam: {prompt}")
                st.write(response.text)
            except:
                st.error("AI Error: Please check if API Key is valid.")

# --- PAGE 3: EXPENSE MANAGER ---
elif page == "💰 Expense Manager":
    st.markdown("<h2 style='color: #2563EB;'>📥 Expense Tracker</h2>", unsafe_allow_html=True)
    item = st.text_input("Item Name")
    amt = st.number_input("Amount", min_value=0.0)
    if st.button("Save"):
        st.success(f"Saved: {item} - ₹{amt}")
