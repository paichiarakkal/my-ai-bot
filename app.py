import streamlit as st

st.title("PAICHI PANTHER 🐾")
st.write("ഹലോ ഫൈസൽ, പൈത്തൺ പഠനത്തിലേക്ക് സ്വാഗതം!")

name = "Faisal"
if st.button('Click Me'):
    st.success(f"Hello {name}, your app is working perfectly!")
