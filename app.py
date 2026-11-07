import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import random
import plotly.express as px
from fpdf import FPDF
import json
import base64
import os
import cv2
import tempfile
import hashlib
from groq import Groq

# --- CONFIG (നിങ്ങളുടെ ലിങ്കുകൾ ഇവിടെ ചേർക്കുക) ---
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
WHISPER_MODEL = "whisper-large-v3"

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

# --- SESSION STATE INIT ---
if 'auth' not in st.session_state:
    st.session_state.auth, st.session_state.user = False, ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "audio_counter" not in st.session_state:
    st.session_state.audio_counter = 0
if "last_audio_hash" not in st.session_state:
    st.session_state.last_audio_hash = None
if "order_counter" not in st.session_state:
    st.session_state.order_counter = 0

def flash_success(msg):
    st.session_state["_flash"] = msg

def show_flash():
    msg = st.session_state.pop("_flash", None)
    if msg:
        st.success(msg)

# --- HELPER: CSV Load ---
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

# --- HELPER: PDF Generation ---
def _find_unicode_font():
    candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansMalayalam-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
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

    pdf.set_font("UFont" if has_unicode else "Helvetica", size=14)
    pdf.cell(190, 10, txt=title, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("UFont" if has_unicode else "Helvetica", size=10)
    
    col_width = 190 / len(columns)
    for col in columns:
        pdf.cell(col_width, 10, txt=str(col), border=1, align='C')
    pdf.ln()
    pdf.set_font("UFont" if has_unicode else "Helvetica", size=9)

    def _safe(v):
        s = str(v)
        return s if has_unicode else s.encode('ascii', 'ignore').decode('ascii')

    for _, row in df.iterrows():
        for col in columns:
            pdf.cell(col_width, 10, txt=_safe(row[col]), border=1)
        pdf.ln()
    return bytes(pdf.output())

# ============================================
# 🤖 AI & VISION HELPERS
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
                    "item":   {"type": "string"},
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

def extract_frames_from_video(video_bytes, num_frames=3):
    try:
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(video_bytes)
        tfile.close()
        cap = cv2.VideoCapture(tfile.name)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames = []
        if total_frames > 0:
            step = max(1, total_frames // num_frames)
            for i in range(0, total_frames, step):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    h, w = frame.shape[:2]
                    if h > 500:
                        ratio = 500 / h
                        frame = cv2.resize(frame, (int(w * ratio), 500))
                    _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                    frames.append(buffer.tobytes())
                if len(frames) >= num_frames:
                    break
        cap.release()
        os.unlink(tfile.name)
        return frames
    except Exception:
        return []

def analyze_images_with_groq(images_bytes_list):
    if not GROQ_API_KEY:
        return False, "Groq API Key missing!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        def _try_analyze(images):
            prompt_text_en = (
                "Analyze these shop CCTV frames. You are a smart business AI. "
                "1. FOOTFALL: Count how many people are visible, where they are, and what they are doing. "
                "2. STOCK/ITEMS: Identify any visible products, items, or stock on shelves. "
                "3. REPORT: Provide a short business activity report covering both people and stock."
            )
            content_list = [{"type": "text", "text": prompt_text_en}]
            for img_bytes in images:
                b64_img = base64.b64encode(img_bytes).decode('utf-8')
                content_list.append({
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}
                })

            completion = client.chat.completions.create(
                model=VISION_MODEL,
                messages=[{"role": "user", "content": content_list}],
                max_tokens=500
            )
            return completion.choices[0].message.content

        try:
            english_report = _try_analyze(images_bytes_list)
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e):
                english_report = _try_analyze(images_bytes_list[:1])
            else:
                raise e

        prompt_text_ml = (
            "You are an expert translator. Translate the following business CCTV report into natural, easy-to-understand Malayalam. "
            "Do NOT translate English brand names or product names. Keep the format clean and professional.\n\n"
            f"English Report:\n{english_report}"
        )

        completion_translate = client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[{"role": "user", "content": prompt_text_ml}],
            max_tokens=800
        )
        return True, completion_translate.choices[0].message.content
    except Exception as e:
        return False, f"Vision Analysis Error: {str(e)}"

