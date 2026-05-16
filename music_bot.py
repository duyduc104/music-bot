import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL
from dotenv import load_dotenv

# Cấu hình Token
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Hàm tìm kiếm 5 kết quả (Đã được nâng cấp để che giấu bot)
def search_multiple_youtube(query, limit=5):
    ydl_opts = {
        'format': 'bestaudio/best',
        'default_search': f'ytsearch{limit}',
        'quiet': True,
        'nocheckcertificate': True,
        
        # --- CẤU HÌNH NGỤY TRANG & CHE GIẤU BOT ---
        # 1. Sử dụng User-Agent của trình duyệt phổ biến
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        
        # 2. Thay đổi client giả lập để bỏ qua cơ chế chặn của client mặc định (Web)
        # Các client như 'ios' hoặc 'android' thường ít bị check khắt khe hơn
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web_embedded']
            }
        },
        
        # 3. Thêm các HTTP Headers cơ bản của trình duyệt để tránh bị nghi ngờ
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Cache-Control': 'max-age=0',
        },
        
        # Nếu chạy trên VPS bị chặn IP nặng, bạn có thể cân nhắc dùng Cookies (Bỏ comment nếu cần)
        # 'cookiesfrombrowser': ('chrome',), # Lấy cookies từ Chrome trên máy local (nếu chạy local)
    }
    
    results = []
    with YoutubeDL(ydl_opts) as ydl:
        try:
            # Sử dụng extract_info trực tiếp với cú pháp ytsearch
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)
            if info and 'entries' in info:
                for entry in info['entries']:
                    if entry:  # Đảm bảo entry không bị rỗng
                        results.append({
                            'title': entry.get('title'),
                            'id': entry.get('id'),
                            'uploader': entry.get('uploader'),
                            'duration': entry.get('duration')
                        })
        except Exception as e:
            print(f"Lỗi tìm kiếm YouTube: {e}")
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
            text_reply += f"{i}. <b>{video['title']}</b>\n👤 <i>{video['uploader']}</i>\n\n"
            
            btn = types.InlineKeyboardButton(
                text=f"Xem bài {i}", 
                url=url
            )
            markup.add(btn)
        
        try:
            bot.send_message(
                message.chat.id, 
                text_reply, 
                reply_markup=markup, 
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            bot.delete_message(message.chat.id, status_msg.message_id)
        except Exception as e:
            print(f"Lỗi gửi tin nhắn: {e}")
    else:
        # Thay vì edit_message (đôi khi lỗi nếu text cũ và mới giống nhau), ta dùng send rồi xóa cho chắc chắn
        bot.send_message(message.chat.id, "❌ Không tìm thấy kết quả nào hoặc hệ thống bị YouTube chặn tạm thời.")
        bot.delete_message(message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    print("--- Bot Gợi Ý 5 Video đã sẵn sàng ---")
    bot.infinity_polling()