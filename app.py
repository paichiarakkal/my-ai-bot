import streamlit as st
import yfinance as yf
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi Pro AI", page_icon="💎")

# നീ തന്ന പുതിയ API Key
API_KEY = "AIzaSyA6GffWmhFd3YVOWuh_dOYu1gHJ1UnekH8"

# AI സെറ്റപ്പ് - മോഡൽ പേര് തിരുത്തിയിട്ടുണ്ട്
try:
    genai.configure(api_key=API_KEY)
    # 'models/' എന്ന് ചേർത്തത് 404 എറർ ഒഴിവാക്കാൻ സഹായിക്കും
    model = genai.GenerativeModel('models/gemini-1.5-flash')
except Exception as e:
    st.error(f"Setup Error: {e}")

if "messages" not in st.session_state:
    st.session_state.messages = []

# സൈഡ്‌ബാർ മെനു
st.sidebar.title("💎 Paichi Menu")
menu = st.sidebar.radio("സേവനം:", ["🤖 AI Assistant", "📈 Market Rates"])

# ലൈവ് പ്രൈസ് ഫംഗ്ഷൻ
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
    
    # വോയ്‌സ് ഇൻപുട്ട്
    v_text = speech_to_text(language='en', start_prompt="🎤 സംസാരിക്കുക", key='v_inp')

    # പഴയ മെസ്സേജുകൾ കാണിക്കാൻ
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # ടെക്സ്റ്റ് ഇൻപുട്ട്
    prompt = st.chat_input("ചോദിക്കൂ...")
    if v_text: prompt = v_text 

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                # AI മറുപടി ചോദിക്കുന്നു
                res = model.generate_content(prompt)
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
            except Exception as e:
                # എറർ ഉണ്ടെങ്കിൽ അത് ഇവിടെ കാണിക്കും
                st.error(f"AI Error: {e}")
                st.info("നിങ്ങളുടെ API Key ആക്റ്റീവ് ആണെന്ന് ഉറപ്പുവരുത്തുക.")

# --- മാർക്കറ്റ് റേറ്റ്സ് സെക്ഷൻ ---
elif menu == "📈 Market Rates":
    st.header("Live Updates")
    oil = get_p("CL=F")
    if oil: st.metric("Crude Oil", f"₹{oil*91.5:.2f}")
    
    aed = get_p("AEDINR=X")
    if aed: st.metric("1 AED to INR", f"₹{aed:.2f}")
    
    nifty = get_p("^NSEI")
    if nifty: st.metric("Nifty 50", f"₹{nifty:,.2f}")
