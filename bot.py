import os
import time
from flask import Flask, request
import telebot
from google import genai

# 1. Initialize Configuration
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL') 

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
    # Auto-retry loop to handle temporary traffic issues
    for attempt in range(3):
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            
            # The model is correctly passed as an argument inside the function call here:
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash-lite',
                contents=message.text,
            )
            
            if response.text:
                bot.reply_to(message, response.text)
                return
            else:
                bot.reply_to(message, "⚠️ The AI returned an empty response.")
                return
                
        except Exception as e:
            # If hit by a rate limit, wait 5 seconds and retry
            if "429" in str(e) and attempt < 2:
                time.sleep(5)
                continue
            
            print(f"Detailed Error: {e}")
            bot.reply_to(message, f"❌ Bot Error: {str(e)}")
            return

# 4. Main Execution
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    app.run(host="0.0.0.0", port=port)
