import streamlit as st
import yfinance as yf
import pandas as pd
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Faisal Pro Multi-Tool AI")

# AI കീ (ഇതൊന്ന് ചെക്ക് ചെയ്യുക)
API_KEY = "AIzaSyCYekGA3KTw-e7WFxR3_eMkIkVEA-_HczM"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

if "messages" not in st.session_state:
    st.session_state.messages = []

# സൈഡ്‌ബാർ
st.sidebar.title("💎 Menu")
menu = st.sidebar.radio("സേവനം:", ["🤖 AI Assistant", "📈 Trading & Rates"])

# ലൈവ് പ്രൈസ് എടുക്കാനുള്ള എളുപ്പവഴി
def get_p(ticker):
    try:
        d = yf.Ticker(ticker).fast_info['last_price']
        return d
    except: return None

# --- AI ഭാഗം ---
if menu == "🤖 AI Assistant":
    st.header("Ask Paichi AI 🎤")
    v_text = speech_to_text(language='en', start_prompt="🎤 സംസാരിക്കുക", key='voice')
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    p = st.chat_input("ചോദിക്കൂ...")
    if v_text: p = v_text

    if p:
        st.session_state.messages.append({"role": "user", "content": p})
        with st.chat_message("user"): st.markdown(p)
        with st.chat_message("assistant"):
            try:
                res = model.generate_content(p)
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
            except: st.error("API Key മാറ്റി നോക്കേണ്ടി വരും.")

# --- ട്രേഡിംഗ് & റേറ്റ്സ് ---
elif menu == "📈 Trading & Rates":
    st.header("Live Rates")
    
    # കറൻസി
    aed_rate = get_p("AEDINR=X")
    if aed_rate:
        st.write(f"1.0 AED = ₹{aed_rate:.2f} INR")
    
    # ക്രൂഡ് ഓയിൽ
    crude = get_p("CL=F")
    if crude:
        st.write(f"Crude Oil Price: ₹{crude*91.5:.2f}")
