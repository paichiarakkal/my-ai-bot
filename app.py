import streamlit as st
import requests
import pandas as pd
import datetime
import os

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Ultra Pro", layout="wide")

# സൈഡ് ബാറിൽ നിന്റെ ഫോട്ടോയും റേയ്റ്റും
with st.sidebar:
    photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png"
    st.image(photo_url, width=120)
    st.markdown("<h2 style='color: #FFD700; text-align: center;'>FAISAL ⚡</h2>", unsafe_allow_html=True)
    
    st.divider()
    page = st.radio("MENU", ["📈 MARKET", "📝 JOURNAL", "💬 CHAT"])
    st.divider()

    # 🎯 ഇൻഡക്സ് സെലക്ഷൻ
    st.subheader("🎯 Select Symbol")
    category = st.selectbox("Category", ["Commodity (Crude)", "Index (Nifty/Sensex)"])
    
    if category == "Commodity (Crude)":
        sym_map = {"CRUDE OIL": "MCX:CRUDEOIL1!", "SILVER": "MCX:SILVER1!"}
        default_interval = "5"
    else:
        sym_map = {"NIFTY 50": "NSE:NIFTY", "BANK NIFTY": "NSE:BANKNIFTY", "SENSEX": "BSE:SENSEX"}
        # സെൻസെക്സിന് ചിലപ്പോൾ ചെറിയ ടൈംഫ്രെയിം കിട്ടില്ല, അതുകൊണ്ട് 'D' (Daily) വെക്കുന്നു
        default_interval = "D" 

    sel_name = st.selectbox("Choose Symbol", list(sym_map.keys()))
    selected_symbol = sym_map[sel_name]

# ഗോൾഡൻ & ബ്ലാക്ക് തീം
st.markdown(f"<style>.stApp {{ background: #000; color: #FFD700 !important; }}</style>", unsafe_allow_html=True)

# --- MARKET PAGE ---
if page == "📈 MARKET":
    st.markdown(f"<h1 style='text-align: center;'>LIVE: {sel_name} ⚡</h1>", unsafe_allow_html=True)
    
    # ലൈവ് ചാർട്ട് വിഡ്ജറ്റ് (നിനക്ക് വേണ്ട ആ ഒറിജിനൽ വില ഇവിടെ വരും)
    chart_html = f"""
    <div style="height:620px; border: 2px solid #FFD700; border-radius: 10px; overflow: hidden;">
        <iframe src="https://s.tradingview.com/widgetembed/?symbol={selected_symbol}&interval={default_interval}&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=f1f3f6&theme=dark&style=1&timezone=Asia%2FKolkata&studies=SuperTrend%40tv-basicstudies" width="100%" height="620" frameborder="0"></iframe>
    </div>
    """
    st.components.v1.html(chart_html, height=630)
    
    # സിഗ്നൽ ടിപ്‌സ്
    st.markdown("---")
    c1, c2 = st.columns(2)
    c1.success("✅ SUPERTREND പച്ചയാണെങ്കിൽ BUY നോക്കുക.")
    c2.error("🛑 SUPERTREND ചുവപ്പാണെങ്കിൽ SELL നോക്കുക.")

# --- JOURNAL ---
elif page == "📝 JOURNAL":
    st.markdown("<h1 style='text-align: center;'>TRADE JOURNAL 📝</h1>", unsafe_allow_html=True)
    st.write("നിന്റെ ട്രേഡുകൾ ഇവിടെ രേഖപ്പെടുത്താം ഫൈസൽ.")

# --- CHAT ---
elif page == "💬 CHAT":
    st.markdown("<h1 style='text-align: center;'>WHATSAPP CHAT 💬</h1>", unsafe_allow_html=True)
    st.write("വാട്സാപ്പിലേക്ക് മെസേജ് അയക്കാൻ ഇവിടെ സൗകര്യമുണ്ട്.")
