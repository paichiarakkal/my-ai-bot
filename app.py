import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi Pro AI Hub", page_icon="💎", layout="wide")

# പുതിയ API Key ഇവിടെ സെറ്റ് ചെയ്തു
NEW_API_KEY = "AIzaSyCRgcDHdqNYhVvjXBkQykqzvrzBYpgw8LA"

try:
    genai.configure(api_key=NEW_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Setup Error: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. സൈഡ്‌ബാർ മെനു
st.sidebar.title("💎 Paichi Menu")
menu = st.sidebar.radio("തിരഞ്ഞെടുക്കുക:", ["🤖 AI Assistant", "📈 Live Trading & Rates"])

# ലൈവ് പ്രൈസ് എടുക്കാനുള്ള എളുപ്പവഴി
def get_p(ticker):
    try:
        # TypeError ഒഴിവാക്കാൻ fast_info ഉപയോഗിക്കുന്നു
        val = yf.Ticker(ticker).fast_info['last_price']
        return val
    except: return None

# --- സെക്ഷൻ 1: AI ASSISTANT (Voice & Text) ---
if menu == "🤖 AI Assistant":
    st.header("Ask Paichi AI 🎤")
    
    # വോയ്‌സ് ബട്ടൺ
    v_text = speech_to_text(language='en', start_prompt="🎤 സംസാരിക്കാൻ അമർത്തുക", stop_prompt="🛑 നിർത്തുക", key='voice_input')

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    p = st.chat_input("ചോദിക്കൂ...")
    if v_text: p = v_text # വോയ്‌സ് ഉണ്ടെങ്കിൽ അത് എടുക്കും

    if p:
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            try:
                res = model.generate_content(p)
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
            except:
                st.error("API Key ആക്റ്റീവ് ആയിട്ടില്ല. അല്പസമയം കഴിഞ്ഞ് ശ്രമിക്കൂ.")

# --- സെക്ഷൻ 2: TRADING & RATES ---
elif menu == "📈 Live Trading & Rates":
    st.header("Real-Time Market Data")
    
    c1, c2 = st.columns(2)
    
    # കറൻസി റേറ്റ്
    aed = get_p("AEDINR=X")
    if aed:
        c1.metric("1 AED to INR", f"₹{aed:.2f}")
    
    # ക്രൂഡ് ഓയിൽ
    oil = get_p("CL=F")
    if oil:
        c2.metric("Crude Oil (Price)", f"₹{oil*91.5:.2f}")

    # നിഫ്റ്റി
    nifty = get_p("^NSEI")
    if nifty:
        st.subheader(f"📊 Nifty 50: ₹{nifty:,.2f}")
