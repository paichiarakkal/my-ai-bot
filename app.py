import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="Video Downloader", page_icon="🚀")

st.title("All-in-One Video Downloader 🚀")
st.write("YouTube, Instagram, Facebook തുടങ്ങി ഏത് വീഡിയോയും വളരെ എളുപ്പത്തിൽ ഡൗൺലോഡ് ചെയ്യാം.")

# ലിങ്ക് ബോക്സ് തനിയെ ക്ലിയർ ചെയ്യാൻ സഹായിക്കുന്ന സെഷൻ സ്റ്റേറ്റ്
if "input_url" not in st.session_state:
    st.session_state.input_url = ""

def clear_text():
    st.session_state.input_url = ""

# ലിങ്ക് വാങ്ങാനുള്ള ബോക്സ്
url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:", key="input_url")

if st.button("Download Video"):
    if url:
        with st.spinner("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക..."):
            
            # വീഡിയോ ലോക്കലായി ഡൗൺലോഡ് ചെയ്യാനുള്ള സെറ്റിങ്സ്
            ydl_opts = {
                'format': 'best[ext=mp4]/best', 
                'outtmpl': '%(title)s.%(ext)s',
                'nocheckcertificate': True,
                'quiet': True,
                'no_warnings': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
                }
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                
                if os.path.exists(filename):
                    st.success("വീഡിയോ റെഡിയായിട്ടുണ്ട്!")
                    
                    # 1. ആപ്പിൽ തന്നെ വീഡിയോ കാണാനുള്ള പ്ലെയർ (നിങ്ങൾ സ്ക്രീൻഷോട്ടിൽ കണ്ടത്)
                    with open(filename, "rb") as file:
                        video_bytes = file.read()
                        st.video(video_bytes)
                    
                    # 2. ഫോണിലേക്ക് സേവ് ചെയ്യാനുള്ള ബട്ടൺ + ഓട്ടോ ക്ലിയർ ഫങ്ഷൻ
                    st.download_button(
                        label="ഫോണിലേക്ക് സേവ് ചെയ്യുക ⬇️",
                        data=video_bytes,
                        file_name=os.path.basename(filename),
                        mime="video/mp4",
                        use_container_width=True,
                        on_click=clear_text # ഈ ബട്ടൺ ഞെക്കിയാൽ ലിങ്ക് തനിയെ മാറും!
                    )
                    
                    # ഉപയോഗത്തിന് ശേഷം ഫയൽ ഡിലീറ്റ് ചെയ്യുന്നു
                    os.remove(filename)
                else:
                    st.error("ഫയൽ കണ്ടെത്താൻ കഴിഞ്ഞില്ല.")
                    
            except Exception as e:
                st.error(f" can't download. എറർ: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
