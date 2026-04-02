import streamlit as st
import yfinance as yf
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

# 1. ആപ്പ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi Pro AI", page_icon="💎")

# നീ ഇപ്പോൾ തന്ന പുതിയ API Key
API_KEY = "AIzaSyA6GffWmhFd3YVOWuh_dOYu1gHJ1UnekH8"

# AI സെറ്റപ്പ്
try:
    genai.configure(api_key=API_KEY)
    # ഏറ്റവും പുതിയ ഫ്ലാഷ് മോഡൽ ഉപയോഗിക്കുന്നു
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"AI Setup Error: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("💎 Paichi Menu")
menu = st.sidebar.radio("തിരഞ്ഞെടുക്കുക:", ["🤖 AI Assistant", "📈 Market Rates"])

# ലൈവ് പ്രൈസ് എടുക്കാനുള്ള ഫംഗ്ഷൻ
def get_p(ticker):
    try:
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not data.empty:
            return float(data['Close'].iloc[-1])
    except: return None
    return None

# --- AI അസിസ്റ്റന്റ് സെക്ഷൻ ---
if menu == "🤖 AI Assistant":
    st.header("Ask Paichi AI 🎤")
    
    # വോയ്‌സ് ബട്ടൺ
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
                # എറർ ഉണ്ടെങ്കിൽ അത് കൃത്യമായി കാണിക്കും
                st.error(f"AI Error: {e}")

# --- മാർക്കറ്റ് റേറ്റ്സ് സെക്ഷൻ ---
elif menu == "📈 Market Rates":
    st.header("Live Updates")
    oil = get_p("CL=F")
    if oil: st.metric("Crude Oil (MCX)", f"₹{oil*91.5:.2f}")
    aed = get_p("AEDINR=X")
    if aed: st.metric("1 AED to INR", f"₹{aed:.2f}")
    nifty = get_p("^NSEI")
    if nifty: st.metric("Nifty 50", f"₹{nifty:,.2f}")
