import os
from flask import Flask, request
import telebot
from google import genai

# 1. Initialize Configuration FIRST
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL') 

# These create the 'bot' and 'app' variables so Python knows what they are
bot = telebot.TeleBot(TOKEN, parse_mode=None)
ai_client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

# 2. Telegram Webhook Routes
@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@app.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{TOKEN}")
    return "Webhook set successfully!", 200

# 3. Bot Message Handlers
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Hello! I am your AI Assistant. Ask me anything!")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        
        if response.text:
            bot.reply_to(message, response.text)
        else:
            bot.reply_to(message, "⚠️ The AI returned an empty response. It might have been blocked by safety filters.")
            
    except Exception as e:
        print(f"Detailed Error: {e}")
        bot.reply_to(message, f"❌ Bot Error: {str(e)}")

# 4. Main Execution LAST
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
