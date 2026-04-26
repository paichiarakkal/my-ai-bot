import streamlit as st

def family_vault():
    st.title("🐾 PAICHI PANTHER - Family Vault")
    
    password = st.text_input("പാസ്‌വേഡ് നൽകുക", type="password")
    
    if password == "1234": # നിനക്ക് ഇഷ്ടമുള്ള പാസ്‌വേഡ് മാറ്റാം
        st.success("സ്വാഗതം ഫൈസൽ!")
        st.subheader("സുപ്രധാന രേഖകൾ")
        st.write("- ഫഹിമയുടെ രേഖകൾ")
        st.write("- ഫിസയുടെ രേഖകൾ")
        st.write("- ഷബാനയുടെ രേഖകൾ")
        # ഇവിടെ ഫയലുകൾ അപ്‌ലോഡ് ചെയ്യാനുള്ള ഓപ്ഷനും നൽകാം
    elif password != "":
        st.error("തെറ്റായ പാസ്‌വേഡ്!")

family_vault()
