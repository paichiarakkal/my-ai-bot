import streamlit as st
import yfinance as yf
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Paichi Pro AI", page_icon="💎")

# നീ തന്ന പുതിയ API Key
API_KEY = "AIzaSyA6GffWmhFd3YVOWuh_dOYu1gHJ1UnekH8"
genai.configure(api_key=API_KEY)

# 404 Error വരാതിരിക്കാൻ ഈ മോഡൽ പേര് ഉപയോഗിക്കാം
model = genai.GenerativeModel('gemini-1.5-flash-latest')

if "messages" not in st.session_state:
    st.session_state.messages = []

st.sidebar.title("💎 Menu")
menu = st.sidebar.radio("സേവനം:", ["🤖 AI Assistant", "📈 Market Rates"])

def get_p(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        return float(data['Close'].iloc[-1]) if not data.empty else None
    except: return None

if menu == "🤖 AI Assistant":
    st.header("Ask Paichi AI 🎤")
    v_text = speech_to_text(language='en', start_prompt="🎤 സംസാരിക്കുക", key='v_inp')
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("ചോദിക്കൂ...")
    if v_text: prompt = v_text 

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                res = model.generate_content(prompt)
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
            except Exception as e:
                # എറർ ഉണ്ടെങ്കിൽ അത് കൃത്യമായി അറിയാൻ
                st.error(f"AI Error: {e}")

elif menu == "📈 Market Rates":
    st.header("Live Updates")
    oil = get_p("CL=F")
    if oil: st.metric("Crude Oil", f"₹{oil*91.5:.2f}")
    aed = get_p("AEDINR=X")
    if aed: st.metric("1 AED to INR", f"₹{aed:.2f}")
