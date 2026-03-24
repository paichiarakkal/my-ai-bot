import telebot
import google.generativeai as genai

# Tokens
TELEGRAM_BOT_TOKEN = '8638662433:AAGKc6Uo-X06W6i2Sdt5Ul1bIpv_FoXhVjQ'
GEMINI_API_KEY = 'AIzaSyC9CUkynm2xlmBDiObx6xkfFi0Dm9vqg_4'

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def chat_with_ai(message):
    try:
        response = model.generate_content(message.text + " (reply in malayalam briefly)")
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "Error: " + str(e))

bot.infinity_polling()

