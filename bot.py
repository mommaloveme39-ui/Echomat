@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        
        # Check if the response actually contains text before replying
        if response.text:
            bot.reply_to(message, response.text)
        else:
            # This happens if the response was blocked by safety filters
            bot.reply_to(message, "⚠️ The AI returned an empty response. It might have been blocked by safety filters.")
            
    except Exception as e:
        print(f"Detailed Error: {e}")
        # Send the exact error to your Telegram chat so you can see it instantly
        bot.reply_to(message, f"❌ Bot Error: {str(e)}")
