import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Web Server សម្រាប់ Render Health Check
app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "Bot is running!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

# ទាញយក Token
BOT_TOKEN = os.environ.get("delfiles_bot")
RESTRICTED_EXTENSIONS = [".exe", ".rar", ".doc", ".zip"]

# Function សម្រាប់ឆ្លើយតបនៅពេលចុច /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "ជំរាបសួរ! ខ្ញុំជា Bot សម្រាប់លុបឯកសារហាមឃាត់ (.exe, .rar, .doc, .zip) ក្នុង Group។\n\n"
        "សូមបន្ថែមខ្ញុំចូលទៅក្នុង Group របស់អ្នក រួចប្រគល់សិទ្ធិជា Admin (Delete Messages) ឲ្យខ្ញុំផង!"
    )

# Function សម្រាប់ស្កេន និងលុប File
async def check_and_delete_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if message and message.document:
        file_name = message.document.file_name
        if file_name:
            _, file_extension = os.path.splitext(file_name.lower())
            if file_extension in RESTRICTED_EXTENSIONS:
                try:
                    await message.delete()
                    await message.chat.send_message(
                        f"⚠️ សាររបស់ @{message.from_user.username or message.from_user.first_name} ត្រូវបានលុប ដោយសារមានផ្ទុក File ហាមឃាត់ ({file_extension})!"
                    )
                except Exception as e:
                    print(f"Error: {e}")

def main():
    # រត់ Web Server
    threading.Thread(target=run_flask, daemon=True).start()

    # បង្កើត Telegram Bot
    app = Application.builder().token(BOT_TOKEN).build()

    # បន្ថែម Handler សម្រាប់ /start និង Document
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.Document.ALL, check_and_delete_attachment))

    print("Bot កំពុងដំណើរការ...")
    app.run_polling()

if __name__ == "__main__":
    main()