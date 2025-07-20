import os
import httpx
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Load environment variables
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Async function to query Gemini AI
async def ask_gemini(question: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": question}]
        }]
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=data)
            response.raise_for_status()
            candidates = response.json().get('candidates', [])
            if candidates:
                return candidates[0]['content']['parts'][0]['text']
            return "Sorry, no response from Gemini."
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return "There was an error talking to Gemini AI."

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm Kibo, your Gemini-powered AI bot 🤖. Ask me anything!")

# Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_name = update.message.chat.full_name
    print(f"User ({chat_name}): {user_message}")

    reply = await ask_gemini(user_message)
    await update.message.reply_text(reply)

# Main function to start the bot
if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Kibo Python bot is running...")
    app.run_polling()
