import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from fpdf import FPDF

# --- CONFIG ---
CSV_URL = "YOUR_FINANCE_SHEET_CSV_LINK"
FORM_API = "YOUR_FINANCE_FORM_API"
STOCK_CSV_URL = "YOUR_STOCK_SHEET_CSV_LINK"
STOCK_FORM_API = "YOUR_STOCK_FORM_API"

USER_PINS = {"admin": "1234", "shop1": "1111"}

# --- SAFE FORM SUBMIT (Demo-safe) ---
def submit_form(api_url, payload):
    """Placeholder URL ആണെങ്കിൽ demo success തരും. Real URL ആണെങ്കിൽ POST ചെയ്യും."""
    if not api_url or "YOUR_" in api_url:
        return True  # 🎭 Demo mode: simulate success
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
    .stApp { background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); color: #fff; }
    [data-testid="stSidebar"] { background: rgba(0,0,0,0.85) !important; }
    .stButton>button { background-color: #00BFFF; color: #000; border-radius: 10px; font-weight: bold; }
    .stDownloadButton>button { background-color: #00FF7F; color: #000; border-radius: 10px; font-weight: bold; }
    .banner { background: rgba(0, 0, 0, 0.7); padding: 25px; border-radius: 15px; border-left: 10px solid #00BFFF; text-align: center; margin-bottom: 25px; }
    h1, h2, h3, p, label { color: white !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

if 'auth' not in st.session_state:
    st.session_state.auth, st.session_state.user = False, ""

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
    except:
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
    except:
        return pd.DataFrame({
            'Date': ['2026-11-01', '2026-11-02', '2026-11-03'],
            'Item': ['Sugar', 'Sugar', 'Milk'],
            'Quantity': [100, 20, 50],
            'Type': ['Stock In', 'Stock Out', 'Stock In']
        })

def generate_pdf(df, title, columns):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(190, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 10)
    col_width = 190 / len(columns)
    for col in columns:
        pdf.cell(col_width, 10, txt=str(col), border=1, align='C')
    pdf.ln()
    pdf.set_font("Arial", size=9)
    for _, row in df.iterrows():
        for col in columns:
            val = str(row[col]).encode('ascii', 'ignore').decode('ascii')
            pdf.cell(col_width, 10, txt=val, border=1)
        pdf.ln()
    return bytes(pdf.output())

# --- 🔒 LOGIN ---
if not st.session_state.auth:
    st.markdown('<div style="max-width:400px; margin:auto; margin-top:100px; background:rgba(0,0,0,0.8); padding:30px; border-radius:20px;">', unsafe_allow_html=True)
    st.subheader("🔐 PAICHI BUSINESS LOGIN")
    u = st.selectbox("👤 Select Role", ["admin", "shop1"]).lower()
    pin = st.text_input("🔑 Enter PIN (admin:1234, shop1:1111)", type="password", max_chars=4)
    if st.button("LOGIN"):
        if USER_PINS.get(u) == pin:
            st.session_state.auth, st.session_state.user = True, u
            st.rerun()
        else:
            st.error("❌ Incorrect PIN!")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    st.sidebar.title(f"👋 Welcome, {st.session_state.user.capitalize()}")
    menu = ["📊 Dashboard", "💰 Add Finance", "📦 Stock Management", "👨‍💼 Staff Salary"]
    page = st.sidebar.radio("Menu", menu)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.rerun()

    df_fin = load_finance_data()
    t_in, t_out = df_fin['Credit'].sum(), df_fin['Debit'].sum()
    bal = t_in - t_out

    # --- 1. DASHBOARD ---
    if page == "📊 Dashboard":
        st.markdown(f'<div class="banner"><span style="font-size:20px; color:#00BFFF;">Total Business Balance</span><br><span style="font-size:40px; color:#FFF;">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
        st.subheader("📈 Shop-wise Performance")
        if not df_fin.empty:
            shop_data = df_fin.groupby('Shop Name')[['Credit', 'Debit']].sum().reset_index()
            fig = px.bar(shop_data, x='Shop Name', y=['Credit', 'Debit'], barmode='group',
                         color_discrete_sequence=['#00FF00', '#FF3131'], title="Credit vs Debit")
            st.plotly_chart(fig, use_container_width=True)
            st.subheader("📋 Recent Transactions")
            st.dataframe(df_fin.tail(10).iloc[::-1], use_container_width=True)

    # --- 2. ADD FINANCE ---
    elif page == "💰 Add Finance":
        st.title("💰 Finance Entry")
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
                        payload = {
                            "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                            "entry.2013476337": f"[{shop}] {it}",
                            "entry.1460982454": am if "Debit" in ty else 0,
                            "entry.1221658767": 0 if "Debit" in ty else am
                        }
                        if submit_form(FORM_API, payload):
                            st.success("Saved! ✅")
                            st.cache_data.clear()
                    except ValueError:
                        st.error("❗ Invalid amount format.")

    # --- 3. STOCK MANAGEMENT ---
    elif page == "📦 Stock Management":
        st.title("📦 Stock & Inventory")
        df_stk = load_stock_data()
        tab1, tab2, tab3 = st.tabs(["📊 Current Stock", "➕ Add Entry", "📄 Item History & PDF"])

        with tab1:
            if not df_stk.empty:
                s = df_stk.copy()
                s['In'] = s.apply(lambda x: x['Quantity'] if x['Type'] == 'Stock In' else 0, axis=1)
                s['Out'] = s.apply(lambda x: x['Quantity'] if x['Type'] == 'Stock Out' else 0, axis=1)
                final_stk = s.groupby('Item')[['In', 'Out']].sum().reset_index()
                final_stk['Available Stock'] = final_stk['In'] - final_stk['Out']
                st.dataframe(final_stk[['Item', 'Available Stock']], use_container_width=True)
            else:
                st.info("No stock data.")

        with tab2:
            with st.form("stock_form", clear_on_submit=True):
                item_name = st.text_input("Item Name")
                qty = st.number_input("Quantity", min_value=1.0)
                stock_type = st.radio("Type", ["Stock In", "Stock Out"], horizontal=True)
                if st.form_submit_button("SAVE STOCK"):
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": item_name,
                        "entry.1460982454": qty,
                        "entry.1221658767": stock_type
                    }
                    if submit_form(STOCK_FORM_API, payload):
                        st.success("Stock Updated! ✅")
                        st.cache_data.clear()

        with tab3:
            if not df_stk.empty:
                selected_item = st.selectbox("Select Item", df_stk['Item'].unique())
                item_history = df_stk[df_stk['Item'] == selected_item]
                st.dataframe(item_history[['Date', 'Type', 'Quantity']], use_container_width=True)
                pdf_b = generate_pdf(item_history, f"Stock History: {selected_item}", ['Date', 'Type', 'Quantity'])
                st.download_button(f"📥 Download {selected_item} PDF", pdf_b, f"{selected_item}_Stock.pdf", "application/pdf")

    # --- 4. STAFF SALARY ---
    elif page == "👨‍💼 Staff Salary":
        st.title("👨‍💼 Staff Salary Management")
        with st.expander("പുതിയ ശമ്പളം നൽകുക (Add New Salary)"):
            with st.form("salary_form", clear_on_submit=True):
                shop = st.selectbox("Select Shop", ["Shop 1", "Shop 2"])
                emp_name = st.text_input("Employee Name")
                sal_amt = st.number_input("Salary Amount", min_value=1.0)
                sal_month = st.selectbox("Month", ["November 2026", "October 2026"])
                if st.form_submit_button("PAY SALARY"):
                    payload = {
                        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
                        "entry.2013476337": f"[{shop}] Salary: {emp_name} ({sal_month})",
                        "entry.1460982454": sal_amt,
                        "entry.1221658767": 0
                    }
                    if submit_form(FORM_API, payload):
                        st.success(f"✅ {emp_name}-ന്റെ ശമ്പളം വിജയകരമായി നൽകി!")
                        st.cache_data.clear()

        st.divider()
        st.subheader("📄 Salary History & PDF")
        if not df_fin.empty:
            sal_df = df_fin[df_fin['Item'].str.contains('Salary', case=False, na=False)].copy()
            if not sal_df.empty:
                sal_df['Employee'] = sal_df['Item'].apply(lambda x: x.split(':')[1].split('(')[0].strip() if ':' in x else "Unknown")
                selected_emp = st.selectbox("Select Staff Member", sal_df['Employee'].unique())
                emp_history = sal_df[sal_df['Employee'] == selected_emp]
                st.dataframe(emp_history[['Date', 'Shop Name', 'Item', 'Debit']], use_container_width=True)
                pdf_b = generate_pdf(emp_history, f"Salary Report: {selected_emp}", ['Date', 'Shop Name', 'Debit'])
                st.download_button(f"📥 Download {selected_emp}'s Salary PDF", pdf_b, f"{selected_emp}_Salary.pdf", "application/pdf")
            else:
                st.info("No salary records found.")