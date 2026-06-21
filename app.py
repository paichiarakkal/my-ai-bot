import streamlit as st
import yt_dlp
import os

# ആപ്പിന്റെ തലക്കെട്ട് മാറ്റാം
st.title("Instagram Reels Downloader 🎬")
st.write("ഇൻസ്റ്റാഗ്രാം റീൽസ് ലിങ്ക് താഴെ പേസ്റ്റ് ചെയ്ത് വീഡിയോ ഫോണിലേക്ക് ഡൗൺലോഡ് ചെയ്യാം.")

# റീൽസ് ലിങ്ക് വാങ്ങാനുള്ള ബോക്സ്
url = st.text_input("Instagram Reels ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'insta_video.%(ext)s', # ഫയൽ നെയിം സെറ്റ് ചെയ്യുന്നു
            'nocheckcertificate': True,
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # വീഡിയോ ഡൗൺലോഡ് ചെയ്യുന്നു
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            st.success("വീഡിയോ റെഡിയായിട്ടുണ്ട്!")
            
            # ഫോണിലേക്ക് സേവ് ചെയ്യാനുള്ള ബട്ടൺ
            with open(filename, "rb") as file:
                st.download_button(
                    label="ഫോണിലേക്ക് സേവ് ചെയ്യുക ⬇️",
                    data=file,
                    file_name="instagram_reel.mp4",
                    mime="video/mp4"
                )
                
            # സെർവറിൽ നിന്ന് ഫയൽ ഡിലീറ്റ് ചെയ്യുന്നു
            os.remove(filename)
                
        except Exception as e:
            st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല. ലിങ്ക് കൃത്യമാണോ എന്ന് പരിശോധിക്കുക. എറർ: {e}")
    else:
        st.warning("ദയവായി ഒരു ഇൻസ്റ്റാഗ്രാം ലിങ്ക് നൽകുക!")
