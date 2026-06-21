import streamlit as st
import yt_dlp
import os

# ആപ്പിന്റെ തലക്കെട്ട് (Title)
st.title("YouTube Video Downloader 🚀")
st.write("യൂട്യൂബ് ലിങ്ക് താഴെ പേസ്റ്റ് ചെയ്ത് വീഡിയോ ഡൗൺലോഡ് ചെയ്യാം.")

# വെബ്സൈറ്റിൽ ലിങ്ക് കൊടുക്കാനുള്ള ബോക്സ്
url = st.text_input("YouTube ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
    if url:
        st.info("ഡൗൺലോഡ് തുടങ്ങുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # വീഡിയോ വിവരങ്ങൾ എടുക്കുന്നു
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            st.success("വീഡിയോ വിജയകരമായി ഡൗൺലോഡ് ചെയ്തു!")
            
            # ഡൗൺലോഡ് ചെയ്ത ഫയൽ യൂസർക്ക് ഫോണിലേക്ക് സേവ് ചെയ്യാൻ ബട്ടൺ നൽകുന്നു
            with open(filename, "rb") as file:
                st.download_button(
                    label="ഫോണിലേക്ക് സേവ് ചെയ്യുക ⬇️",
                    data=file,
                    file_name=filename,
                    mime="video/mp4"
                )
                
            # ഉപയോഗത്തിന് ശേഷം സെർവറിൽ നിന്ന് ഫയൽ ഡിലീറ്റ് ചെയ്യുന്നു
            os.remove(filename)
                
        except Exception as e:
            st.error(f"എന്തോ തകരാർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ഒരു ലിങ്ക് നൽകുക!")
