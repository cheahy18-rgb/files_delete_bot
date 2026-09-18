import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# បង្កើត Web Server តូចមួយសម្រាប់ Render
app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

# --- កូដ Bot របស់អ្នក ---
BOT_TOKEN = os.environ.get("del_files_bot")
RESTRICTED_EXTENSIONS = [".exe", ".rar", ".doc", ".zip"]

async def check_and_delete_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message and message.document:
        file_name = message.document.file_name
        if file_name:
            _, file_extension = os.path.splitext(file_name.lower())
            if file_extension in RESTRICTED_EXTENSIONS:
                try:
                    await message.delete()
                except Exception as e:
                    print(f"Error: {e}")

def main():
    # រត់ Flask លើ Thread ផ្សេង
    threading.Thread(target=run_flask, daemon=True).start()

    # រត់ Telegram Bot
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.Document.ALL, check_and_delete_attachment))
    app.run_polling()

if __name__ == "__main__":
    main()