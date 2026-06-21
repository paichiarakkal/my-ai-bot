import streamlit as st
import yt_dlp
import os

# ആപ്പിന്റെ തലക്കെട്ട്
st.title("Universal Video Downloader 🎬")
st.write("Instagram Reels, YouTube Shorts, Facebook, Twitter തുടങ്ങി ഏത് വീഡിയോ ലിങ്കും താഴെ പേസ്റ്റ് ചെയ്ത് ഡൗൺലോഡ് ചെയ്യാം.")

# ലിങ്ക് വാങ്ങാനുള്ള ബോക്സ്
url = st.text_input("വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക:")

if st.button("Download Video"):
    if url:
        st.info("വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക...")
        
        # താൽക്കാലികമായി ഡൗൺലോഡ് ചെയ്യാനുള്ള ഫയൽ നെയിം പാറ്റേൺ
        outtmpl_path = 'downloaded_video.%(ext)s'
        
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': outtmpl_path,
            'nocheckcertificate': True,
            'quiet': True,
            # YouTube ബ്ലോക്ക് ചെയ്യാതിരിക്കാൻ റാൻഡം യൂസർ ഏജന്റും ഹെഡ്ഡറുകളും നൽകുന്നു
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            },
            # ജിയോ-ബ്ലോക്കിങ് ഒഴിവാക്കാൻ സഹായിക്കും
            'geo_bypass': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # വീഡിയോ വിവരങ്ങൾ എടുക്കുന്നു
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
            st.success("വീഡിയോ റെഡിയായിട്ടുണ്ട്!")
            
            # ഡൗൺലോഡ് ചെയ്ത ഫയൽ റീഡ് ചെയ്ത് ബട്ടൺ കാണിക്കുന്നു
            with open(filename, "rb") as file:
                st.download_button(
                    label="ഫോണിലേക്ക് സേവ് ചെയ്യുക ⬇️",
                    data=file,
                    file_name="video_download.mp4",
                    mime="video/mp4"
                )
                
            # സെർവറിൽ നിന്ന് ആ താൽക്കാലിക ഫയൽ ഡിലീറ്റ് ചെയ്യുന്നു
            os.remove(filename)
                
        except Exception as e:
            st.error(f"ഡൗൺലോഡ് ചെയ്യാൻ സാധിച്ചില്ല. ലിങ്ക് കൃത്യമാണോ എന്ന് പരിശോധിക്കുക. എറർ: {e}")
    else:
        st.warning("ദയവായി ഒരു വീഡിയോ ലിങ്ക് നൽകുക!")
