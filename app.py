import streamlit as st
import yt_dlp
import os

st.title("YouTube Video Downloader 🚀")
st.write("യൂട്യൂബ് ലിങ്ക് താഴെ പേസ്റ്റ് ചെയ്ത് വീഡിയോ ഡൗൺലോഡ് ചെയ്യാം.")

url = st.text_input("YouTube ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
    if url:
        st.info("ഡൗൺലോഡ് തുടങ്ങുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
            # ശക്തമായ പുതിയ സുരക്ഷാ ബൈപാസ് കോഡുകൾ:
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'referer': 'https://www.youtube.com/',
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            st.success("വീഡിയോ വിജയകരമായി ഡൗൺലോഡ് ചെയ്തു!")
            
            with open(filename, "rb") as file:
                st.download_button(
                    label="ഫോണിലേക്ക് സേവ് ചെയ്യുക ⬇️",
                    data=file,
                    file_name=filename,
                    mime="video/mp4"
                )
                
            os.remove(filename)
                
        except Exception as e:
            st.error(f"എന്തോ തകരാർ സംഭവിച്ചു: {e}")
    else:
        st.warning("ദയവായി ഒരു ലിങ്ക് നൽകുക!")
