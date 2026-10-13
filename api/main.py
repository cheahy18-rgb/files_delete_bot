import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

app = Flask(__name__)

# ទាញយក Token
BOT_TOKEN = os.environ.get("del_files_bot")
RESTRICTED_EXTENSIONS = [".exe", ".rar", ".doc", ".zip", ".txt", ".vbs"]

# កន្លែងរក្សាទុក Telegram Application instance
telegram_app = None

def get_telegram_app():
    global telegram_app
    if telegram_app is None and BOT_TOKEN:
        telegram_app = Application.builder().token(BOT_TOKEN).build()
        telegram_app.add_handler(CommandHandler("start", start_command))
        telegram_app.add_handler(MessageHandler(filters.Document.ALL, check_and_delete_attachment))
    return telegram_app

async def start_command(update, context):
    await update.message.reply_text(
        "ជំរាបសួរ! ខ្ញុំជា Bot សម្រាប់លុបឯកសារហាមឃាត់ (.exe, .rar, .doc, .zip, .txt, .vbs)) ក្នុង Group។\n\n"
        "សូមបន្ថែមខ្ញុំចូលទៅក្នុង Group របស់អ្នក រួចប្រគល់សិទ្ធិជា Admin (Delete Messages) ឲ្យខ្ញុំផង!"
    )

async def check_and_delete_attachment(update, context):
    message = update.effective_message
    if message and message.document:
        file_name = message.document.file_name
        if file_name:
            _, file_extension = os.path.splitext(file_name.lower())
            if file_extension in RESTRICTED_EXTENSIONS:
                try:
                    await message.delete()
                    user_name = message.from_user.username or message.from_user.first_name
                    await message.chat.send_message(
                        f"⚠️ សាររបស់ @{user_name} ត្រូវបានលុប ដោយសារមានផ្ទុក File ហាមឃាត់ ({file_extension})!"
                    )
                except Exception as e:
                    print(f"Error: {e}")

@app.route('/')
def home():
    return "Telegram Bot is running on Vercel!", 200

@app.route('/api/webhook', methods=['POST'])
def webhook():
    if not BOT_TOKEN:
        return "Error: BOT_TOKEN is missing in environment variables.", 500

    app_instance = get_telegram_app()
    if not app_instance:
        return "Error: Failed to initialize Telegram App.", 500

    if request.method == "POST":
        try:
            data = request.get_json(force=True)
            update = Update.de_json(data, app_instance.bot)
            
            async def process():
                await app_instance.initialize()
                await app_instance.process_update(update)
                await app_instance.shutdown()

            asyncio.run(process())
            return "OK", 200
        except Exception as e:
            print(f"Webhook Error: {e}")
            return str(e), 500
