import streamlit as st

st.title("PAICHI PANTHER 🐾")
st.write("ഹലോ ഫൈസൽ, പൈത്തൺ പഠനത്തിലേക്ക് സ്വാഗതം!")

name = "Faisal"
if st.button('Click Me'):
    st.success(f"Hello {name}, your app is working perfectly!")
import streamlit as st

st.title("PAICHI PANTHER 🐾")

# യൂസറിൽ നിന്ന് പേര് വാങ്ങുന്നുimport streamlit as st

st.title("PAICHI PANTHER 🐾")

st.header("📈 ട്രേഡിംഗ് ലാഭം കണക്കാക്കാം")

# നമ്പറുകൾ ഇൻപുട്ട് ആയി വാങ്ങുന്നു
buy_price = st.number_input("വാങ്ങിയ വില (Buy Price):", value=0.0)
sell_price = st.number_input("വിറ്റ വില (Sell Price):", value=0.0)
quantity = st.number_input("എണ്ണം (Quantity):", value=1)

# ലാഭം കണക്കുകൂട്ടുന്നു
profit = (sell_price - buy_price) * quantity

if st.button('ലാഭം നോക്കാം'):
    if profit > 0:
        st.success(f"അടിപൊളി! നിന്റെ ലാഭം: {profit}")
    elif profit < 0:
        st.error(f"സാരമില്ല, നിന്റെ നഷ്ടം: {profit}")
    else:
        st.info("ലാഭവും നഷ്ടവുമില്ല!")
user_name = st.text_input("നിങ്ങളുടെ പേര് ഇവിടെ ടൈപ്പ് ചെയ്യൂ:")

# ബട്ടൺ അമർത്തുമ്പോൾ മറുപടി നൽകുന്നു
if st.button('സ്വാഗതം പറയൂ'):
    if user_name:
        st.success(f"ഹലോ {user_name}, PAICHI PANTHER ആപ്പിലേക്ക് സ്വാഗതം!")
    else:
        st.warning("ദയവായി ഒരു പേര് ടൈപ്പ് ചെയ്യൂ.")
