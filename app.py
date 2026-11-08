import pandas as pd
import requests
import random
import os
from fpdf import FPDF
from groq import Groq
import streamlit as st
from datetime import datetime
import json

CSV_URL = "YOUR_FINANCE_SHEET_CSV_LINK"
FORM_API = "YOUR_FINANCE_FORM_API"
STOCK_CSV_URL = "YOUR_STOCK_SHEET_CSV_LINK"
STOCK_FORM_API = "YOUR_STOCK_FORM_API"

USER_PINS = {"admin": "1234", "shop1": "1111"}

try:
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    GROQ_API_KEY = ""

VISION_MODEL = "qwen/qwen3.8-27b"
AGENT_MODEL  = "openai/gpt-oss-120b"

def submit_form(api_url, payload):
    if not api_url or "YOUR_" in api_url: return True
    try:
        r = requests.post(api_url, data=payload, timeout=10)
        return r.status_code == 200
    except: return False

def _append_cache_buster(url):
    if not url or "YOUR_" in url: raise ValueError("placeholder")
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
        return pd.DataFrame(columns=['Date', 'Shop Name', 'Item', 'Debit', 'Credit'])

@st.cache_data(ttl=5)
def load_stock_data():
    try:
        df = pd.read_csv(_append_cache_buster(STOCK_CSV_URL))
        df.columns = df.columns.str.strip()
        df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').fillna(0)
        return df
    except Exception:
        return pd.DataFrame(columns=['Date', 'Item', 'Quantity', 'Type'])

def execute_add_finance(shop, item, amount, t_type):
    payload = {
        "entry.1044099436": datetime.now().strftime("%Y-%m-%d"),
        "entry.2013476337": f"[{shop}] {item}",
        "entry.1460982454": amount if t_type == "Debit" else 0,
        "entry.1221658767": 0 if t_type == "Debit" else amount
    }
    if submit_form(FORM_API, payload):
        load_finance_data.clear()
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
        load_stock_data.clear()
        return "Success"
    return "Failed"

def _find_unicode_font():
    candidates = ["/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf", "C:/Windows/Fonts/arial.ttf"]
    for p in candidates:
        if os.path.exists(p): return p
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
        except: pass

    pdf.set_font("UFont" if has_unicode else "Helvetica", size=14)
    pdf.cell(190, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("UFont" if has_unicode else "Helvetica", size=10)
    col_width = 190 / len(columns)
    for col in columns: pdf.cell(col_width, 10, txt=str(col), border=1, align='C')
    pdf.ln()
    pdf.set_font("UFont" if has_unicode else "Helvetica", size=9)
    def _safe(v):
        s = str(v)
        return s if has_unicode else s.encode('ascii', 'ignore').decode('ascii')
    for _, row in df.iterrows():
        for col in columns: pdf.cell(col_width, 10, txt=_safe(row[col]), border=1)
        pdf.ln()
    return bytes(pdf.output())

def _parse_employee(item_str):
    try:
        if ':' not in item_str: return "Unknown"
        part = item_str.split(':', 1)[1]
        return part.split('(')[0].strip() or "Unknown"
    except: return "Unknown"

def process_ai_agent(prompt_text):
    client = Groq(api_key=GROQ_API_KEY)
    tools = [
        {"type": "function", "function": {"name": "add_finance", "description": "Add finance", "parameters": {"type": "object", "properties": {"shop": {"type": "string", "enum": ["Shop 1", "Shop 2"]}, "item": {"type": "string"}, "amount": {"type": "number"}, "type": {"type": "string", "enum": ["Debit", "Credit"]}}, "required": ["shop", "item", "amount", "type"]}}},
        {"type": "function", "function": {"name": "add_stock", "description": "Add stock", "parameters": {"type": "object", "properties": {"item_name": {"type": "string"}, "qty": {"type": "number"}, "stock_type": {"type": "string", "enum": ["Stock In", "Stock Out"]}}, "required": ["item_name", "qty", "stock_type"]}}}
    ]
    sys_ins = f"നീ ഒരു AI ആണ്. ബാലൻസ്: ₹{st.session_state.get('current_bal', 0):,.2f}. മലയാളത്തിൽ മറുപടി നൽകുക."
    messages = [{"role": "system", "content": sys_ins}] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.get("messages", [])[-4:]] + [{"role": "user", "content": prompt_text}]
    
    response = client.chat.completions.create(model=AGENT_MODEL, messages=messages, tools=tools, tool_choice="auto")
    msg = response.choices[0].message
    tool_used = False
    if msg.tool_calls:
        tool_used = True
        replies = []
        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)
            if tc.function.name == "add_finance":
                res = execute_add_finance(args["shop"], args["item"], args["amount"], args["type"])
                replies.append(f"✅ {args['shop']}-ൽ '{args['item']}' എൻട്രി ഇട്ടു!" if res == "Success" else "❌ എൻട്രി ഇടാൻ പറ്റിയില്ല.")
            elif tc.function.name == "add_stock":
                res = execute_add_stock(args["item_name"], args["qty"], args["stock_type"])
                replies.append(f"✅ {args['item_name']} സ്റ്റോക്ക് അപ്ഡേറ്റ് ചെയ്തു!" if res == "Success" else "❌ സ്റ്റോക്ക് അപ്ഡേറ്റ് പറ്റിയില്ല.")
        ai_reply = "\n\n".join(replies)
    else:
        ai_reply = msg.content or ""
    return ai_reply, tool_used