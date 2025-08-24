import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from dotenv import load_dotenv

# Загружаем токен из .env файла
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Проверяем токен
if not TOKEN:
    print("❌ ОШИБКА: Создайте файл .env с BOT_TOKEN=ваш_токен")
    exit(1)

print("✅ Бот запускается...")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Отправь ссылку на YouTube видео")


async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    # Проверка YouTube ссылки
    youtube_patterns = [
        r'youtube\.com/watch\?v=',
        r'youtu\.be/',
        r'youtube\.com/shorts/'
    ]

    if not any(pattern in url for pattern in youtube_patterns):
        await update.message.reply_text("❌ Это не ссылка YouTube!")
        return

    try:
        msg = await update.message.reply_text("⏳ Скачиваю...")

        # Настройки для скачивания
        ydl_opts = {
            'format': 'best[filesize<50M]',
            'outtmpl': 'video.%(ext)s',
            'quiet': True,
        }

        # Скачиваем видео
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            # Отправляем видео
            with open(filename, 'rb') as video_file:
                await update.message.reply_video(video=video_file)

            # Удаляем временный файл
            os.remove(filename)
            await msg.delete()

    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("❌ Не получилось скачать видео")


# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))

print("✅ Бот готов! Ожидаю сообщения...")
app.run_polling()