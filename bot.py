import openai
from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import requests
import os

# توکن بات تلگرام
BOT_TOKEN = ''
# کلید API OpenAI
OPENAI_API_KEY = ''

# تنظیمات OpenAI API
openai.api_key = OPENAI_API_KEY

# دستور start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('سلام! من اینجا هستم تا به سوالات شما پاسخ بدم. هر نوع فایل، عکس یا صوت هم می‌تونید ارسال کنید.')

# دریافت پیام‌های متنی و پاسخ از OpenAI
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        # درخواست به OpenAI API
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",
            prompt=user_message,
            max_tokens=150,
            temperature=0.7
        )

        bot_reply = response.choices[0].text.strip()

        # ارسال پاسخ متنی به کاربر
        await update.message.reply_text(bot_reply)

        # تبدیل پاسخ متنی به صوت
        tts = gTTS(bot_reply)
        audio_path = "response.mp3"
        tts.save(audio_path)

        # ارسال پاسخ صوتی
        with open(audio_path, 'rb') as audio_file:
            await update.message.reply_audio(audio=audio_file)

        # حذف فایل صوتی بعد از ارسال
        os.remove(audio_path)
        
    except Exception as e:
        await update.message.reply_text(f"خطا: {e}")

# دریافت و ارسال فایل‌ها
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بررسی نوع فایل
    if update.message.document:
        # دریافت فایل مستندات
        file = await update.message.document.get_file()
        file_path = f"downloads/{update.message.document.file_id}.pdf"
        await file.download_to_drive(file_path)
        await update.message.reply_text(f"فایل مستندات شما ذخیره شد: {file_path}")

    elif update.message.audio:
        # دریافت فایل صوتی
        file = await update.message.audio.get_file()
        file_path = f"downloads/{update.message.audio.file_id}.mp3"
        await file.download_to_drive(file_path)
        await update.message.reply_text(f"فایل صوتی شما ذخیره شد: {file_path}")

    elif update.message.photo:
        # دریافت عکس
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"downloads/{update.message.photo[-1].file_id}.jpg"
        await photo_file.download_to_drive(file_path)
        await update.message.reply_text(f"عکس شما ذخیره شد: {file_path}")

    # ارسال تایید به کاربر
    await update.message.reply_text("فایل دریافت شد.")

# اجرای بات
app = ApplicationBuilder().token(BOT_TOKEN).build()

# ثبت دستورها
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle_text))  # دریافت پیام متنی
app.add_handler(MessageHandler(filters.AUDIO | filters.DOCUMENT | filters.PHOTO, handle_file))  # دریافت فایل‌ها

print("ربات در حال اجرا است...")
app.run_polling()
