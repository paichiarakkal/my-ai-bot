import yt_dlp

def download_video():
    url = input("YouTube ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക: ")
    ydl_opts = {
        'format': 'best',
        'outtmpl': '%(title)s.%(ext)s', # വീഡിയോയുടെ പേരിൽ തന്നെ സേവ് ആകുന്നു
    }

    try:
        print("ഡൗൺലോഡ് തുടങ്ങുന്നു, ദയവായി കാത്തിരിക്കുക...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("വിജയകരമായി ഡൗൺലോഡ് ചെയ്തു!")
    except Exception as e:
        print(f"എന്തോ കുഴപ്പമുണ്ട്: {e}")

if __name__ == "__main__":
    download_video()
