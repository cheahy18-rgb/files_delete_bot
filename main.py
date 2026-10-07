import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Web Server សម្រាប់ Render Health Check
app_web = Flask(__name__)

@app_web.route('/')
def health_check():
    return "Bot is active!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host="0.0.0.0", port=port)

# ទាញយក Token
BOT_TOKEN = os.environ.get("delfiles_bot")

# កំណត់ប្រភេទ File ហាមឃាត់ និងទំហំអតិបរមា (200 MB = 200 * 1024 * 1024 bytes)
RESTRICTED_EXTENSIONS = [".exe", ".rar", ".doc", ".zip", ".txt", ".vbs"]
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200 MB

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot កំពុងដំណើរការស្កេន និងការពារ Group របស់អ្នក!")

async def check_and_delete_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    # ចាប់យកឯកសារប្រភេទ Document, Video, ឬ Audio
    file_obj = message.document or message.video or message.audio
    if not file_obj:
        return

    file_name = getattr(file_obj, 'file_name', None) or "Unknown_File"
    file_size = getattr(file_obj, 'file_size', 0)
    
    # គណនាទំហំជា MB
    file_size_mb = round(file_size / (1024 * 1024), 1)
    
    sender_user = message.from_user
    sender_name = f"@{sender_user.username}" if sender_user.username else sender_user.first_name

    _, file_extension = os.path.splitext(file_name.lower())

    # ១. ករណី File មានទំហំធំជាង 200 MB
    if file_size > MAX_FILE_SIZE:
        try:
            await message.delete()
            warning_msg = (
                f"⚠️ រកឃើញឯកសារធំពេក — មិនអាចស្កេនបាន / File too large to scan\n\n"
                f"👤 អ្នកផ្ញើ / Sender : {sender_name}\n"
                f"📄 ឯកសារ / File : {file_name}\n"
                f"📦 ទំហំ / Size : {file_size_mb} MB (limit 200 MB)\n\n"
                f"⛔ សារនេះត្រូវបានលុបចេញ ព្រោះឯកសារធំពេក ហើយមិនអាចផ្ទៀងផ្ទាត់បាន។\n"
                f"⛔ Message removed — file could not be scanned. Do not re-upload unverified files."
            )
            await message.chat.send_message(warning_msg)
        except Exception as e:
            print(f"Error deleting large file: {e}")
        return

    # ២. ករណី File ស្ថិតក្នុងបញ្ជីហាមឃាត់ (.exe, .rar, .doc, .zip, .txt, .vbs)
    if file_extension in RESTRICTED_EXTENSIONS:
        try:
            await message.delete()
            warning_msg = (
                f"⚠️ សាររបស់ {sender_name} ត្រូវបានលុប ដោយសារមានផ្ទុក File ប្រភេទ ({file_extension}) "
                f"ដែលមិនត្រូវបានអនុញ្ញាត!"
            )
            await message.chat.send_message(warning_msg)
        except Exception as e:
            print(f"Error deleting restricted file: {e}")

def main():
    threading.Thread(target=run_flask, daemon=True).start()

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    
    # ចាប់យកទាំង Document, Video, និង Audio
    file_filter = filters.Document.ALL | filters.VIDEO | filters.AUDIO
    app.add_handler(MessageHandler(file_filter, check_and_delete_attachment))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
