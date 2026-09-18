import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# កំណត់ Token របស់ Bot អ្នកនៅទីនេះ
BOT_TOKEN = "8928133664:AAH6FCh4KvVlg0KDfNobmkXOkp1ZEiOOl_g"

# កំណត់ប្រភេទ Extension ដែលត្រូវលុប (អាចថែមថយបាន)
RESTRICTED_EXTENSIONS = [".exe", ".rar", ".doc", ".zip",".txt",]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

async def check_and_delete_attachment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    
    # ពិនិត្យមើលថាសារមានផ្ញើជា Document/File ឬទេ
    if message and message.document:
        file_name = message.document.file_name
        
        if file_name:
            # ទាញយក extension នៃ file (ឧទាហរណ៍: .exe)
            _, file_extension = os.path.splitext(file_name.lower())
            
            # ពិនិត្យបើ extension ស្ថិតក្នុងបញ្ជីហាមឃាត់
            if file_extension in RESTRICTED_EXTENSIONS:
                try:
                    # លុបសារដែលមាន File នោះ
                    await message.delete()
                    
                    # ផ្ញើសារប្រាប់ក្នុង Group (ជម្រើសបន្ថែម)
                    warning_msg = await message.chat.send_message(
                       # f"⚠️ សាររបស់ @{message.from_user.username or message.from_user.first_name} ត្រូវបានលុប ដោយសារមានផ្ទុក File ប្រភេទ ({file_extension}) ដែលមិនត្រូវបានអនុញ្ញាត!"
                    )
                except Exception as e:
                    logging.error(f"មិនអាចលុបសារបានទេ: {e}")

def main():
    # បង្កើត Application
    app = Application.builder().token(BOT_TOKEN).build()

    # ស្កេនរាល់សារទាំងឡាយណាដែលជាប្រភេទ Document/File
    app.add_handler(MessageHandler(filters.Document.ALL, check_and_delete_attachment))

    print("Bot កំពុងដំណើរការ...")
    app.run_polling()

if __name__ == "__main__":
    main()