import streamlit as st
from google import genai

# 1. പ്ലാറ്റ്‌ഫോം സെറ്റിംഗ്സ്
st.set_page_config(page_title="PAICHI TRADING HUB", layout="wide")

# സൈഡ്‌ബാറിൽ മെനു ഉണ്ടാക്കുന്നു
st.sidebar.title("📈 PAICHI HUB")
page = st.sidebar.radio("Go to:", ["Dashboard", "AI Learning Zone", "Market Watch"])

# API Key സെറ്റപ്പ്
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    # നിന്റെ പുതിയ കീ ഇവിടെ നൽകാം
    api_key = "AIzaSyCs2bRTki97CGu_Jgn67U_JAHdt1c1It-8"

client = genai.Client(api_key=api_key)

# --- പേജുകൾ ---

if page == "Dashboard":
    st.title("🚀 PAICHI TRADING HUB")
    st.write("നിന്റെ ട്രേഡിംഗ് യാത്ര ഇവിടെ തുടങ്ങുന്നു. നമുക്ക് ഒരുമിച്ച് പഠിക്കാം!")
    
    # ഒരു ചെറിയ സ്റ്റാറ്റിസ്റ്റിക്സ് ബോക്സ് (ഉദാഹരണത്തിന്)
    col1, col2 = st.columns(2)
    col1.metric("Today's Focus", "Crude Oil")
    col2.metric("Target", "Pro Trader")

elif page == "AI Learning Zone":
    st.title("🤖 AI Learning Assistant")
    st.write("പൈത്തണിനെക്കുറിച്ചോ ട്രേഡിംഗിനെക്കുറിച്ചോ എന്ത് സംശയവും ഇവിടെ ചോദിക്കാം.")
    
    user_input = st.text_input("നിന്റെ ചോദ്യം ഇവിടെ ടൈപ്പ് ചെയ്യൂ:")
    
    if st.button("ചോദിക്കുക"):
        if user_input:
            with st.spinner("ജെമിനി ആലോചിക്കുന്നു..."):
                try:
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=user_input
                    )
                    st.success("മറുപടി:")
                    st.write(response.text)
                except Exception as e:
                    st.error(f"Error: {e}")

elif page == "Market Watch":
    st.title("📊 Market Data (Coming Soon)")
    st.info("ലൈവ് ഡാറ്റ ഇവിടെ ഉടനെ ലഭ്യമാകും. നമ്മൾ ഇത് ഡെവലപ്പ് ചെയ്തുകൊണ്ടിരിക്കുകയാണ്!")
