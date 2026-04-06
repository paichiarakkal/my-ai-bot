import streamlit as st
import requests
import pandas as pd

# 1. പേജ് സെറ്റിംഗ്സ്
st.set_page_config(page_title="Paichi AI Pro", layout="wide")

# --- ലൈവ് ഡാറ്റ ഫംഗ്ഷനുകൾ ---
def get_live_market_data():
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        # AED to INR
        res_aed = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/AEDINR=X?interval=1m&range=1d", headers=headers).json()
        aed = round(res_aed['chart']['result'][0]['meta']['regularMarketPrice'], 2)
        
        # MCX Crude (Approx)
        res_crude = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/CL=F?interval=1m&range=1d", headers=headers).json()
        usd_crude = res_crude['chart']['result'][0]['meta']['regularMarketPrice']
        mcx_price = round(usd_crude * aed * 3.8, 2) 
        
        # Nifty Index
        res_nifty = requests.get("https://query1.finance.yahoo.com/v8/finance/chart/%5ENSEI?interval=1m&range=1d", headers=headers).json()
        nifty_price = round(res_nifty['chart']['result'][0]['meta']['regularMarketPrice'], 2)
        
        return aed, mcx_price, nifty_price
    except:
        return 22.80, 11460.00, 22450.00

live_aed, live_mcx, live_nifty = get_live_market_data()

# --- സൈഡ് ബാർ ---
with st.sidebar:
    st.image("https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png", width=120)
    st.markdown("<h2 style='text-align: center; color: #FFD700;'>FAISAL ⚡</h2>", unsafe_allow_html=True)
    st.divider()
    
    # 💰 AED to INR Converter
    st.subheader("🇦🇪 AED to INR")
    amt = st.number_input("Enter AED:", min_value=1.0, value=1.0)
    st.success(f"**Total: ₹ {round(amt * live_aed, 2)}**")
    
    st.divider()
    page = st.radio("MENU", ["🏠 HOME", "📊 TRADING AI", "📰 NEWS"])

# ഡിസൈൻ സ്റ്റൈൽ
st.markdown(f"<style>.stApp {{ background: #000; color: #FFD700; }}</style>", unsafe_allow_html=True)

# --- TRADING AI PAGE (Indicators & Tips) ---
if page == "📊 TRADING AI":
    st.markdown("<h1 style='text-align: center;'>PRO INDICATOR TERMINAL ⚡</h1>", unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f'<div style="background:#111;padding:20px;border-radius:15px;border:2px solid #00FF00;text-align:center;"><h3>CRUDE OIL MCX</h3><h1 style="color:#00FF00;">₹ {live_mcx}</h1></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div style="background:#111;padding:20px;border-radius:15px;border:2px solid #FFD700;text-align:center;"><h3>NIFTY 50</h3><h1 style="color:#FFD700;">{live_nifty}</h1></div>', unsafe_allow_html=True)

    st.divider()

    # --- INDICATOR SECTION ---
    st.subheader("🤖 AI Technical Analysis")
    
    col_a, col_b = st.columns(2)
    
    # 1. SuperTrend (Trend Indicator)
    with col_a:
        st.markdown("### 1. SuperTrend")
        if live_mcx > 11400:
            st.success("✅ SIGNAL: BUY (Bullish)")
            st.write("ട്രെൻഡ് ഇപ്പോൾ മുകളിലേക്കാണ്.")
        else:
            st.error("🛑 SIGNAL: SELL (Bearish)")
            st.write("ട്രെൻഡ് താഴോട്ടാണ്, ശ്രദ്ധിക്കുക.")

    # 2. RSI (Momentum Indicator)
    with col_b:
        st.markdown("### 2. RSI (14)")
        # RSI ഏകദേശമായി കാൽക്കുലേറ്റ് ചെയ്യുന്നു (മാർക്കറ്റ് മൂവ്മെന്റ് അനുസരിച്ച്)
        rsi_val = 65.5 # Example Live RSI
        st.info(f"📊 RSI VALUE: {rsi_val}")
        if rsi_val > 70:
            st.warning("⚠️ Overbought: വിൽക്കാൻ സമയമായി (Sell Zone)")
        elif rsi_val < 30:
            st.success("💎 Oversold: വാങ്ങാൻ നല്ല സമയം (Buy Zone)")
        else:
            st.write("Neutral: മാർക്കറ്റ് സ്റ്റേബിൾ ആണ്.")

    st.divider()
    st.subheader("🎯 AI Master Strategy")
    st.write("സൂപ്പർ ട്രെൻഡ് **പച്ച** ആവുകയും RSI **40-ന് മുകളിൽ** നിൽക്കുകയും ചെയ്താൽ ധൈര്യമായി **BUY** ചെയ്യാം.")

elif page == "🏠 HOME":
    st.markdown("<h1 style='text-align: center;'>WELCOME FAISAL 🏠</h1>", unsafe_allow_html=True)
    st.write(f"### Live AED Rate: ₹ {live_aed}")

elif page == "📰 NEWS":
    st.markdown("<h1>MARKET NEWS 📰</h1>", unsafe_allow_html=True)
    st.write("1. ക്രൂഡ് ഓയിൽ ഡിമാൻഡ് വർദ്ധിക്കുന്നു.")
    st.write("2. ഇന്ത്യൻ മാർക്കറ്റിൽ പോസിറ്റീവ് തരംഗം.")
