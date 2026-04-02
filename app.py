import streamlit as st
import yfinance as yf
import google.generativeai as genai
from streamlit_mic_recorder import speech_to_text

st.set_page_config(page_title="Paichi Pro AI", page_icon="💎")

# പുതിയ API Key
API_KEY = "AIzaSyA6GffWmhFd3YVOWuh_dOYu1gHJ1UnekH8"
genai.configure(api_key=API_KEY)

# മോഡൽ സെറ്റ് ചെയ്യാൻ ഒരു ഫംഗ്ഷൻ (404 ഒഴിവാക്കാൻ)
def get_model():
    # ആദ്യം പുതിയ മോഡൽ നോക്കും, അത് കിട്ടിയില്ലെങ്കിൽ പഴയതിലേക്ക് മാറും
    for m_name in ['gemini-1.5-flash', 'gemini-pro', 'models/gemini-pro']:
        try:
            m = genai.GenerativeModel(m_name)
            # ഒന്ന് ചെക്ക് ചെയ്യുന്നു
            m.generate_content("test", generation_config={"max_output_tokens": 1})
            return m
        except:
            continue
    return None

model = get_model()

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
            if model:
                try:
                    res = model.generate_content(prompt)
                    st.markdown(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                except Exception as e:
                    st.error(f"AI Error: {e}")
            else:
                st.error("AI മോഡലുകൾ ഒന്നും ഇപ്പോൾ ലഭ്യമല്ല. API Key ശ്രദ്ധിക്കുക.")

elif menu == "📈 Market Rates":
    st.header("Live Updates")
    oil = get_p("CL=F")
    if oil: st.metric("Crude Oil", f"₹{oil*91.5:.2f}")
    aed = get_p("AEDINR=X")
    if aed: st.metric("1 AED to INR", f"₹{aed:.2f}")
