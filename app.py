from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
import yt_dlp
import threading
import os

# നിങ്ങളുടെ ഫോണ്ടുകളുടെ പേര് ഇവിടെ കൊടുക്കുക (main.py ഇരിക്കുന്ന അതേ ഫോൾഡറിൽ ഉണ്ടായിരിക്കണം)
MALAYALAM_FONT = "NotoSansMalayalam-Regular.ttf" # അല്ലെങ്കിൽ "AnjaliOldLipi.ttf"

class DownloaderApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        
        screen = MDScreen()
        layout = MDBoxLayout(orientation='vertical', padding=30, spacing=25)
        
        # Title
        layout.add_widget(MDLabel(
            text="Universal Video Downloader 🎬", 
            font_style="H4", 
            halign="center"
        ))
        
        # Subtitle (Malayalam Font Added)
        layout.add_widget(MDLabel(
            text="ലിങ്ക് താഴെ പേസ്റ്റ് ചെയ്ത് ഡൗൺലോഡ് ചെയ്യാം", 
            font_name=MALAYALAM_FONT if os.path.exists(MALAYALAM_FONT) else None,
            halign="center",
            theme_text_color="Secondary"
        ))
        
        # Input Box
        self.url_input = MDTextField(
            hint_text="വീഡിയോ ലിങ്ക് ഇവിടെ പേസ്റ്റ് ചെയ്യുക", 
            mode="rectangle"
        )
        layout.add_widget(self.url_input)
        
        # Status Label (Fixed the error logic here)
        self.status_label = MDLabel(
            text="", 
            font_name=MALAYALAM_FONT if os.path.exists(MALAYALAM_FONT) else None,
            halign="center", 
            theme_text_color="Error"
        )
        layout.add_widget(self.status_label)
        
        # Download Button
        btn = MDRaisedButton(
            text="Download Video", 
            pos_hint={"center_x": .5},
            padding=15
        )
        btn.bind(on_release=self.start_download_thread)
        layout.add_widget(btn)
        
        screen.add_widget(layout)
        return screen

    def start_download_thread(self, instance):
        threading.Thread(target=self.download_video).start()

    def download_video(self):
        url = self.url_input.text
        if not url:
            self.status_label.text = "ദയവായി ഒരു ലിങ്ക് നൽകുക!"
            return
            
        self.status_label.text = "വീഡിയോ പ്രോസസ്സ് ചെയ്യുന്നു, ദയവായി കാത്തിരിക്കുക..."
        
        # Android Downloads folder path
        download_folder = '/storage/emulated/0/Download/'
        if not os.path.exists(download_folder):
            download_folder = './' 
            
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join(download_folder, 'Downloaded_Video_%(id)s.%(ext)s'),
            'nocheckcertificate': True,
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            self.status_label.theme_text_color = "Custom"
            self.status_label.text_color = (0, 0.6, 0, 1) # പച്ച നിറം
            self.status_label.text = "വീഡിയോ Downloads ഫോൾഡറിൽ സേവ് ചെയ്തിട്ടുണ്ട്! ✅"
        except Exception as e:
            self.status_label.theme_text_color = "Error"
            self.status_label.text = f"ഡൗൺലോഡ് പരാജയപ്പെട്ടു!"
            print(f"Error: {e}") # യഥാർത്ഥ എറർ ടെർമിനലിൽ പ്രിന്റ് ചെയ്യും

if __name__ == "__main__":
    DownloaderApp().run()
