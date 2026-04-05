import streamlit as st
import requests
import pandas as pd
import datetime
import os
from streamlit_autorefresh import st_autorefresh

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi Multi-Theme Pro", layout="wide")

# --- സൈഡ് ബാർ നാവിഗേഷൻ ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #000;'>🚀 Paichi Pro</h1>", unsafe_allow_html=True)
    page = st.radio("പേജ് തിരഞ്ഞെടുക്കുക:", ["🏠 HOME", "📈 MARKET", "📝 JOURNAL", "📊 DASHBOARD"])
    st.divider()
    
    # മാർക്കറ്റ് പേജിൽ മാത്രം ചാർട്ട് സെലക്ഷൻ
    if page == "📈 MARKET":
        st.subheader("🎯 Select Symbol")
        if st.button("📊 NIFTY 50"): st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=NSE:NIFTY", "NIFTY 50"
        if st.button("🏦 BANK NIFTY"): st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=NSE:BANKNIFTY", "BANK NIFTY"
        if st.button("🛢️ CRUDE OIL"): st.session_state.url, st.session_state.name = "https://in.tradingview.com/chart/?symbol=MCX:CRUDEOIL1!", "CRUDE OIL"
        
        if 'url' in st.session_state:
            st.markdown(f'<a href="{st.session_state.url}" target="_blank" style="display: block; width: 100%; padding: 12px; background: #000; color: #FFD700; text-align: center; border-radius: 10px; text-decoration: none; font-weight: bold; border: 2px solid #FFD700;">📈 OPEN {st.session_state.name}</a>', unsafe_allow_html=True)

# --- ഡൈനാമിക് കളർ തീം സെലക്ഷൻ ---
if page == "🏠 HOME":
    # സിൽവർ തീം
    bg_color = "linear-gradient(135deg, #C0C0C0, #E8E8E8, #808080)"
    text_color = "#000"
elif page == "📈 MARKET":
    # ഗോൾഡൻ തീം
    bg_color = "linear-gradient(135deg, #BF953F, #FCF6BA, #B38728, #AA771C)"
    text_color = "#000"
elif page == "📝 JOURNAL":
    # പ്ലാറ്റിനം തീം
    bg_color = "linear-gradient(135deg, #E5E4E2, #F5F5F5, #BCC6CC)"
    text_color = "#000"
else:
    # എനിക്ക് ഇഷ്ടപ്പെട്ട റോയൽ ബ്ലൂ & ഗോൾഡ്
    bg_color = "linear-gradient(135deg, #002366, #0047AB, #BF953F)"
    text_color = "#FFF"

st.markdown(f"""
<style>
    .stApp {{ background: {bg_color} !important; color: {text_color} !important; }}
    section[data-testid="stSidebar"] {{ background: #C0C0C0 !important; }}
    .main-title {{ font-size: 35px; font-weight: 800; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
</style>
""", unsafe_allow_html=True)

# --- പേജ് കണ്ടന്റ് ---

if page == "🏠 HOME":
    st.markdown("<p class='main-title'>SILVER HOME 🏠</p>", unsafe_allow_html=True)
    my_photo_url = "https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png" 
    st.markdown(f'<div style="text-align: center;"><img src="{my_photo_url}" style="width: 200px; border-radius: 50%; border: 5px solid #808080; box-shadow: 0px 10px 20px rgba(0,0,0,0.2);"></div>', unsafe_allow_html=True)
    st.markdown("### 🧠 Trading Rules")
    st.info("1. ക്ഷമയാണ് പ്രധാനം.\n2. സ്റ്റോപ്പ് ലോസ് മറക്കരുത്.\n3. ഓവർ ട്രേഡിംഗ് ഒഴിവാക്കുക.")

elif page == "📈 MARKET":
    st.markdown(f"<p class='main-title'>GOLDEN MARKET: {st.session_state.get('name', 'NIFTY 50')} ⚡</p>", unsafe_allow_html=True)
    st.markdown("<div style='text-align: center; font-size: 100px;'>📈</div>", unsafe_allow_html=True)

elif page == "📝 JOURNAL":
    st.markdown("<p class='main-title'>PLATINUM JOURNAL 📝</p>", unsafe_allow_html=True)
    # ജേണൽ ഫോം ഇവിടെ വരും (പഴയ കോഡ് ഉപയോഗിക്കാം)
    st.write("നിന്റെ ട്രേഡുകൾ ഇവിടെ സേവ് ചെയ്യാം...")

elif page == "📊 DASHBOARD":
    st.markdown("<p class='main-title'>ROYAL DASHBOARD 📊</p>", unsafe_allow_html=True)
    st.metric("Total Profit", "₹ 2,350", delta="15%")
    st.write("നിന്റെ പെർഫോമൻസ് ഗ്രാഫ് ഇവിടെ വരും.")