def analyze_shelf_changes(morning_bytes, evening_bytes):
    if not GROQ_API_KEY:
        return False, "Groq API Key missing!"
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        b64_morning = base64.b64encode(morning_bytes).decode('utf-8')
        b64_evening = base64.b64encode(evening_bytes).decode('utf-8')
        
        prompt_text_en = (
            "You are an expert retail auditor. Compare these two images of the same shelf (Morning vs Evening). "
            "IMPORTANT: If the images are identical or there are NO noticeable changes in the stock, you MUST explicitly say: "
            "'No changes detected. The shelf looks exactly the same.' Do NOT invent or imagine differences. "
            "If there are actual changes, list which items are reduced or moved."
        )
        
        content_list = [
            {"type": "text", "text": prompt_text_en},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_morning}"}},
            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_evening}"}}
        ]
        
        completion_vision = client.chat.completions.create(
            model=VISION_MODEL,
            messages=[{"role": "user", "content": content_list}],
            max_tokens=800,
            temperature=0.1
        )
        english_report = completion_vision.choices[0].message.content

        prompt_text_ml = (
            "You are an expert translator. Translate the following shelf comparison report into natural, easy-to-understand Malayalam. "
            "Do NOT translate English brand names or product names. Keep the format clean and professional.\n\n"
            f"English Report:\n{english_report}"
        )

        completion_translate = client.chat.completions.create(
            model=AGENT_MODEL,
            messages=[{"role": "user", "content": prompt_text_ml}],
            max_tokens=800
        )
        return True, completion_translate.choices[0].message.content
    except Exception as e:
        return False, f"Shelf Analysis Error: {str(e)}"

def _parse_employee(item_str):
    try:
        if ':' not in item_str: return "Unknown"
        part = item_str.split(':', 1)[1]
        return part.split('(')[0].strip() or "Unknown"
    except Exception:
        return "Unknown"

def process_ai_agent(prompt_text):
    client = Groq(api_key=GROQ_API_KEY)
    system_instruction = (
        f"നീ ഒരു ബിസിനസ്സ് മാനേജർ AI ആണ്. ബാലൻസ്: ₹{st.session_state.get('current_bal', 0):,.2f}. "
        "ഫിനാൻസിന് add_finance-ഉം സ്റ്റോക്കിന് add_stock-ഉം ഉപയോഗിക്കുക. മലയാളത്തിൽ മറുപടി നൽകുക. "
        "പ്രധാനം: ഉപയോക്താവ് വ്യക്തമായി ഒരു സാധനത്തിന്റെ പേരും അതിന്റെ എണ്ണവും (quantity) പറഞ്ഞാൽ മാത്രമേ add_stock ടൂൾ ഉപയോഗിക്കാവൂ."
    )
    
    messages_for_api = [{"role": "system", "content": system_instruction}]
    for m in st.session_state.messages[-4:]:
        messages_for_api.append({"role": m["role"], "content": m["content"]})
    
    messages_for_api.append({"role": "user", "content": prompt_text})

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
        replies = []
        for tool_call in response_message.tool_calls:
            try:
                args = json.loads(tool_call.function.arguments)
            except:
                continue
            if tool_call.function.name == "add_finance":
                res = execute_add_finance(args["shop"], args["item"], args["amount"], args["type"])
                replies.append(f"✅ {args['shop']}-ൽ '{args['item']}' എൻട്രി ഷീറ്റിൽ ഇട്ടു!" if res == "Success" else "❌ എൻട്രി ഇടാൻ പറ്റിയില്ല.")
            elif tool_call.function.name == "add_stock":
                res = execute_add_stock(args["item_name"], args["qty"], args["stock_type"])
                replies.append(f"✅ {args['item_name']} സ്റ്റോക്ക് അപ്ഡേറ്റ് ചെയ്തു!" if res == "Success" else "❌ സ്റ്റോക്ക് അപ്ഡേറ്റ് പറ്റിയില്ല.")
        ai_reply = "\n\n".join(replies)
    else:
        ai_reply = response_message.content or ""

    return ai_reply, tool_used

