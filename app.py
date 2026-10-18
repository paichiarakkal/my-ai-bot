# ============================================
# PAICHI EXPENSES v4.0 — Refactored & Fixed
# ============================================

import streamlit as st
import pandas as pd
import requests
import random
import re
import urllib.parse
import threading
from datetime import datetime
from io import BytesIO

import plotly.express as px
from streamlit_mic_recorder import speech_to_text
from streamlit_autorefresh import st_autorefresh
from streamlit_calendar import calendar
from fpdf import FPDF


# ============================================
# CONFIG
# ============================================
CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vRccfZch3jSdHqrScpqsR_j3FSd70NbELC1j6_nPi-MQXdrhVr3BPcKoI1nub4mQql727pQRPWYk9C-"
    "/pub?gid=1583146028&single=true&output=csv"
)
FORM_API = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSfLySolQSiRXV0wELNPhUBlKJh77RnJKWc2-uqAM0TPNG3Q5A/formResponse"
)
BG_IMAGE_URL = "https://raw.githubusercontent.com/paichiarakkal/paichiarakkal/main/profile.jpg"

# Secrets (streamlit cloud / local secrets.toml)
WA_PHONE = st.secrets.get("WA_PHONE", "")
WA_API_KEY = st.secrets.get("WA_API_KEY", "")
TWILIO_SID = st.secrets.get("TWILIO_SID", "")
TWILIO_TOKEN = st.secrets.get("TWILIO_TOKEN", "")
TWILIO_FROM = st.secrets.get("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

USER_PINS = {
    "faisal": st.secrets.get("PIN_FAISAL", ""),
    "shabana": st.secrets.get("PIN_SHABANA", ""),
    "admin": st.secrets.get("PIN_ADMIN", ""),
}


# ============================================
# PAGE SETUP
# ============================================
st.set_page_config(page_title="PAICHI EXPENSES v4.0", layout="wide")

# Autorefresh — only on dashboard, not on entry pages
if st.session_state.get("page") == "🏠 Dashboard":
    st_autorefresh(interval=60000, key="auto_refresh")


# ============================================
# CSS
# ============================================
st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image: linear-gradient(rgba(0,0,0,0.70), rgba(0,0,0,0.70)), url("{BG_IMAGE_URL}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    [data-testid="stHeader"] {{ background-color: rgba(0,0,0,0); }}
    [data-testid="stSidebar"] {{ background: rgba(0,0,0,0.85) !important; }}
    .stButton>button {{
        background-color: #FFD700; color: #000;
        border-radius: 10px; font-weight: bold; width: 100%;
        transition: 0.3s;
    }}
    .stButton>button:hover {{
        background-color: #FFF; color: #000;
        box-shadow: 0px 0px 10px #FFD700;
    }}
    .balance-banner {{
        background: rgba(0,0,0,0.65);
        backdrop-filter: blur(10px);
        padding: 25px; border-radius: 15px;
        border-left: 10px solid #FFD700;
        margin-bottom: 25px; text-align: center;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5);
    }}
    .purple-box {{
        background: rgba(0,0,0,0.65);
        backdrop-filter: blur(10px);
        padding: 20px; border-radius: 25px;
        border: 2px solid rgba(255,215,0,0.3);
        text-align: center; margin-bottom: 20px;
    }}
    .category-box {{
        background: rgba(0,0,0,0.65);
        backdrop-filter: blur(10px);
        padding: 15px; border-radius: 15px;
        text-align: center;
        border-bottom: 4px solid #FFD700;
        margin-bottom: 15px;
    }}
    .alert-banner {{
        background-color: #ff4d4d; color: white;
        padding: 10px; border-radius: 10px;
        text-align: center; font-weight: bold;
        margin-bottom: 20px;
    }}
    .login-card {{
        background: rgba(0,0,0,0.7);
        backdrop-filter: blur(10px);
        padding: 25px; border-radius: 20px;
        border: 1px solid rgba(255,215,0,0.4);
        box-shadow: 0px 8px 32px 0 rgba(0,0,0,0.7);
        max-width: 450px; margin: auto; margin-top: 30px;
    }}
    .login-title {{
        text-align: center; font-size: 22px;
        font-weight: bold; color: #FFD700 !important;
        margin-bottom: 15px;
    }}
    h1, h2, h3, p, label {{ color: white !important; font-weight: bold !important; }}
    .stDataFrame {{ background: white; border-radius: 10px; color: black; }}
    </style>
""", unsafe_allow_html=True)


# ============================================
# SESSION INIT
# ============================================
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = ""
if "custom_alert_text" not in st.session_state:
    st.session_state.custom_alert_text = "Shop kuri book"
if "low_limit" not in st.session_state:
    st.session_state.low_limit = 6000


# ============================================
# HELPERS
# ============================================
def send_whatsapp_auto(msg: str):
    """CallMeBot WhatsApp notification (background thread)."""
    if not (WA_PHONE and WA_API_KEY):
        return
    def _send():
        try:
            r = requests.get(
                f"https://api.callmebot.com/whatsapp.php"
                f"?phone={WA_PHONE}&text={urllib.parse.quote(msg)}&apikey={WA_API_KEY}",
                timeout=10,
            )
            if r.status_code != 200:
                print(f"[WA] Failed: {r.status_code}")
        except Exception as e:
            print(f"[WA] Error: {e}")
    threading.Thread(target=_send, daemon=True).start()


def send_twilio_whatsapp(to_number: str, msg_body: str):
    """Twilio WhatsApp message (optional)."""
    if not (TWILIO_SID and TWILIO_TOKEN):
        return
    try:
        from twilio.rest import Client
        Client(TWILIO_SID, TWILIO_TOKEN).messages.create(
            from_=TWILIO_FROM, body=msg_body, to=f"whatsapp:{to_number}"
        )
    except Exception as e:
        print(f"[Twilio] Error: {e}")


def parse_mixed_dates(date_series: pd.Series) -> pd.Series:
    """Parse dates — try dayfirst, fallback to monthfirst."""
    parsed = []
    for val in date_series:
        s = str(val).strip()
        dt = pd.to_datetime(s, dayfirst=True, errors="coerce")
        if pd.isna(dt):
            dt = pd.to_datetime(s, errors="coerce")
        parsed.append(dt)
    return pd.Series(parsed)


@st.cache_data(ttl=30)
def load_data() -> pd.DataFrame:
    """Load CSV with error handling."""
    try:
        df = pd.read_csv(f"{CSV_URL}&r={random.randint(1, 999)}")
        df.columns = df.columns.str.strip()
        if "Date" not in df.columns:
            st.error("Date column missing in sheet!")
            return pd.DataFrame()
        df["Date"] = parse_mixed_dates(df["Date"])
        df["Debit"] = pd.to_numeric(df["Debit"], errors="coerce").fillna(0)
        df["Credit"] = pd.to_numeric(df["Credit"], errors="coerce").fillna(0)
        return df
    except Exception as e:
        st.error(f"Data load error: {e}")
        return pd.DataFrame()


def create_pdf(df: pd.DataFrame) -> BytesIO | None:
    """Generate PDF with Unicode support."""
    try:
        pdf = FPDF()
        pdf.add_page()
        # Unicode font (place DejaVuSans.ttf in project root)
        try:
            pdf.add_font("DejaVu", "", "DejaVuSans.ttf")
            pdf.set_font("DejaVu", "", 10)
            use_unicode = True
        except Exception:
            pdf.set_font("Arial", "", 10)
            use_unicode = False

        pdf.set_font("Arial", "B", 14)
        pdf.cell(190, 10, txt="PAICHI FINANCE REPORT", ln=True, align="C")
        pdf.ln(10)

        widths = {"Date": 30, "Item": 85, "Debit": 35, "Credit": 35}
        pdf.set_font("Arial", "B", 10)
        for col in widths:
            pdf.cell(widths[col], 10, txt=col, border=1, align="C")
        pdf.ln()

        pdf.set_font("Arial", "", 9)
        for _, row in df.iterrows():
            if pdf.get_y() > 260:
                pdf.add_page()
            y_start = pdf.get_y()

            # Date
            pdf.cell(30, 10, txt=str(row["Date"]), border=0)
            x_after_date = pdf.get_x()

            # Item (Unicode-aware)
            item_text = str(row["Item"])
            if not use_unicode:
                item_text = item_text.encode("ascii", "ignore").decode("ascii")
            pdf.multi_cell(85, 5, txt=item_text, border=0)
            h = max(10, pdf.get_y() - y_start)

            # Amounts
            pdf.set_xy(x_after_date + 85, y_start)
            pdf.cell(35, h, txt=str(row["Debit"]), border=0, align="R")
            pdf.cell(35, h, txt=str(row["Credit"]), border=0, align="R")

            # Borders
            pdf.set_xy(10, y_start)
            for w in widths.values():
                pdf.cell(w, h, txt="", border=1)
            pdf.set_y(y_start + h)

        return BytesIO(bytes(pdf.output()))
    except Exception as e:
        print(f"[PDF] Error: {e}")
        return None


def extract_cat(x) -> str:
    """Simplified category extraction."""
    item_text = str(x).lower()
    rules = {
        "Food": ["food", "ഭക്ഷണം", "ചായ", "ഹോട്ടൽ", "ബിരിയാണി", "mess", "lunch"],
        "Shop": ["shop", "കട", "സാധനങ്ങൾ", "സൂപ്പർമാർക്കറ്റ്", "groceries"],
        "Fish": ["fish", "മീൻ", "ഇറച്ചി", "ചിക്കൻ", "meat", "chicken"],
        "Travel": ["travel", "യാത്ര", "പെട്രോൾ", "വണ്ടി", "ടാക്സി", "petrol", "diesel"],
        "Rent": ["rent", "വാടക", "റൂം"],
    }
    for cat, keywords in rules.items():
        if any(w in item_text for w in keywords):
            return cat
    if "]" in str(x) and ":" in str(x):
        return str(x).split("]")[1].split(":")[0].strip().capitalize()
    if ":" in str(x):
        return str(x).split(":")[0].strip().capitalize()
    return "Others"


# ============================================
# LOGIN SCREEN
# ============================================
if not st.session_state.auth:
    st.markdown('<div class="login-card"><div class="login-title">🔐 PAICHI EXPENSES</div>', unsafe_allow_html=True)

    u = st.selectbox("👤 Select User", ["faisal", "shabana", "admin"]).lower()
    pin = st.text_input("🔑 Enter 4-Digit PIN", type="password", max_chars=4)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("UNLOCK APP 🔓"):
        expected_pin = USER_PINS.get(u, "")
        if expected_pin and expected_pin == pin:
            st.session_state.auth = True
            st.session_state.user = u
            st.rerun()
        else:
            st.error("❌ Incorrect PIN! Try again.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()


# ============================================
# MAIN APP (authenticated)
# ============================================
df = load_data()
t_in = df["Credit"].sum() if not df.empty else 0.0
t_out = df["Debit"].sum() if not df.empty else 0.0
bal = t_in - t_out


# ----- Sidebar Settings -----
if st.session_state.user != "shabana":
    with st.sidebar.expander("⚙️ Alert & Expense Settings"):
        st.session_state.custom_alert_text = st.text_area(
            "Custom Alert Message", value=st.session_state.custom_alert_text
        )
        st.session_state.low_limit = st.number_input(
            "Low Balance Limit (₹)", value=st.session_state.low_limit
        )

if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()


# ----- Alert Banner -----
if bal < st.session_state.low_limit:
    st.markdown(
        f'<div class="alert-banner">⚠️ ശ്രദ്ധിക്കുക: അക്കൗണ്ട് ബാലൻസ് കുറവാണ് '
        f'{st.session_state.custom_alert_text} (₹{bal:,.2f})! അത്യാവശ്യ കാര്യങ്ങൾക്കായി ഫണ്ട് സൂക്ഷിക്കുക.</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="balance-banner">'
    f'<span style="font-size:20px; color:#E0B0FF;">Available Balance</span><br>'
    f'<span style="font-size:40px; color:#FFD700; font-weight:bold;">₹{bal:,.2f}</span>'
    f'</div>',
    unsafe_allow_html=True,
)


# ----- Menu -----
menu = ["💰 Add Entry", "📅 Calendar", "📊 Report", "🔍 History", "🤝 Debt Tracker"]
if st.session_state.user != "shabana":
    menu.insert(0, "🏠 Dashboard")

page = st.sidebar.radio("Menu", menu)
st.session_state.page = page  # store for autorefresh logic

if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.rerun()


# ============================================
# PAGE: DASHBOARD
# ============================================
if page == "🏠 Dashboard" and not df.empty:
    st.title("Financial Overview")
    st.markdown(
        f'<div class="purple-box">'
        f'<h2 style="color:#00FF00;">Total Credit: ₹{t_in:,.2f}</h2>'
        f'<h2 style="color:#FF3131;">Total Debit: ₹{t_out:,.2f}</h2>'
        f'</div>',
        unsafe_allow_html=True,
    )

    st.subheader("🗂️ Categorywise Expense Breakdown")
    df_dash = df.copy()
    df_dash["Cat"] = df_dash["Item"].apply(extract_cat)
    cats = (
        df_dash[~df_dash["Item"].str.contains("total", case=False, na=False)]
        .groupby("Cat")["Debit"]
        .sum()
        .to_dict()
    )

    cols = st.columns(3)
    idx = 0
    for c_name, c_amt in cats.items():
        if c_amt > 0:
            with cols[idx % 3]:
                st.markdown(
                    f'<div class="category-box">'
                    f'<span style="font-size:16px; color:#aaa;">Total {c_name}</span><br>'
                    f'<span style="font-size:24px; color:#FFF; font-weight:bold;">₹{c_amt:,.2f}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            idx += 1


# ============================================
# PAGE: ADD ENTRY
# ============================================
elif page == "💰 Add Entry":
    st.title("Smart Voice Entry 🎙️")

    # Voice input — persist across reruns
    v_raw = speech_to_text(language="ml", key="voice_v9")
    if v_raw:
        st.session_state["voice_data"] = v_raw
    v_raw = st.session_state.get("voice_data", "")

    v_cat, v_amt, v_desc, v_type = "Others", "", "", "Debit"

    if v_raw:
        raw = v_raw.lower().replace(".", "").replace(",", "")
        nums = re.findall(r"\d+", raw)
        v_amt = nums[0] if nums else ""
        v_desc = re.sub(r"\d+", "", raw).strip()

        rules_voice = {
            "Food": ["food", "ഭക്ഷണം", "ചായ", "ഹോട്ടൽ", "ബിരിയാണി", "mess"],
            "Shop": ["shop", "കട", "സാധനങ്ങൾ", "സൂപ്പർമാർക്കറ്റ്", "groceries"],
            "Fish": ["fish", "മീൻ", "ഇറച്ചി", "ചിക്കൻ", "meat"],
            "Travel": ["travel", "യാത്ര", "പെട്രോൾ", "വണ്ടി", "ടാക്സി", "petrol"],
            "Rent": ["rent", "വാടക", "റൂം"],
        }
        for cat, kws in rules_voice.items():
            if any(x in raw for x in kws):
                v_cat = cat
                break

        if any(x in raw for x in ["കിട്ടി", "വന്നു", "തന്നു", "ക്രെഡിറ്റ്", "credit"]):
            v_type = "Credit"

    with st.form("entry_form", clear_on_submit=True):
        it = st.text_input("Description", value=v_desc)
        am_str = st.text_input("Amount", value=str(v_amt))
        cat_options = ["Food", "Shop", "Fish", "Travel", "Rent", "Others"]
        cat = st.selectbox(
            "Category", cat_options,
            index=cat_options.index(v_cat) if v_cat in cat_options else 0,
        )
        ty = st.radio(
            "Type", ["Debit", "Credit"], horizontal=True,
            index=0 if v_type == "Debit" else 1,
        )
        submitted = st.form_submit_button("SAVE & NOTIFY")

    if submitted:
        try:
            am = float(am_str.strip().replace(",", ""))
            payload = {
                "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                "entry.2013476337": f"[{st.session_state.user.capitalize()}] {cat}: {it}",
                "entry.1460982454": am if ty == "Debit" else 0,
                "entry.1221658767": 0 if ty == "Debit" else am,
            }
            threading.Thread(
                target=lambda: requests.post(FORM_API, data=payload, timeout=10),
                daemon=True,
            ).start()

            wa_msg = (
                f"✅ *Paichi Entry*\n"
                f"📝 Item: {it}\n"
                f"💰 Amt: ₹{am}\n"
                f"👤 User: {st.session_state.user}"
            )
            send_whatsapp_auto(wa_msg)

            st.session_state["voice_data"] = ""  # clear voice cache
            st.session_state["flash"] = "Saved! ✅"
            st.cache_data.clear()
            st.rerun()
        except ValueError:
            st.error("❌ Valid amount required!")


# ============================================
# PAGE: CALENDAR
# ============================================
elif page == "📅 Calendar":
    st.title("P&L Calendar View 📅")
    df_cal = df.dropna(subset=["Date"]) if not df.empty else pd.DataFrame()

    if df_cal.empty:
        st.warning("No valid date data found!")
    else:
        summary = (
            df_cal.groupby(df_cal["Date"].dt.strftime("%Y-%m-%d"))
            .agg({"Debit": "sum", "Credit": "sum"})
            .reset_index()
        )
        events = []
        for _, row in summary.iterrows():
            if row["Credit"] > 0:
                events.append({
                    "title": f" +₹{row['Credit']:,.0f}",
                    "start": row["Date"],
                    "backgroundColor": "#198754",
                    "borderColor": "#198754",
                    "textColor": "white",
                })
            if row["Debit"] > 0:
                events.append({
                    "title": f" -₹{row['Debit']:,.0f}",
                    "start": row["Date"],
                    "backgroundColor": "#dc3545",
                    "borderColor": "#dc3545",
                    "textColor": "white",
                })

        cal_data = calendar(
            events=events,
            options={
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth",
                },
                "initialView": "dayGridMonth",
                "selectable": True,
            },
            key="pnl_calendar",
        )

        if cal_data.get("eventClick"):
            dt_click = cal_data["eventClick"]["event"]["start"].split("T")[0]
            st.markdown("---")
            st.subheader(f"📋 Details for {pd.to_datetime(dt_click).strftime('%d %B %Y')}")
            day_df = df_cal[df_cal["Date"].dt.strftime("%Y-%m-%d") == dt_click].copy()
            if not day_df.empty:
                day_df["Date"] = day_df["Date"].dt.strftime("%d/%m/%Y")
                st.download_button(
                    "📥 Download This Day's Data",
                    day_df[["Date", "Item", "Debit", "Credit"]].to_csv(index=False).encode("utf-8"),
                    f"Transactions_{dt_click}.csv",
                    "text/csv",
                )
                st.dataframe(day_df[["Date", "Item", "Debit", "Credit"]], use_container_width=True)


# ============================================
# PAGE: REPORT & HISTORY
# ============================================
elif page in ("📊 Report", "🔍 History"):
    if df.empty:
        st.warning("No data available!")
    else:
        df_rep = df[
            (df["Date"].dt.year == 2026) & (df["Date"].dt.month >= 4)
        ].copy()
        df_rep["Month"] = df_rep["Date"].dt.strftime("%B %Y")
        months = (
            df_rep.dropna(subset=["Month"])
            .sort_values("Date", ascending=False)["Month"]
            .unique()
        )

        if len(months) == 0:
            st.warning("No data found from April 2026 onwards!")
        else:
            sel_m = st.selectbox("Select Month", months, key=f"{page}_select")
            m_df = df_rep[df_rep["Month"] == sel_m].copy()

            search_query = st.text_input(
                "🔍 Search items (e.g. Fish, Petrol, Travel)...", ""
            ).strip().lower()
            filter_type = st.selectbox("Filter Type", ["All", "Debit Only", "Credit Only"])

            if search_query:
                m_df = m_df[m_df["Item"].str.lower().str.contains(searc