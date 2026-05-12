import streamlit as st, pandas as pd, requests, yfinance as yf, random, re, urllib.parse, threading
from datetime import datetime
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh

# --- 1. CONFIG ---
CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-/pub?gid=1583146028&single=true&output=csv"
FORM_API = "https://docs.google.com/forms/d/e/1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
USERS = {"faisal": "faisal147", "shabana": "shabana123", "admin": "paichi786"}

st.set_page_config(page_title="PAICHI v8.0", layout="wide")
st_autorefresh(interval=60000, key="refresh")

# --- 2. STYLE ---
st.markdown("<style>.stApp{background:linear-gradient(135deg,#2D0844,#4B0082,#1A0521);color:#fff;}[data-testid='stSidebar']{background:rgba(0,0,0,0.85)!important;}.balance-banner{background:rgba(255,255,255,0.05);padding:20px;border-radius:15px;border-left:10px solid #FFD700;text-align:center;}.purple-box{background:rgba(255,255,255,0.05);padding:15px;border-radius:15px;border:1px solid #FFD700;text-align:center;margin-bottom:10px;}.stDataFrame{background:white;border-radius:10px;color:black;}</style>", unsafe_allow_html=True)

# --- 3. ENGINES ---
def api_call(url, data=None):
    try:
        if data: threading.Thread(target=lambda: requests.post(url, data=data)).start()
        else: return requests.get(url, timeout=10)
    except: pass

def get_data():
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1,999)}")
        df.columns = df.columns.str.strip()
        return df
    except: return pd.DataFrame()

if 'auth' not in st.session_state: st.session_state.auth = False

# --- 4. MAIN ---
if not st.session_state.auth:
    u = st.text_input("User").lower()
    p = st.text_input("Pass", type="password")
    if st.button("LOGIN") and USERS.get(u) == p:
        st.session_state.auth, st.session_state.user = True, u
        st.rerun()
else:
    df = get_data()
    bal = pd.to_numeric(df['Credit'], errors='coerce').sum() - pd.to_numeric(df['Debit'], errors='coerce').sum()
    st.markdown(f'<div class="balance-banner"><h3>Available Balance: ₹{bal:,.2f}</h3></div>', unsafe_allow_html=True)

    menu = ["💰 Add", "🔍 History"] if st.session_state.user == "shabana" else ["📊 Advisor", "💰 Add", "🔍 History", "🤝 Debt"]
    page = st.sidebar.radio("Menu", menu)

    if page == "📊 Advisor":
        for n, s in {"Nifty": "^NSEI", "Crude": "CL=F"}.items():
            px = yf.Ticker(s).history(period="1d")['Close'].iloc[-1]
            if n == "Crude": px *= 96 
            st.markdown(f'<div class="purple-box"><h2>{n}</h2><h1>₹{px:,.0f}</h1></div>', unsafe_allow_html=True)

    elif page == "💰 Add":
        v = speech_to_text(language='ml', key='v8')
        with st.form("f", clear_on_submit=True):
            it, am = st.text_input("Item", value=v if v else ""), st.text_input("Amount")
            ty = st.radio("Type", ["Debit", "Credit"], horizontal=True)
            if st.form_submit_button("SAVE"):
                d, c = (am, 0) if ty == "Debit" else (0, am)
                payload = {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"[{st.session_state.user.title()}] {it}", "entry.1460982454": d, "entry.1221658767": c}
                api_call(FORM_API, payload)
                st.success("Saved!")

    elif page == "🔍 History":
        def style_h(x):
            s = pd.DataFrame('', index=x.index, columns=x.columns)
            s.loc[pd.to_numeric(x['Debit'], errors='coerce') > 0, 'Debit'] = 'background-color:#ffe6e6;color:red;font-weight:bold;'
            s.loc[pd.to_numeric(x['Credit'], errors='coerce') > 0, 'Credit'] = 'background-color:#e6ffed;color:green;font-weight:bold;'
            return s
        st.dataframe(df.iloc[::-1].style.apply(style_h, axis=None).format({'Debit': "{:.2f}", 'Credit': "{:.2f}"}, na_rep=""), use_container_width=True)

    elif page == "🤝 Debt":
        with st.form("d"):
            n, a, t = st.text_input("Name"), st.number_input("Amt"), st.selectbox("Type", ["Borrowed", "Lent"])
            if st.form_submit_button("SAVE"):
                d, c = (0, a) if "Borrowed" in t else (a, 0)
                api_call(FORM_API, {"entry.1044099436": datetime.now().strftime("%Y-%m-%d"), "entry.2013476337": f"DEBT: {t}-{n}", "entry.1460982454": d, "entry.1221658767": c})
                st.success("Saved!")

    if st.sidebar.button("Logout"): st.session_state.auth = False; st.rerun()
