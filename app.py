import streamlit as st

st.title("PAICHI PANTHER 🐾")
st.write("ഹലോ ഫൈസൽ, പൈത്തൺ പഠനത്തിലേക്ക് സ്വാഗതം!")

name = "Faisal"
if st.button('Click Me'):
    st.success(f"Hello {name}, your app is working perfectly!")
import streamlit as st

st.title("PAICHI PANTHER 🐾")

# യൂസറിൽ നിന്ന് പേര് വാങ്ങുന്നു
user_name = st.text_input("നിങ്ങളുടെ പേര് ഇവിടെ ടൈപ്പ് ചെയ്യൂ:")

# ബട്ടൺ അമർത്തുമ്പോൾ മറുപടി നൽകുന്നു
if st.button('സ്വാഗതം പറയൂ'):
    if user_name:
        st.success(f"ഹലോ {user_name}, PAICHI PANTHER ആപ്പിലേക്ക് സ്വാഗതം!")
    else:
        st.warning("ദയവായി ഒരു പേര് ടൈപ്പ് ചെയ്യൂ.")