def process_voice_order(transcript):
    client = Groq(api_key=GROQ_API_KEY)
    prompt = (
        f"A customer just said this order in a shop: '{transcript}'. "
        "Extract the item names and quantities. "
        "Return ONLY a valid JSON array. Do not add any markdown or text outside the JSON. "
        "Format: [{\"item\": \"Sugar\", \"qty\": 2}]"
    )
    
    response = client.chat.completions.create(
        model=AGENT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300
    )
    
    result_text = response.choices[0].message.content.strip()
    if result_text.startswith("```json"):
        result_text = result_text[7:-3]
        
    try:
        order_items = json.loads(result_text)
        return True, order_items
    except:
        return False, "ഓർഡർ കൃത്യമായി മനസ്സിലാക്കാൻ സാധിച്ചില്ല."

# --- 🔒 LOGIN ---
if not st.session_state.auth:
    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.subheader("🔐 PAICHI BUSINESS LOGIN")
        u = st.selectbox("👤 Select Role", ["admin", "shop1"]).lower()
        pin = st.text_input("🔑 Enter PIN", type="password", max_chars=4)
        if st.button("LOGIN"):
            if USER_PINS.get(u) == pin:
                st.session_state.auth, st.session_state.user = True, u
                st.rerun()
            else:
                st.error("❌ Incorrect PIN!")

