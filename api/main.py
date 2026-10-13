import os
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

app = Flask(__name__)

# ទាញយក Token
BOT_TOKEN = os.environ.get("del_files_bot")
RESTRICTED_EXTENSIONS = [".exe", ".rar", ".doc", ".zip", ".vbs", ".txt"]

# បង្កើត Application របស់ Telegram សម្រាប់ដំណើរការแบบ Stateless (Webhook)
# Note: In production serverless, initializing the app globally or per request is needed.
telegram_app = Application.builder().token(BOT_TOKEN).build()

async def start_command(update, context):
    await update.message.reply_text(
        "ជំរាបសួរ! ខ្ញុំជា Bot សម្រាប់លុបឯកសារហាមឃាត់ (.exe, .rar, .doc, .zip, .vbs, .txt) ក្នុង Group។\n\n"
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

# ចុះឈ្មោះ Handlers
telegram_app.add_handler(CommandHandler("start", start_command))
telegram_app.add_handler(MessageHandler(filters.Document.ALL, check_and_delete_attachment))

@app.route('/')
def home():
    return "Telegram Bot is running on Vercel!", 200

@app.route('/api/webhook', methods=['POST'])
def webhook():
    """Endpoint សម្រាប់ទទួល Update ពី Telegram Webhook"""
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), telegram_app.bot)
        
        # ដំណើរការ update តាមរយៈ asyncio loop ក្នុង serverless context
        async def process():
            await telegram_app.initialize()
            await telegram_app.process_update(update)
            await telegram_app.shutdown()

        import asyncio
        asyncio.run(process())
        
        return "OK", 200
