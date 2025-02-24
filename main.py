import os
import logging
import yt_dlp
import instaloader
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytube import YouTube
from mutagen.mp3 import MP3
from PIL import Image

# إعدادات البوت
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# إعداد تسجيل الأخطاء
logging.basicConfig(level=logging.INFO)

# دالة تحميل فيديو من يوتيوب كملف صوتي مع صورة مصغرة
def download_youtube_audio(url):
    yt = YouTube(url)
    filename = f"{yt.title}.mp3"
    thumbnail_url = yt.thumbnail_url

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': filename,
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # تحميل الصورة المصغرة
    thumbnail_filename = f"{yt.title}.jpg"
    response = requests.get(thumbnail_url)
    with open(thumbnail_filename, 'wb') as f:
        f.write(response.content)

    return filename, thumbnail_filename, yt.title

# دالة لتحميل ستوريات انستجرام
def download_instagram_story(username):
    loader = instaloader.Instaloader()
    loader.download_profiles([username], profile_pic_only=False, stories=True)
    return f"{username}_stories"

# استقبال الرسائل من المستخدم
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "أهلاً! أرسل لي رابط فيديو أو صورة وسأقوم بتحميلها لك!")

@bot.message_handler(func=lambda message: message.text.startswith("http"))
def handle_url(message):
    url = message.text

    if "youtube.com" in url or "youtu.be" in url:
        filename, thumbnail, title = download_youtube_audio(url)
        with open(thumbnail, 'rb') as thumb, open(filename, 'rb') as audio:
            bot.send_audio(message.chat.id, audio, title=title, thumb=thumb)

    elif "instagram.com" in url:
        if "/stories/" in url:
            username = url.split("/")[-2]
            folder = download_instagram_story(username)
            bot.send_message(message.chat.id, f"تم تحميل ستوريات {username}")

    else:
        bot.send_message(message.chat.id, "هذا الرابط غير مدعوم حالياً.")

# تشغيل البوت
if __name__ == "__main__":
    bot.polling()