import time  # Add this to the top of your file with other imports

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    # Try up to 3 times if we hit a rate limit
    for attempt in range(3):
        try:
            bot.send_chat_action(message.chat.id, 'typing')
            
            response = ai_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=message.text,
            )
            
            if response.text:
                bot.reply_to(message, response.text)
                return  # Success! Break out of the retry loop
            else:
                bot.reply_to(message, "⚠️ The AI returned an empty response.")
                return
                
        except Exception as e:
            # If it's a rate limit error, wait 5 seconds and try again
            if "429" in str(e) and attempt < 2:
                time.sleep(5)
                continue
            
            # If it fails on the final attempt or is a different error, report it
            print(f"Detailed Error: {e}")
            bot.reply_to(message, "⚠️ The bot is experiencing high traffic right now. Please try your question again in a moment!")
            return
