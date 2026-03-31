import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai
import urllib.parse

# 1. Gemini AI Config
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

# --- SMART TICKER FUNCTION ---
def get_ticker(name):
    name = name.upper().strip()
    mapping = {"NIFTY": "^NSEI", "BANK NIFTY": "^NSEBANK", "CRUDE": "CL=F", "GOLD": "GC=F"}
    return mapping.get(name, f"{name}.NS") if name in mapping else (name if "." in name else f"{name}.NS")

# --- INDICATOR CALCULATIONS (Pandas മാത്രം ഉപയോഗിച്ച്) ---
def add_indicators(df):
    # 1. Simple Moving Average (SMA)
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    
    # 2. RSI (Relative Strength Index)
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    return df

# --- SIDEBAR ---
st.sidebar.markdown("<h1 style='text-align: center; color: #2563EB;'>🚀 FTB PRO</h1>", unsafe_allow_html=True)
page = st.sidebar.radio("MENU", ["📊 Trading Terminal", "🤖 AI Trading Assistant", "💰 Expense Manager"])

# --- PAGE 1: TRADING TERMINAL ---
if page == "📊 Trading Terminal":
    st.markdown("<h2 style='color: #2563EB;'>📉 Live Market Terminal</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col2:
        search = st.text_input("Symbol", value="Nifty")
        interval = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "1d"], index=1)
        
        whatsapp_url = f"https://wa.me/?text={urllib.parse.quote('Check FTB PRO Analysis: https://upqvdh.streamlit.app')}"
        st.markdown(f'<a href="{whatsapp_url}" target="_blank" class="whatsapp-btn">📲 Share on WhatsApp</a>', unsafe_allow_html=True)

    ticker_sym = get_ticker(search)
    with col1:
        try:
            df = yf.download(ticker_sym, period="5d", interval=interval, multi_level_index=False)
            if not df.empty:
                df = add_indicators(df)
                
                fig = go.Figure()
                fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name="Price"))
                fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='#2563EB', width=1.5), name="SMA 20"))

                fig.update_layout(height=500, template='plotly_white', xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
                
                # RSI Chart
                fig_rsi = go.Figure()
                fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='#FF9800'), name="RSI"))
                fig_rsi.update_layout(height=200, template='plotly_white')
                st.plotly_chart(fig_rsi, use_container_width=True)
                
                st.metric(f"{search.upper()} PRICE", f"₹ {df['Close'].iloc[-1]:,.2f}")
        except Exception as e:
            st.error(f"Error: {e}")

# --- PAGE 2: AI TRADING ASSISTANT ---
elif page == "🤖 AI Trading Assistant":
    st.markdown("<h2 style='color: #2563EB;'>🤖 AI Smart Advisor</h2>", unsafe_allow_html=True)
    stock_to_analyze = st.text_input("ഏത് സ്റ്റോക്കിനെ കുറിച്ചാണ് ചോദിക്കേണ്ടത്?", value="Nifty")
    user_q = st.chat_input("നിങ്ങളുടെ സംശയം ചോദിക്കൂ (eg: Can I buy now?)")

    if user_q:
        with st.spinner("ഡാറ്റ വിശകലനം ചെയ്യുന്നു..."):
            t_sym = get_ticker(stock_to_analyze)
            data = yf.download(t_sym, period="5d", interval="15m")
            if not data.empty:
                data = add_indicators(data)
                cp = data['Close'].iloc[-1]
                rsi_val = data['RSI'].iloc[-1]
                sma_val = data['SMA_20'].iloc[-1]
                
                # AI-ക്ക് കൂടുതൽ ഡാറ്റ നൽകുന്നു
                prompt = f"""
                Analysis for {stock_to_analyze}:
                Current Price: {cp}
                RSI (14): {rsi_val:.2f}
                SMA (20): {sma_val:.2f}
                
                User question: {user_q}
                
                Please provide a professional trading advice in Malayalam. 
                If RSI is below 30, suggest 'Potential Buy/Oversold'. 
                If RSI is above 70, suggest 'Potential Sell/Overbought'.
                Keep the answer clear for an intraday trader.
                """
                
                response = model.generate_content(prompt)
                with st.chat_message("assistant"):
                    st.write(f"**Live Analysis for {stock_to_analyze}**")
                    st.write(f"Price: ₹{cp:,.2f} | RSI: {rsi_val:.2f}")
                    st.write(response.text)
            else:
                st.error("ഡാറ്റ ലഭ്യമല്ല.")

# --- PAGE 3: EXPENSE MANAGER ---
elif page == "💰 Expense Manager":
    item = st.text_input("Item")
    amt = st.number_input("Amount")
    if st.button("Save"): st.success(f"Saved: {item}")
