import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

# Cấu hình Token
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Hàm tìm kiếm 5 kết quả
def search_multiple_youtube(query, limit=5):
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': f'ytsearch{limit}',
        'quiet': True,
        'nocheckcertificate': True,
    }
    
    results = []
    with YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            if 'entries' in info:
                for entry in info['entries']:
                    results.append({
                        'title': entry.get('title'),
                        'id': entry.get('id'),
                        'uploader': entry.get('uploader'),
                        'duration': entry.get('duration')
                    })
        except Exception as e:
            print(f"Lỗi tìm kiếm: {e}")
    return results

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "🎵 Chào Đức! Nhập tên bài hát, mình sẽ liệt kê 5 gợi ý tốt nhất cho bạn.")

@bot.message_handler(func=lambda message: True)
def handle_search(message):
    query = message.text
    status_msg = bot.reply_to(message, f"🔍 Đang tìm 5 gợi ý cho: '{query}'...")
    
    results = search_multiple_youtube(query)
    
    if results:
        markup = types.InlineKeyboardMarkup()
        text_reply = "<b>🔥 Dưới đây là 5 kết quả tìm thấy:</b>\n\n"
        
        for i, video in enumerate(results, 1):
            url = f"https://www.youtube.com/watch?v={video['id']}"
            # Thêm thông tin vào tin nhắn văn bản
            text_reply += f"{i}. <b>{video['title']}</b>\n👤 <i>{video['uploader']}</i>\n\n"
            
            # Tạo nút bấm cho mỗi video
            btn = types.InlineKeyboardButton(
                text=f"Xem bài {i}", 
                url=url
            )
            markup.add(btn)
        
        bot.send_message(
            message.chat.id, 
            text_reply, 
            reply_markup=markup, 
            parse_mode='HTML',
            disable_web_page_preview=True # Tắt preview để danh sách gọn hơn
        )
        bot.delete_message(message.chat.id, status_msg.message_id)
    else:
        bot.edit_message_text("❌ Không tìm thấy kết quả nào.", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    print("--- Bot Gợi Ý 5 Video đã sẵn sàng ---")
    bot.infinity_polling()