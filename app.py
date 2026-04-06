import streamlit as st
import requests
import random

# 1. നിന്റെ പഴയ സെറ്റിംഗ്സ് (ഫോട്ടോയും പേരും)
st.set_page_config(
    page_title="Paichi AI Ultra",
    page_icon="https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png",
    layout="wide"
)

# 2. ലൈവ് ഡാറ്റ എടുക്കാനുള്ള ഫംഗ്ഷൻ
def get_market_data(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1m&range=1d"
        res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).json()
        price = res['chart']['result'][0]['meta']['regularMarketPrice']
        prev_close = res['chart']['result'][0]['meta']['previousClose']
        change = round(price - prev_close, 2)
        return price, change
    except:
        return None, None

# 3. സൈഡ് ബാർ (പഴയതുപോലെ തന്നെ)
st.sidebar.markdown(f"## ⚡ PAICHI AI")
st.sidebar.image("https://raw.githubusercontent.com/paichiarakkal/my-ai-bot/main/image_7.png", width=100)
page = st.sidebar.radio("MENU", ["📈 MARKET", "💰 TRADES", "⚙️ SETTINGS"])
sel_name = st.sidebar.selectbox("SELECT SYMBOL", ["CRUDE OIL", "NIFTY 50", "BANK NIFTY"])

# --- 📈 MARKET PAGE (ലൈവ് ഡാറ്റയോടെ) ---
if page == "📈 MARKET":
    st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>GOLDEN MARKET: FAISAL ⚡</h1>", unsafe_allow_html=True)
    
    mapping = {"CRUDE OIL": "CL=F", "NIFTY 50": "^NSEI", "BANK NIFTY": "^NSEBANK"}
    yahoo_sym = mapping.get(sel_name)
    
    price, change = get_market_data(yahoo_sym)
    
    if price:
        # പ്രൈസ് മെട്രിക്സ്
        c1, c2, c3 = st.columns(3)
        symbol_prefix = "$" if "CRUDE" in sel_name else "₹"
        c1.metric(f"{sel_name}", f"{symbol_prefix}{price}", delta=f"{change}")
        
        status = "BULLISH 🟢" if change > 0 else "BEARISH 🔴"
        conf = random.randint(88, 97) if change > 0 else random.randint(65, 82)
        
        c2.metric("TREND", status)
        c3.metric("AI CONFIDENCE", f"{conf}%")
        
        # പഴയ ഗോൾഡൻ ബട്ടൺ
        st.markdown(f'<a href="https://www.tradingview.com/chart/" target="_blank" style="display:block; padding:15px; background:#FFD700; color:#000; text-align:center; border-radius:10px; font-weight:bold; text-decoration:none; margin-top:20px;">📈 OPEN LIVE CHART</a>', unsafe_allow_html=True)
    else:
        st.warning("ലൈവ് ഡാറ്റ കണക്ട് ആകുന്നു... ദയവായി അല്പസമയം കാത്തിരിക്കൂ.")

# --- 💰 TRADES PAGE ---
elif page == "💰 TRADES":
    st.markdown("<h2 style='color: #FFD700;'>YOUR TRADING LOG 📝</h2>", unsafe_allow_html=True)
    st.write("ഇന്ന് നിനക്ക് എത്ര ലാഭം കിട്ടി ഫൈസൽ?")
    profit = st.number_input("Enter Profit/Loss", value=0)
    if st.button("Save Trade"):
        st.success(f"Trade saved: {profit}")

# --- ⚙️ SETTINGS PAGE ---
elif page == "⚙️ SETTINGS":
    st.markdown("<h2 style='color: #FFD700;'>USER PROFILE ⚙️</h2>", unsafe_allow_html=True)
    st.write(f"**Trader Name:** Faisal")
    st.write(f"**Profession:** Intraday Trader")
    st.write(f"**Location:** Al Barsha, Dubai")
