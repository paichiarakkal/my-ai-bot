import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Video Downloader", page_icon="🚀")

st.title("All-in-One Video Downloader 🚀")
st.write("YouTube, Instagram, Facebook തുടങ്ങി ഏത് വീഡിയോയും വളരെ എളുപ്പത്തിൽ ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
    if url:
        # ലോഡിങ് ആനിമേഷൻ കാണിക്കാൻ
        with st.spinner("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക..."):
            
            # താല്കാലികമായി സെർവറിലേക്ക് ഡൗൺലോഡ് ചെയ്യാനുള്ള സെറ്റിങ്സ്
            ydl_opts = {
                # ഫോണിൽ പ്ലേ ചെയ്യാൻ ഏറ്റവും അനുയോജ്യമായ സിംഗിൾ MP4 ഫയൽ
                'format': 'best[ext=mp4]/best', 
                'outtmpl': 'downloads/%(title)s.%(ext)s', # ഒരു ഫോൾഡറിലേക്ക് മാറ്റുന്നു
                'nocheckcertificate': True,
                'quiet': True,
                'no_warnings': True,
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                
                # ഫയൽ വിജയകരമായി ഡൗൺലോഡ് ചെയ്താൽ
                if os.path.exists(filename):
                    st.success("വീഡിയോ റെഡിയായിട്ടുണ്ട്! താഴെയുള്ള ബട്ടൺ ഞെക്കി സേവ് ചെയ്യാം.")
                    
                    # ഫയൽ ബൈനറി ആയി റീഡ് ചെയ്ത് ബട്ടണിലേക്ക് നൽകുന്നു
                    with open(filename, "rb") as file:
                        st.download_button(
                            label="ഫോണിലേക്ക് സേവ് ചെയ്യുക ⬇️",
                            data=file,
                            file_name=os.path.basename(filename),
                            mime="video/mp4",
                            use_container_width=True # ബട്ടൺ ഭംഗിയാക്കാൻ
                        )
                    
                    # ഡൗൺലോഡ് കഴിഞ്ഞ ഉടനെ സെർവറിലെ ഫയൽ ഡിലീറ്റ് ചെയ്ത് മെമ്മറി ക്ലിയർ ആക്കുന്നു
                    os.remove(filename)
                else:
                    st.error("ഫയൽ കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                    
            except Exception as e:
                st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല. ലിങ്ക് കൃത്യമാണോ എന്ന് പരിശോധിക്കുക.\nഎറർ: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
