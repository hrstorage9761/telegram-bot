import os
import subprocess

# نصب ماژول‌های مورد نیاز
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    subprocess.check_call(["pip", "install", "python-telegram-bot"])
    from telegram import Update
    from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

try:
    import openai
except ImportError:
    subprocess.check_call(["pip", "install", "openai"])
    import openai

try:
    from dotenv import load_dotenv
except ImportError:
    subprocess.check_call(["pip", "install", "python-dotenv"])
    from dotenv import load_dotenv

from gtts import gTTS

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# دریافت توکن‌ها از محیط
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# تنظیمات OpenAI API
openai.api_key = OPENAI_API_KEY

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('سلام! من اینجا هستم تا به سوالات شما پاسخ بدم. هر نوع فایل، عکس یا صوت هم می‌تونید ارسال کنید.')

# دریافت پیام‌های متنی و پاسخ از OpenAI
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # استفاده از مدل gpt-4 به جای gpt-4o
            messages=[{"role": "user", "content": user_message}],
            max_tokens=150,
            temperature=0.7
        )

        bot_reply = response['choices'][0]['message']['content'].strip()
        await update.message.reply_text(bot_reply)

        # تبدیل پاسخ متنی به صوت (کامنت شده)
        # tts = gTTS(bot_reply, lang='en')
        # audio_path = "response.mp3"
        # tts.save(audio_path)

        # with open(audio_path, 'rb') as audio_file:
        #     await update.message.reply_audio(audio=audio_file)

        # os.remove(audio_path)

    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")

# دریافت فایل‌ها
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.document:
        file = await update.message.document.get_file()
        file_path = f"downloads/{update.message.document.file_id}"
        await file.download_to_drive(file_path)
        await update.message.reply_text(f"فایل شما ذخیره شد: {file_path}")

    elif update.message.audio:
        file = await update.message.audio.get_file()
        file_path = f"downloads/{update.message.audio.file_id}.mp3"
        await file.download_to_drive(file_path)
        await update.message.reply_text(f"فایل صوتی شما ذخیره شد: {file_path}")

    elif update.message.photo:
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"downloads/{update.message.photo[-1].file_id}.jpg"
        await photo_file.download_to_drive(file_path)
        await update.message.reply_text(f"عکس شما ذخیره شد: {file_path}")

    await update.message.reply_text("فایل دریافت شد.")

# اجرای بات
if BOT_TOKEN and OPENAI_API_KEY:
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_text))
    app.add_handler(MessageHandler(filters.ATTACHMENT, handle_file))

    print("ربات در حال اجرا است...")
    app.run_polling()
else:
    print("لطفاً مقادیر TELEGRAM_BOT_TOKEN و OPENAI_API_KEY را در محیط تنظیم کنید.")
