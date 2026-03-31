import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import google.generativeai as genai

# 1. Gemini AI സെറ്റപ്പ് - നിന്റെ API Key ഇവിടെ നൽകി
genai.configure(api_key="AIzaSyCamT29LeVv_9031swUtfXQcS3FLPemi3A")
model = genai.GenerativeModel('gemini-pro')

st.set_page_config(page_title="FTB SMART TERMINAL", page_icon="🤖", layout="wide")

# --- സൈഡ്‌ബാറിലെ വിവരങ്ങൾ ---
st.sidebar.markdown("## 📊 FTB SETTINGS")
user_input = st.sidebar.text_input("Search Stock/Index", value="Nifty")

def get_ticker(name):
    name = name.lower().strip()
    mapping = {"nifty": "^NSEI", "bank nifty": "^NSEBANK", "crude": "CL=F", "gold": "GC=F"}
    if name in mapping: return mapping[name]
    if name.isalpha(): return f"{name.upper()}.NS"
    return name.upper()

search_ticker = get_ticker(user_input)
chart_int = st.sidebar.selectbox("Interval", ["1m", "5m", "15m"], index=0)

# --- മെയിൻ ബോഡി ---
st.markdown("<h1 style='color: #00E676;'>📊 FTB AI TERMINAL</h1>", unsafe_allow_html=True)
tab1, tab2 = st.tabs(["📈 LIVE CHART", "🤖 FTB AI CHAT"])

with tab1:
    try:
        df = yf.Ticker(search_ticker).history(period="1d", interval=chart_int)
        if not df.empty:
            st.subheader(f"LIVE: {user_input.upper()}")
            fig = go.Figure(data=[go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'])])
            fig.update_layout(height=500, template='plotly_dark', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        else: st.error("Stock not found.")
    except: st.error("Connection Error.")

with tab2:
    st.subheader("💬 Ask Anything to Gemini")
    if "messages" not in st.session_state: st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("നിന്റെ സംശയങ്ങൾ ഇവിടെ ചോദിക്കൂ..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        with st.chat_message("assistant"):
            try:
                # Gemini മറുപടി നൽകുന്നു
                full_prompt = f"You are a helpful Malayalam and English speaking trading expert for Faisal. Answer this: {prompt}"
                response = model.generate_content(full_prompt)
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error("AI response error. Please check your API key.")