else:
    st.sidebar.title(f"👋 Welcome, {st.session_state.user.capitalize()}")
    menu = ["📊 Dashboard", "💰 Add Finance", "📦 Stock Management", "🧾 Bill Scanner", "🗣️ Voice Order", "🛒 Shelf Monitor", "👨‍💼 Staff Salary", "🤖 AI Agent", "🎥 CCTV AI Vision"]
    page = st.sidebar.radio("Menu", menu)

    if st.sidebar.button("Logout"):
        st.session_state.auth = False
        st.session_state.messages = []
        st.rerun()

    df_fin = load_finance_data()
    df_stk = load_stock_data()
    
    t_in = df_fin['Credit'].sum() if not df_fin.empty else 0
    t_out = df_fin['Debit'].sum() if not df_fin.empty else 0
    bal = t_in - t_out
    st.session_state['current_bal'] = bal

    # --- 1. DASHBOARD ---
    if page == "📊 Dashboard":
        st.markdown(f'<div class="banner"><span class="b-label">Total Business Balance</span><br><span class="b-value">₹{bal:,.2f}</span></div>', unsafe_allow_html=True)
        st.subheader("📈 Shop-wise Performance")
        if not df_fin.empty:
            shop_data = df_fin.groupby('Shop Name')[['Credit', 'Debit']].sum().reset_index()
            fig = px.bar(shop_data, x='Shop Name', y=['Credit', 'Debit'], barmode='group', color_discrete_sequence=['#00FF00', '#FF3131'])
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df_fin.tail(10).iloc[::-1], use_container_width=True)
        else:
            st.info("ഇതുവരെ ഒരു ഇടപാടും നടന്നിട്ടില്ല.")

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
                if clean:
                    try:
                        am = float(clean)
                        if execute_add_finance(shop, it, am, "Debit" if "Debit" in ty else "Credit") == "Success":
                            flash_success("Saved to Google Sheet! ✅")
                            st.rerun()
                        else:
                            st.error("❌ Save failed.")
                    except ValueError:
                        st.error("❗ Invalid amount.")
                else:
                    st.error("❗ Enter amount.")

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
                st.info("സ്റ്റോക്ക് വിവരങ്ങൾ ലഭ്യമല്ല.")
        with tab2:
            with st.form("stock_form", clear_on_submit=True):
                item_name  = st.text_input("Item Name")
                qty        = st.number_input("Quantity", min_value=1.0)
                stock_type = st.radio("Type", ["Stock In", "Stock Out"], horizontal=True)
                if st.form_submit_button("SAVE STOCK"):
                    if execute_add_stock(item_name, qty, stock_type) == "Success":
                        flash_success("Stock Updated in Google Sheet! ✅")
                        st.rerun()
        with tab3:
            if not df_stk.empty:
                selected_item = st.selectbox("Select Item", df_stk['Item'].unique())
                item_history = df_stk[df_stk['Item'] == selected_item]
                st.dataframe(item_history[['Date', 'Type', 'Quantity']], use_container_width=True)
                pdf_b = generate_pdf(item_history, f"Stock History: {selected_item}", ['Date', 'Type', 'Quantity'])
                st.download_button(f"📥 Download {selected_item} PDF", pdf_b, f"{selected_item}_Stock.pdf", "application/pdf")

    # --- 4. BILL SCANNER ---
    elif page == "🧾 Bill Scanner":
        st.title("🧾 Bill / Stock Photo Scanner")
        st.write("ബില്ലിന്റെയോ സാധനങ്ങളുടെയോ ഫോട്ടോ എടുത്ത് അപ്‌ലോഡ് ചെയ്യുക. AI അതിലെ സാധനങ്ങളും വിലയും വായിച്ച് തനിയെ ഷീറ്റിൽ എൻട്രി ഇടും.")
        
        if not GROQ_API_KEY:
            st.error("Groq API Key ലഭ്യമല്ല!")
            
        bill_file = st.file_uploader("Upload Bill Photo", type=["jpg", "jpeg", "png"])
        
        if bill_file is not None:
            st.image(bill_file, caption="Uploaded Bill", use_container_width=True)
            shop_select = st.selectbox("ഏത് കടയുടെ ബില്ലാണ്? (Select Shop)", ["Shop 1", "Shop 2"])
            
            if st.button("🔍 വായിച്ച് എൻട്രി ഇടുക (Extract & Add)"):
                with st.spinner("AI ബിൽ വായിക്കുന്നു..."):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        b64_img = base64.b64encode(bill_file.getvalue()).decode('utf-8')
                        
                        prompt = (
                            "Analyze this bill or stock image. Extract the item name, quantity, and total price. "
                            "Return ONLY a valid JSON array. Do not add any markdown or text outside the JSON. "
                            "Format: [{\"item\": \"Sugar 1kg\", \"qty\": 5, \"price\": 250}]"
                        )
                        
                        response = client.chat.completions.create(
                            model=VISION_MODEL,
                            messages=[{
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": prompt},
                                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_img}"}}
                                ]
                            }],
                            max_tokens=1000
                        )
                        
                        result_text = response.choices[0].message.content.strip()
                        if result_text.startswith("```json"):
                            result_text = result_text[7:-3]
                            
                        items_data = json.loads(result_text)
                        st.success(f"✅ {len(items_data)} സാധനങ്ങൾ കണ്ടെത്തി. ഷീറ്റിലേക്ക് അയക്കുന്നു...")
                        
                        for item in items_data:
                            execute_add_stock(item['item'], item['qty'], "Stock In")
                            execute_add_finance(shop_select, f"Purchase: {item['item']}", item['price'], "Debit")
                        
                        st.balloons()
                        st.success("🎉 എല്ലാം വിജയകരമായി ഷീറ്റിൽ എൻട്രി ഇട്ടു!")
                        
                    except Exception as e:
                        st.error(f"❌ വായിക്കാൻ സാധിച്ചില്ല. ദയവായി വ്യക്തമായ ഫോട്ടോ നൽകുക. (Error: {e})")

    # --- 5. VOICE ORDER KIOSK ---
    elif page == "🗣️ Voice Order":
        st.title("🗣️ AI Voice Order Kiosk")
        st.write("കസ്റ്റമറിനോട് സംസാരിക്കാൻ പറയുക. AI ഓർഡർ കേട്ട് കൃത്യമായി എഴുതി എടുക്കും.")

        current_order_key = f"order_audio_{st.session_state.order_counter}"
        audio_order = st.audio_input("🎤 ഓർഡർ റെക്കോർഡ് ചെയ്യാൻ ഇവിടെ അമർത്തുക", key=current_order_key)

        if audio_order:
            with st.spinner("AI കസ്റ്റമറുടെ ഓർഡർ കേൾക്കുന്നു..."):
                try:
                    client = Groq(api_key=GROQ_API_KEY)
                    transcription = client.audio.transcriptions.create(
                        file=(audio_order.name, audio_order.getvalue()),
                        model=WHISPER_MODEL,
                        response_format="text",
                        prompt="Shop 1, Shop 2, Sales, Expense, Salary, Stock, Rupees, Aayi, Undayi, Sugar, Tea, Milk, 1kg, 2kg."
                    )
                    transcript = transcription.strip()
                    
                    if transcript:
                        st.info(f"🗣️ കസ്റ്റമർ പറഞ്ഞത്: **{transcript}**")
                        ok, order_data = process_voice_order(transcript)
                        
                        if ok and order_data:
                            st.success("✅ ഓർഡർ വിജയകരമായി എടുത്തു!")
                            st.subheader("📝 Order Summary")
                            df_order = pd.DataFrame(order_data)
                            st.dataframe(df_order, use_container_width=True)
                            
                            pdf_b = generate_pdf(df_order, "Customer Order Receipt", ['item', 'qty'])
                            st.download_button("📥 Download Order Receipt (PDF)", pdf_b, "Order_Receipt.pdf", "application/pdf")
                            
                            if st.button("✅ Done / അടുത്തത്"):
                                st.session_state.order_counter += 1
                                st.rerun()
                        else:
                            st.error(order_data)
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- 6. SMART SHELF MONITOR ---
    elif page == "🛒 Shelf Monitor":
        st.title("🛒 Smart Shelf Monitor (ഷെൽഫ് മോണിറ്റർ)")
        st.write("കട തുറക്കുമ്പോഴും (രാവിലെ) അടയ്ക്കുമ്പോഴും (വൈകുന്നേരം) ഷെൽഫിന്റെ ഫോട്ടോ എടുത്ത് അപ്‌ലോഡ് ചെയ്യുക. AI രണ്ടും തമ്മിൽ താരതമ്യം ചെയ്ത് എന്തൊക്കെ തീർന്നു എന്ന് പറയും.")

        if not GROQ_API_KEY:
            st.error("Groq API Key ലഭ്യമല്ല!")

        col1, col2 = st.columns(2)
        with col1:
            morning_file = st.file_uploader("🌅 രാവിലെയുള്ള ഫോട്ടോ (Morning Photo)", type=["jpg", "jpeg", "png"])
            if morning_file:
                st.image(morning_file, caption="Morning Shelf", use_container_width=True)
                
        with col2:
            evening_file = st.file_uploader("🌙 വൈകുന്നേരത്തെ ഫോട്ടോ (Evening Photo)", type=["jpg", "jpeg", "png"])
            if evening_file:
                st.image(evening_file, caption="Evening Shelf", use_container_width=True)

        if morning_file and evening_file:
            if st.button("🔍 താരതമ്യം ചെയ്യുക (Compare Shelves)"):
                with st.spinner("AI ഷെൽഫ് പരിശോധിക്കുന്നു..."):
                    ok, analysis_result = analyze_shelf_changes(
                        morning_file.getvalue(), 
                        evening_file.getvalue()
                    )
                    st.subheader("📊 Shelf Analysis Report")
                    if ok:
                        st.success(analysis_result)
                    else:
                        st.error(analysis_result)

    # --- 7. STAFF SALARY ---
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
                    if execute_add_finance(shop, f"Salary: {emp_name} ({sal_month})", sal_amt, "Debit") == "Success":
                        flash_success(f"✅ {emp_name}-ന്റെ ശമ്പളം നൽകി!")
                        st.rerun()
        st.divider()
        if not df_fin.empty:
            sal_df = df_fin[df_fin['Item'].str.contains('Salary', case=False, na=False)].copy()
            if not sal_df.empty:
                sal_df['Employee'] = sal_df['Item'].apply(_parse_employee)
                selected_emp = st.selectbox("Select Staff Member", sal_df['Employee'].unique())
                emp_history = sal_df[sal_df['Employee'] == selected_emp]
                st.dataframe(emp_history[['Date', 'Shop Name', 'Item', 'Debit']], use_container_width=True)
                pdf_b = generate_pdf(emp_history, f"Salary Report: {selected_emp}", ['Date', 'Shop Name', 'Debit'])
                st.download_button(f"📥 Download {selected_emp}'s Salary PDF", pdf_b, f"{selected_emp}_Salary.pdf", "application/pdf")

    # --- 8. AI AGENT (WHATSAPP STYLE) ---
    elif page == "🤖 AI Agent":
        st.title("🤖 PAICHI Business AI")
        st.write("വാട്ട്‌സ്ആപ്പ് പോലെ സംസാരിക്കാം. (ശബ്ദം കേട്ട് കഴിഞ്ഞാൽ മൈക്ക് ഓട്ടോമാറ്റിക് ആയി റീസെറ്റ് ആകും)")

        if not GROQ_API_KEY:
            st.error("Groq API Key ലഭ്യമല്ല!")

        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("🗑️ Clear Chat"):
                st.session_state.messages = []
                st.session_state['audio_counter'] += 1
                st.session_state['last_audio_hash'] = None
                st.rerun()

        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        current_audio_key = f"audio_input_{st.session_state['audio_counter']}"

        st.write("---")
        audio_value = st.audio_input("🎤 റെക്കോർഡ് ചെയ്യാൻ ഇവിടെ അമർത്തുക", key=current_audio_key)
        text_prompt = st.chat_input("ഇവിടെ ടൈപ്പ് ചെയ്യാം...")

        prompt = None

        if audio_value:
            audio_hash = hashlib.md5(audio_value.getvalue()).hexdigest()
            
            if st.session_state.get("last_audio_hash") != audio_hash:
                st.session_state["last_audio_hash"] = audio_hash
                
                with st.spinner("ശബ്ദം കേൾക്കുന്നു..."):
                    try:
                        client = Groq(api_key=GROQ_API_KEY)
                        transcription = client.audio.transcriptions.create(
                            file=(audio_value.name, audio_value.getvalue()),
                            model=WHISPER_MODEL,
                            response_format="text",
                            prompt="Shop 1, Shop 2, Sales, Expense, Salary, Stock, Rupees, Aayi, Undayi, Sugar, Tea, Milk."
                        )
                        prompt = transcription.strip()
                        
                        if prompt and any(u'\u4e00' <= c <= u'\u9fff' for c in prompt):
                            st.warning("⚠️ ശബ്ദം വ്യക്തമല്ല. ദയവായി വീണ്ടും സംസാരിക്കുക.")
                            prompt = None
                            st.session_state['audio_counter'] += 1 
                            st.rerun()
                    except Exception as e:
                        st.error(f"Audio Error: {str(e)}")

        if text_prompt:
            prompt = text_prompt

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.spinner("AI ടൈപ്പ് ചെയ്യുന്നു..."):
                try:
                    ai_reply, tool_used = process_ai_agent(prompt)
                    
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    with st.chat_message("assistant"):
                        st.markdown(ai_reply)
                        
                    st.session_state['audio_counter'] += 1
                    st.rerun()
                except Exception as e:
                    st.error(f"AI Error: {str(e)}")

    # --- 9. CCTV AI VISION ---
    elif page == "🎥 CCTV AI Vision":
        st.title("🎥 CCTV AI Vision & Footfall Monitor")
        st.write("കടയിലെ ഫോട്ടോയോ വീഡിയോയോ അപ്‌ലോഡ് ചെയ്ത് ഫൂട്ട്ഫാളും സ്റ്റോക്കും വിശകലനം ചെയ്യാം.")

        if not GROQ_API_KEY:
            st.error("Groq API Key ലഭ്യമല്ല!")

        uploaded_file = st.file_uploader("Upload Shop CCTV Photo or Video", type=["jpg", "jpeg", "png", "mp4", "avi", "mov"])
        
        if uploaded_file is not None:
            file_type = uploaded_file.type
            
            if "image" in file_type:
                st.image(uploaded_file, caption="Uploaded Snapshot", use_container_width=True)
                images_to_analyze = [uploaded_file.getvalue()]
            
            elif "video" in file_type:
                st.video(uploaded_file)
                with st.spinner("വീഡിയോയിൽ നിന്ന് ഫ്രെയിമുകൾ എടുക്കുന്നു..."):
                    images_to_analyze = extract_frames_from_video(uploaded_file.getvalue(), num_frames=3)
                    if not images_to_analyze:
                        st.error("❌ വീഡിയോയിൽ നിന്ന് ഫ്രെയിമുകൾ എടുക്കാൻ സാധിച്ചില്ല.")
                        st.stop()
                    st.success(f"✅ വീഡിയോയിൽ നിന്ന് {len(images_to_analyze)} ഫ്രെയിമുകൾ എടുത്തു.")

            if st.button("🔍 Analyze with AI"):
                with st.spinner("AI വിശകലനം ചെയ്യുന്നു..."):
                    ok, analysis_result = analyze_images_with_groq(images_to_analyze)
                    st.subheader("📊 AI Analysis Report")
                    if ok:
                        st.success(analysis_result)
                    else:
                        st.error(analysis_result)