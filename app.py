import streamlit as st, pandas as pd, requests, yfinance as yf, random, re, urllib.parse, threading
from datetime import datetime
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
WA_PHONE, WA_KEY = "971551347989", "7463030"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI GOLD v8.0", layout="wide")
st_autorefresh(interval=60000, key="refresh")

# --- 2. STYLE ---
st.markdown("<style>.stApp{background:linear-gradient(135deg,#2D0844,#4B0082,#1A0521);color:#fff;}[data-testid='stSidebar']{background:rgba(0,0,0,0.85)!important;}.balance-banner{background:rgba(255,255,255,0.05);padding:20px;border-radius:15px;border-left:10px solid #FFD700;text-align:center;}.purple-box{background:rgba(255,255,255,0.05);padding:15px;border-radius:15px;border:1px solid #FFD700;text-align:center;margin-bottom:10px;}.stDataFrame{background:white;border-radius:10px;color:black;}</style>", unsafe_allow_html=True)

# --- 3. FUNCTIONS ---
def run_api(url, data=None):
    try: threading.Thread(target=lambda: requests.post(url, data=data)).start()
    except: pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 4. MAIN APP ---
if not st.session_state.auth:
    st.title("🔐 PAICHI LOGIN")
    u, p = st.text_input("User").lower(), st.text_input("Pass", type="password")
    if st.button("LOGIN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
else:
    df = get_data()
    d_sum = pd.to_numeric(df['Debit'], errors='coerce').fillna(0).sum()
    c_sum = pd.to_numeric(df['Credit'], errors='coerce').fillna(0).sum()
    st.markdown(f'<div class="balance-banner"><h3>Balance: ₹{c_sum - d_sum:,.2f}</h3></div>', unsafe_allow_html=True)

    menu = ["💰 Add", "🔍 History"] if st.session_state.user == "shabana" else ["📊 Advisor", "🏠 Dashboard", "💰 Add", "🔍 History", "🤝 Debt"]
    page = st.sidebar.radio("Menu", menu)

    if page == "📊 Advisor":
        for n, s in {"Nifty": "^NSEI", "Crude": "CL=F"}.items():
            try:
                val = yf.Ticker(s).history(period="1d")['Close'].iloc[-1]
                if n == "Crude": val *= 96
                st.markdown(f'<div class="purple-box"><h3>{n}</h3><h1 style="color:#FFD700">₹{val:,.0f}</h1></div>', unsafe_allow_html=True)
            except: pass

    elif page == "🏠 Dashboard":
        st.markdown(f'<div class="purple-box"><h2 style="color:#00FF00">IN: ₹{c_sum:,.2f}</h2><h2 style="color:#FF3131">OUT: ₹{d_sum:,.2f}</h2></div>', unsafe_allow_html=True)

    elif page == "💰 Add":
        v = speech_to_text(language='ml', key='v8')
        with st.form("f", clear_on_submit=True):
            it, am = st.text_input("Item", value=v if v else ""), st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user.title()}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                run_api(FORM_API, payload)
                wa_msg = f"✅ *Paichi Entry*\n📝 {it}\n💰 ₹{am}\n👤 {st.session_state.user}"
                run_api(f"https://api.callmebot.com/whatsapp.php?phone={WA_PHONE}&text={urllib.parse.quote(wa_msg)}&apikey={WA_KEY}")
                st.success("Saved!")

    elif page == "🔍 History":
        def style_h(x):
            s = pd.DataFrame('', index=x.index, columns=x.columns)
            d = pd.to_numeric(x['Debit'], errors='coerce').fillna(0)
            c = pd.to_numeric(x['Credit'], errors='coerce').fillna(0)
            s.loc[d > 0, 'Debit'] = 'background-color:#ffe6e6;color:red;font-weight:bold;'
            s.loc[c > 0, 'Credit'] = 'background-color:#e6ffed;color:green;font-weight:bold;'
            return s
        st.dataframe(df.iloc[::-1].style.apply(style_h, axis=None).format({'Debit': "{:.2f}", 'Credit': "{:.2f}"}, na_rep=""), use_container_width=True)

    elif page == "🤝 Debt":
        with st.form("d"):
            n, a, t = st.text_input("Name"), st.number_input("Amt"), st.selectbox("Type", ["Borrowed", "Lent"])
            if st.form_submit_button("SAVE"):
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                run_api(FORM_API, {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"DEBT: {t}-{n}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Debt Saved!")

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
