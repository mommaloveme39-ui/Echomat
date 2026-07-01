import os
from flask import Flask, request
import telebot
from google import genai

# 1. Initialize Configuration
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
# Render provides the IS_PULL_REQUEST or you can set a custom app name env
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL') 

bot = telebot.TeleBot(TOKEN, parse_mode=None)
ai_client = genai.Client(api_key=GEMINI_API_KEY)
app = Flask(__name__)

# 2. Telegram Webhook Route
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
        # Send a typing action to look responsive
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Generate content using the fast, lightweight gemini-2.5-flash model
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "Sorry, I ran into an error processing that.")

# 4. Main Execution
if __name__ == "__main__":
    # Render routes traffic to port 10000 by default or via the PORT env variable
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
