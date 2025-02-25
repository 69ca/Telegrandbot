import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import requests
import yt_dlp
import os
from config import BOT_TOKEN, YOUTUBE_QUALITIES

# تهيئة البوت
bot = telegram.Bot(token=BOT_TOKEN)
updater = Updater(BOT_TOKEN, use_context=True)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="مرحبًا! أرسل رابطًا لصورة أو فيديو من Instagram أو TikTok أو YouTube.")

def handle_link(update, context):
    url = update.message.text
    chat_id = update.effective_chat.id

    if "youtube.com" in url or "youtu.be" in url:
        show_youtube_options(chat_id, url, context)
    elif "instagram.com" in url:
        download_instagram_media(url, chat_id, context)
    elif "tiktok.com" in url:
        download_tiktok_media(url, chat_id, context)
    else:
        context.bot.send_message(chat_id=chat_id, text="الرابط غير مدعوم.")

def show_youtube_options(chat_id, url, context):
    keyboard = [
        [InlineKeyboardButton("240p", callback_data=f"youtube_{url}_1"),
         InlineKeyboardButton("480p", callback_data=f"youtube_{url}_2")],
        [InlineKeyboardButton("720p", callback_data=f"youtube_{url}_3"),
         InlineKeyboardButton("1080p", callback_data=f"youtube_{url}_4")],
        [InlineKeyboardButton("ملف صوتي", callback_data=f"youtube_{url}_5")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=chat_id, text="اختر جودة الفيديو:", reply_markup=reply_markup)

def handle_youtube_choice(update, context):
    query = update.callback_query
    query.answer()
    data = query.data.split('_')
    url = data[1]
    choice = data[2]
    chat_id = query.message.chat_id

    ydl_opts = {
        'outtmpl': '%(title)s.%(ext)s',
        'format': YOUTUBE_QUALITIES.get(choice, 'best'),
    }

    if choice == '5':  # تنزيل ملف صوتي فقط
        ydl_opts.update({'extract_audio': True, 'audio_format': 'mp3'})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            if choice == '5':
                context.bot.send_audio(chat_id=chat_id, audio=open(file_path, 'rb'), 
                                       title=info['title'])
            else:
                context.bot.send_video(chat_id=chat_id, video=open(file_path, 'rb'))
            os.remove(file_path)  # حذف الملف بعد الإرسال
    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text=f"حدث خطأ: {str(e)}")

def download_instagram_media(url, chat_id, context):
    context.bot.send_message(chat_id=chat_id, text="تنزيل من Instagram قيد التطوير.")

def download_tiktok_media(url, chat_id, context):
    context.bot.send_message(chat_id=chat_id, text="تنزيل من TikTok قيد التطوير.")

def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))
    dp.add_handler(CallbackQueryHandler(handle_youtube_choice, pattern='youtube_.*'))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()