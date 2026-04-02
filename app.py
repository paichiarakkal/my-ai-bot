import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Faisal Pro Hub", page_icon="💎", layout="wide")

# AI കീ സെറ്റപ്പ്
genai.configure(api_key="AIzaSyCYekGA3KTw-e7WFxR3_eMkIkVEA-_HczM")
model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. സൈഡ്‌ബാർ
st.sidebar.title("💎 Faisal Pro Menu")
menu = st.sidebar.radio("മെനു തിരഞ്ഞെടുക്കുക:", 
    ["📈 Paper Trading", "💰 Currency & Gold", "📊 Nifty 50 Live", "🤖 AI Assistant"])

# സഹായി - വില കൃത്യമായി എടുക്കാൻ
def get_live_price(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not data.empty:
            # എറർ ഒഴിവാക്കാൻ സീരീസ് ആണോ എന്ന് നോക്കുന്നു
            last_val = data['Close'].iloc[-1]
            if isinstance(last_val, pd.Series):
                return float(last_val.iloc[0])
            return float(last_val)
    except:
        return None
    return None

# --- സെക്ഷൻ 1: AI ASSISTANT (Voice + Text) ---
if menu == "🤖 AI Assistant":
    st.header("Ask Paichi AI 🎤")
    
    # വോയ്‌സ് ബട്ടൺ
    v_text = speech_to_text(language='en', start_prompt="🎤 സംസാരിക്കാൻ അമർത്തുക", stop_prompt="🛑 നിർത്തുക", key='voice')

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("ചോദിക്കൂ...")
    if v_text: prompt = v_text 

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                response = model.generate_content(prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except:
                st.error("AI കണക്ഷനിൽ ചെറിയ പ്രശ്നം. അല്പസമയം കഴിഞ്ഞ് ശ്രമിക്കൂ.")

# --- സെക്ഷൻ 2: CURRENCY & GOLD ---
elif menu == "💰 Currency & Gold":
    st.header("Live Rates (Exchange & Gold)")
    rate = get_live_price("AEDINR=X")
    if rate:
        val = st.number_input("Enter AED:", value=1.0)
        st.subheader(f"{val} AED = ₹{val * rate:.2f} INR")
    st.divider()
    st.write("🟡 **Gold Price (India)**")
    st.write("ഇന്നത്തെ സ്വർണ്ണവില (8g): ₹68,450 (Approx)")

# --- സെക്ഷൻ 3: TRADING ---
elif menu == "📈 Paper Trading":
    st.header("Live Trading Dashboard")
    p = get_live_price("CL=F")
    if p:
        st.metric("Crude Oil Price", f"₹{p*91.5:.2f}")
    else:
        st.error("ഡാറ്റ ലഭ്യമല്ല.")

# --- സെക്ഷൻ 4: NIFTY ---
elif menu == "📊 Nifty 50 Live":
    st.header("Nifty 50 Top Stocks")
    n_price = get_live_price("^NSEI")
    if n_price:
        st.metric("Nifty 50 Index", f"₹{n_price:,.2f}")
