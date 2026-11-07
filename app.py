import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from fpdf import FPDF
import json
import base64
import os                      # FIX: PDF font detection-ന്
from groq import Groq

# --- CONFIG ---
CSV_URL = "YOUR_FINANCE_SHEET_CSV_LINK"
FORM_API = "YOUR_FINANCE_FORM_API"
STOCK_CSV_URL = "YOUR_STOCK_SHEET_CSV_LINK"
STOCK_FORM_API = "YOUR_STOCK_FORM_API"

USER_PINS = {"admin": "1234", "shop1": "1111"}

# FIX: st.secrets missing ആയാൽ crash ആവില്ല
try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = ""

# FIX: Vision-സപ്പോർട്ടുള്ള മോഡൽ (text-only gpt-oss-120b പകരം)
VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
AGENT_MODEL  = "llama-3.3-70b-versatile"


# --- SAFE FORM SUBMIT ---
def submit_form(api_url, payload):
    if not api_url or "YOUR_" in api_url:
        return True
    try:
        r = requests.post(api_url, data=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        st.error(f"❌ Submission failed: {e}")
        return False


# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="PAICHI BUSINESS", layout="wide")

st.markdown("""
    <style>
    .stApp { background: #f4f6f9; color: #000000; }
    [data-testid="stSidebar"] { background: #e0e0e0 !important; }
    .stButton>button { background-color: #007BFF; color: #ffffff; border-radius: 10px; font-weight: bold; }
    .stDownloadButton>button { background-color: #28a745; color: #ffffff; border-radius: 10px; font-weight: bold; }
    .banner { background: #ffffff; padding: 25px; border-radius: 15px; border-left: 10px solid #007BFF; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    h1, h2, h3, p, label, span { color: #000000 !important; font-weight: bold !important; }
    [data-testid="stChatMessage"] { background-color: #ffffff !important; border-radius: 10px; padding: 15px; border: 1px solid #ccc; color: #000; }
    .banner .b-label { color: #007BFF !important; font-size: 20px; }
    .banner .b-value { color: #000000 !important; font-size: 40px; }
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state.auth, st.session_state.user = False, ""
if "messages" not in st.session_state:
    st.session_state.messages = []


# FIX: Form submit-ന് ശേഷം rerun ചെയ്തും success message കാണിക്കാൻ
def flash_success(msg):
    st.session_state["_flash"] = msg

def show_flash():
    msg = st.session_state.pop("_flash", None)
    if msg:
        st.success(msg)


# --- HELPER: Safe CSV load ---
def _append_cache_buster(url):
    if not url or "YOUR_" in url:
        raise ValueError("placeholder")
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}r={random.randint(1,999)}"

@st.cache_data(ttl=5)
def load_finance_data():
    try:
        df = pd.read_csv(_append_cache_buster(CSV_URL))
        df.columns = df.columns.str.strip()
        df['Debit'] = pd.to_numeric(df['Debit'], errors='coerce').fillna(0)
        df['Credit'] = pd.to_numeric(df['Credit'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame({
            'Date': ['2026-11-01', '2026-11-02', '2026-11-03', '2026-11-04'],
            'Shop Name': ['Shop 1', 'Shop 2', 'Shop 1', 'Shop 2'],
            'Item': ['Sales', 'Sales', 'Salary: Rahim', 'Rent'],
            'Debit': [0, 0, 2500, 5000],
            'Credit': [4500, 6000, 0, 0]
        })

@st.cache_data(ttl=5)
def load_stock_data():
    try:
        df = pd.read_csv(_append_cache_buster(STOCK_CSV_URL))
        df.columns = df.columns.str.strip()
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame({
            'Date': ['2026-11-01', '2026-11-02', '2026-11-03'],
            'Item': ['Sugar', 'Sugar', 'Milk'],
            'Quantity': [100, 20, 50],
            'Type': ['Stock In', 'Stock Out', 'Stock In']
        })


# FIX: Malayalam PDF-ന് Unicode font auto-detect (ഇല്ലെങ്കിൽ ascii fallback)
def _find_unicode_font():
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def generate_pdf(df, title, columns):
    pdf = FPDF()
    pdf.add_page()

    font_path = _find_unicode_font()
    has_unicode = False
    if font_path:
        try:
            pdf.add_font("UFont", "", font_path)
            has_unicode = True
        except Exception:
            has_unicode = False

    if has_unicode:
        pdf.set_font("UFont", size=14)
    else:
        pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(190, 10, txt=title, ln=True, align='C')
    pdf.ln(10)

    if has_unicode:
        pdf.set_font("UFont", size=10)
    else:
        pdf.set_font("Helvetica", 'B', 10)

    col_width = 190 / len(columns)
    for col in columns:
        pdf.cell(col_width, 10, txt=str(col), border=1, align='C')
    pdf.ln()

    if has_unicode:
        pdf.set_font("UFont", size=9)
    else:
        pdf.set_font("Helvetica", size=9)

    def _safe(v):
        s = str(v)
        return s if has_unicode else s.encode('ascii', 'ignore').decode('ascii')

    for _, row in df.iterrows():
        for col in columns:
            pdf.cell(col_width, 10, txt=_safe(row[col]), border=1)
        pdf.ln()

    return bytes(pdf.output())


# ============================================
# 🤖 AI AGENT TOOLS
# ============================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_finance",
            "description": "ഒരു പുതിയ സാമ്പത്തിക ഇടപാട് (Debit/Credit) ചേർക്കുക.",
            "parameters": {
                "type": "object",
                "properties": {
                    "shop":   {"type": "string", "enum": ["Shop 1", "Shop 2"]},
                    "item":   {"type": "string", "description": "ഇടപാടിന്റെ വിവരണം"},
                    "amount": {"type": "number"},
                    "type":   {"type": "string", "enum": ["Debit", "Credit"]}
                },
                "required": ["shop", "item", "amount", "type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_stock",
            "description": "സ്റ്റോക്കിൽ പുതിയ സാധനങ്ങൾ ചേർക്കുകയോ കുറയ്ക്കുകയോ ചെയ്യുക.",
            "parameters": {
                "type": "object",
                "properties": {
                    "item_name":  {"type": "string"},
                    "qty":        {"type": "number"},
                    "stock_type": {"type": "string", "enum": ["Stock In", "Stock Out"]}
                },
                "required": ["item_name", "qty", "stock_type"]
            }
        }
    }
]

def execute_add_finance(shop, item, amount, t_type):
    payload = {
        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
        "entry.2013476337": f"[{shop}] {item}",
        "entry.1460982454": amount if t_type == "Debit" else 0,
        "entry.1221658767": 0 if t_type == "Debit" else amount
    }
    if submit_form(FORM_API, payload):
        load_finance_data.clear()   # FIX: specific cache clear
        return "Success"
    return "Failed"

def execute_add_stock(item_name, qty, stock_type):
    payload = {
        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
        "entry.2013476337": item_name,
        "entry.1460982454": qty,
        "entry.1221658767": stock_type
    }
    if submit_form(STOCK_FORM_API, payload):
        load_stock_data.clear()     # FIX: specific cache clear
        return "Success"
    return "Failed"


# FIX: Vision - ശരിയായ image_url payload, (success, msg) return
def analyze_image_with_groq(image_bytes):
    if not GROQ_API_KEY:
        return False, "Groq API Key missing!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        prompt_text = (
            "Analyze this shop CCTV frame. Count how many people are visible, "
            "where they're positioned, notable actions, and provide a short "
            "business footfall activity report."
        )
        completion = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }}
                ]
            }],
            max_tokens=500
        )
        return True, completion.choices[0].message.content
    except Exception as e:
        return False, f"Vision Analysis Error: {str(e)}"


# FIX: Salary parser - crash-safe
def _parse_employee(item_str):
    try:
        if ':' not in item_str:
            return "Unknown"
        part = item_str.split(':', 1)[1]
        return part.split('(')[0].strip() or "Unknown"
    except Exception:
        return "Unknown"


# --- 🔒 LOGIN ---
if not st.session_state.auth:
    _, mid, _ = st.columns([1, 2, 1])     # FIX: columns wrapper
    with mid:
        st.subheader("🔐 PAICHI BUSINESS LOGIN")
        u = st.selectbox("👤 Select Role", ["admin", "shop1"]).lower()
        pin = st.text_input("🔑 Enter PIN (admin:1234, shop1:1111)",
                            type="password", max_chars=4)
        if st.button("LOGIN"):
            if USER_PINS.get(u) == pin:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else:
                st.error("❌ Incorrect PIN!")

else:
    st.sidebar.title(f"👋 Welcome, {st.session_state.user.capitalize()}")
    menu = ["📊 Dashboard", "💰 Add Finance", "📦 Stock Management",
            "👨‍💼 Staff Salary", "🤖 AI Agent", "🎥 CCTV AI Vision"]
    page = st.sidebar.radio("Menu", menu)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.messages = []
        st.rerun()

    df_fin = load_finance_data()
    df_stk = load_stock_data()
    t_in, t_out = df_fin['Credit'].sum(), df_fin['Debit'].sum()
    bal = t_in - t_out

    # --- 1. DASHBOARD ---
    if page == "📊 Dashboard":
        st.markdown(
            f'<div class="banner">'
            f'<span class="b-label">Total Business Balance</span><br>'
            f'<span class="b-value">₹{bal:,.2f}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
        st.subheader("📈 Shop-wise Performance")
        if not df_fin.empty:
            shop_data = df_fin.groupby('Shop Name')[['Credit', 'Debit']].sum().reset_index()
            fig = px.bar(shop_data, x='Shop Name', y=['Credit', 'Debit'],
                         barmode='group',
                         color_discrete_sequence=['#00FF00', '#FF3131'],
                         title="Credit vs Debit")
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("📋 Recent Transactions")
            st.dataframe(df_fin.tail(10).iloc[::-1], use_container_width=True)

    # --- 2. ADD FINANCE ---
    elif page == "💰 Add Finance":
        st.title("💰 Finance Entry")
        show_flash()
        with st.form("finance_form", clear_on_submit=True):
            shop = st.selectbox("Select Shop", ["Shop 1", "Shop 2"])
            it = st.text_input("Description")
            am_str = st.text_input("Amount")
            ty = st.radio("Type", ["Debit (Expense)", "Credit (Sales)"], horizontal=True)

            if st.form_submit_button("SAVE ENTRY"):
                clean = am_str.strip().replace(',', '')
                if not clean:
                    st.error("❗ Please enter an amount.")
                else:
                    try:
                        am = float(clean)
                        res = execute_add_finance(
                            shop, it, am,
                            "Debit" if "Debit" in ty else "Credit"
                        )
                        if res == "Success":
                            flash_success("Saved! ✅")
                            st.rerun()          # FIX
                        else:
                            st.error("❌ Save failed.")
                    except ValueError:
                        st.error("❗ Invalid amount format.")

    # --- 3. STOCK MANAGEMENT ---
    elif page == "📦 Stock Management":
        st.title("📦 Stock & Inventory")
        show_flash()
        tab1, tab2, tab3 = st.tabs(["📊 Current Stock", "➕ Add Entry", "📄 Item History & PDF"])

        with tab1:
            if not df_stk.empty:
                s = df_stk.copy()
                s['In']  = s.apply(lambda x: x['Quantity'] if x['Type'] == 'Stock In'  else 0, axis=1)
                s['Out'] = s.apply(lambda x: x['Quantity'] if x['Type'] == 'Stock Out' else 0, axis=1)
                final_stk = s.groupby('Item')[['In', 'Out']].sum().reset_index()
                final_stk['Available Stock'] = final_stk['In'] - final_stk['Out']
                st.dataframe(final_stk[['Item', 'Available Stock']], use_container_width=True)
            else:
                st.info("No stock data.")

        with tab2:
            with st.form("stock_form", clear_on_submit=True):
                item_name  = st.text_input("Item Name")
                qty        = st.number_input("Quantity", min_value=1.0)
                stock_type = st.radio("Type", ["Stock In", "Stock Out"], horizontal=True)
                if st.form_submit_button("SAVE STOCK"):
                    if execute_add_stock(item_name, qty, stock_type) == "Success":
                        flash_success("Stock Updated! ✅")
                        st.rerun()              # FIX
                    else:
                        st.error("❌ Stock update failed.")

        with tab3:
            if not df_stk.empty:
                selected_item = st.selectbox("Select Item", df_stk['Item'].unique())
                item_history = df_stk[df_stk['Item'] == selected_item]
                st.dataframe(item_history[['Date', 'Type', 'Quantity']], use_container_width=True)
                pdf_b = generate_pdf(item_history, f"Stock History: {selected_item}",
                                     ['Date', 'Type', 'Quantity'])
                st.download_button(f"📥 Download {selected_item} PDF", pdf_b,
                                   f"{selected_item}_Stock.pdf", "application/pdf")

    # --- 4. STAFF SALARY ---
    elif page == "👨‍💼 Staff Salary":
        st.title("👨‍💼 Staff Salary Management")
        show_flash()

        with st.expander("പുതിയ ശമ്പളം നൽകുക (Add New Salary)"):
            with st.form("salary_form", clear_on_submit=True):
                shop      = st.selectbox("Select Shop", ["Shop 1", "Shop 2"])
                emp_name  = st.text_input("Employee Name")
                sal_amt   = st.number_input("Salary Amount", min_value=1.0)
                sal_month = st.selectbox("Month", ["November 2026", "October 2026"])
                if st.form_submit_button("PAY SALARY"):
                    res = execute_add_finance(
                        shop, f"Salary: {emp_name} ({sal_month})", sal_amt, "Debit"
                    )
                    if res == "Success":
                        flash_success(f"✅ {emp_name}-ന്റെ ശമ്പളം വിജയകരമായി നൽകി!")
                        st.rerun()              # FIX
                    else:
                        st.error("❌ Salary payment failed.")

        st.divider()
        st.subheader("📄 Salary History & PDF")
        if not df_fin.empty:
            sal_df = df_fin[df_fin['Item'].str.contains('Salary', case=False, na=False)].copy()
            if not sal_df.empty:
                # FIX: crash-safe parser
                sal_df['Employee'] = sal_df['Item'].apply(_parse_employee)
                selected_emp = st.selectbox("Select Staff Member", sal_df['Employee'].unique())
                emp_history = sal_df[sal_df['Employee'] == selected_emp]
                st.dataframe(emp_history[['Date', 'Shop Name', 'Item', 'Debit']],
                             use_container_width=True)
                pdf_b = generate_pdf(emp_history, f"Salary Report: {selected_emp}",
                                     ['Date', 'Shop Name', 'Debit'])
                st.download_button(f"📥 Download {selected_emp}'s Salary PDF", pdf_b,
                                   f"{selected_emp}_Salary.pdf", "application/pdf")
            else:
                st.info("No salary records found.")

    # --- 5. AI AGENT ---
    elif page == "🤖 AI Agent":
        st.title("🤖 PAICHI Business AI Agent")
        st.write("ബിസിനസ്സിലെ കാര്യങ്ങൾ ചാറ്റ് വഴി ചെയ്യാം. (ഉദാ: 'Shop 1-ൽ 5000 സെയിൽസ് ഉണ്ടായി')")

        if not GROQ_API_KEY:
            st.error("Groq API Key ലഭ്യമല്ല!")

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        if prompt := st.chat_input("Ask me to add finance, stock, or check balance..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("AI ആലോചിക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    system_instruction = f"""
                    നീ ഒരു വളരെ മികച്ച ബിസിനസ്സ് മാനേജർ AI ഏജന്റ് ആണ്.
                    നിലവിലെ മൊത്തം ബാലൻസ്: ₹{bal:,.2f}.
                    യൂസർ ഫിനാൻസ് എൻട്രി ചേർക്കാൻ പറഞ്ഞാൽ add_finance ടൂൾ ഉപയോഗിക്കുക.
                    യൂസർ സ്റ്റോക്ക് കാര്യങ്ങൾ പറഞ്ഞാൽ add_stock ടൂൾ ഉപയോഗിക്കുക.
                    എന്ത് ചോദിച്ചാലും മലയാളത്തിൽ മറുപടി നൽകുക.
                    """
                    messages_for_api = [{"role": "system", "content": system_instruction}] + \
                        [{"role": m["role"], "content": m["content"]}
                         for m in st.session_state.messages[-5:]]

                    response = client.chat.completions.create(
                        model=AGENT_MODEL,
                        messages=messages_for_api,
                        tools=tools,
                        tool_choice="auto"
                    )

                    response_message = response.choices[0].message
                    tool_used = False

                    if response_message.tool_calls:
                        tool_used = True
                        replies = []        # FIX: multiple tool calls handle
                        for tool_call in response_message.tool_calls:
                            try:
                                args = json.loads(tool_call.function.arguments)
                            except json.JSONDecodeError:
                                replies.append(
                                    f"❌ ടൂൾ arguments parse ചെയ്യാൻ പറ്റിയില്ല: {tool_call.function.name}"
                                )
                                continue

                            if tool_call.function.name == "add_finance":
                                res = execute_add_finance(
                                    args["shop"], args["item"],
                                    args["amount"], args["type"]
                                )
                                replies.append(
                                    f"✅ ചേട്ടാ, {args['shop']}-ൽ '{args['item']}' എന്നതിന് "
                                    f"₹{args['amount']} ({args['type']}) എൻട്രി ഇട്ടിട്ടുണ്ട്!"
                                    if res == "Success"
                                    else "❌ എൻട്രി ഇടാൻ പറ്റിയില്ല."
                                )
                            elif tool_call.function.name == "add_stock":
                                res = execute_add_stock(
                                    args["item_name"], args["qty"], args["stock_type"]
                                )
                                replies.append(
                                    f"✅ ചേട്ടാ, {args['item_name']}-ന്റെ {args['qty']} എണ്ണം "
                                    f"അപ്ഡേറ്റ് ചെയ്തിട്ടുണ്ട്!"
                                    if res == "Success"
                                    else "❌ സ്റ്റോക്ക് അപ്ഡേറ്റ് ചെയ്യാൻ പറ്റിയില്ല."
                                )
                        ai_reply = "\n\n".join(replies) if replies else "ഒന്നും ചെയ്യാൻ പറ്റിയില്ല."
                    else:
                        ai_reply = response_message.content or ""

                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    with st.chat_message("assistant"):
                        st.markdown(ai_reply)

                    if tool_used:
                        st.rerun()

                except Exception as e:
                    st.error(f"AI Error: {str(e)}")

    # --- 6. CCTV AI VISION ---
    elif page == "🎥 CCTV AI Vision":
        st.title("🎥 CCTV AI Vision & Footfall Monitor")
        st.write("കടയിലെ ക്യാമറ ഫൂട്ടേജോ ചിത്രമോ അപ്‌ലോഡ് ചെയ്ത് ആളുകളുടെ വരവും (Footfall) "
                 "പ്രവർത്തനങ്ങളും AI വഴി വിശകലനം ചെയ്യാം.")

        if not GROQ_API_KEY:
            st.error("Groq API Key ലഭ്യമല്ല — `.streamlit/secrets.toml`-ൽ `GROQ_API_KEY` set ചെയ്യുക.")

        uploaded_cctv_file = st.file_uploader("Upload Shop CCTV Frame (JPG/PNG)",
           type=["jpg", "jpeg", "png"])
        if uploaded_cctv_file is not None:
            st.image(uploaded_cctv_file, caption="Uploaded CCTV Snapshot",
                     use_container_width=True)

            if st.button("🔍 Analyze CCTV Frame with AI"):
                with st.spinner("AI CCTV ഫൂട്ടേജ് പരിശോധിക്കുന്നു..."):
                    ok, analysis_result = analyze_image_with_groq(
                        uploaded_cctv_file.getvalue()
                    )
                    st.subheader("📊 AI CCTV Analysis Report")
                    if ok:                       # FIX: error-ന് st.error
                        st.success(analysis_result)
                    else:
                        st.error(analysis_result)                                   type=["jpg", "jpeg", "png"])
        if uploaded_cctv_file is not None:
            st.image(uploaded_cctv_file, caption="Uploaded CCTV Snapshot",
                     use_container_width=True)

            if st.button("🔍 Analyze CCTV Frame with AI"):
                with st.spinner("AI CCTV ഫൂട്ടേജ് പരിശോധിക്കുന്നു..."):
                    ok, analysis_result = analyze_image_with_groq(
                        uploaded_cctv_file.getvalue()
                    )
                    st.subheader("📊 AI CCTV Analysis Report")
                    if ok:                       # FIX: error-ന് st.error
                        st.success(analysis_result)
                    else:
                        st.error(analysis_result)