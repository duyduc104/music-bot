import os
import datetime
import requests
import telebot

from telebot import types
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
from lunardate import LunarDate

# =========================
# LOAD ENV
# =========================

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# BOT COMMANDS
# =========================

bot.set_my_commands([
    telebot.types.BotCommand("start", "Khởi động bot"),
    telebot.types.BotCommand("menu", "Hiện menu"),
    telebot.types.BotCommand("help", "Hướng dẫn"),
    telebot.types.BotCommand("date", "Xem ngày hôm nay"),
    telebot.types.BotCommand("weather", "Xem thời tiết"),
    telebot.types.BotCommand("forecast", "Dự báo 5 ngày"),
    telebot.types.BotCommand("school", "Có đi học không"),
    telebot.types.BotCommand("rain", "Kiểm tra trời mưa"),
    telebot.types.BotCommand("hot", "Kiểm tra trời nóng"),
    telebot.types.BotCommand("music", "Tìm nhạc YouTube"),
    telebot.types.BotCommand("download", "Tải audio YouTube"),
    telebot.types.BotCommand("about", "Giới thiệu bot"),
])

# =========================
# YT-DLP CONFIG
# =========================

def get_base_ydl_opts():

    return {

        'quiet': True,

        'nocheckcertificate': True,

        'format': 'bestaudio/best',

        'noplaylist': True,

        'geo_bypass': True,

        'socket_timeout': 30,

        'retries': 10,

        'fragment_retries': 10,

        'ignoreerrors': True,

        'cookiefile': 'cookies.txt',

        'user_agent': (
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
            'AppleWebKit/537.36 '
            '(KHTML, like Gecko) '
            'Chrome/124.0 Safari/537.36'
        ),

        'http_headers': {
            'Accept-Language': 'vi-VN,vi;q=0.9',
            'Referer': 'https://www.youtube.com/',
        },

        'extractor_args': {
            'youtube': {
                'player_client': [
                    'android',
                    'ios',
                    'web'
                ]
            }
        }
    }


# =========================
# YOUTUBE SEARCH
# =========================

def search_multiple_youtube(query, limit=5):

    ydl_opts = get_base_ydl_opts()

    ydl_opts['format'] = 'bestaudio/best'
    ydl_opts['default_search'] = f'ytsearch{limit}'

    results = []

    try:

        with YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                f"ytsearch{limit}:{query}",
                download=False
            )

            if info and 'entries' in info:

                for entry in info['entries']:

                    if entry:

                        results.append({
                            'title': entry.get('title'),
                            'id': entry.get('id'),
                            'uploader': entry.get('uploader')
                        })

    except Exception as e:

        print("Lỗi tìm kiếm:", e)

    return results


# =========================
# GET AUDIO LINK
# =========================

def get_audio_download_link(video_url):

    ydl_opts = get_base_ydl_opts()

    ydl_opts['format'] = 'bestaudio[ext=m4a]/bestaudio/best'

    try:

        with YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(
                video_url,
                download=False
            )

            return {
                'title': info.get('title'),
                'download_url': info.get('url'),
                'uploader': info.get('uploader')
            }

    except Exception as e:

        print("Lỗi tải audio:", e)
        return None


# =========================
# DATE INFO
# =========================

def get_current_date_info():

    today = datetime.date.today()

    lunar_today = LunarDate.fromSolarDate(
        today.year,
        today.month,
        today.day
    )

    days_of_week = [
        "Thứ Hai",
        "Thứ Ba",
        "Thứ Tư",
        "Thứ Năm",
        "Thứ Sáu",
        "Thứ Bảy",
        "Chủ Nhật"
    ]

    weekday = days_of_week[today.weekday()]

    text = (
        f"📅 <b>THÔNG TIN HÔM NAY</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📆 Dương lịch: {weekday}, "
        f"{today.day:02d}/{today.month:02d}/{today.year}\n"
        f"🌙 Âm lịch: "
        f"{lunar_today.day:02d}/"
        f"{lunar_today.month:02d}/"
        f"{lunar_today.year}"
    )

    return text


# =========================
# WEATHER
# =========================

def get_current_weather(city="Hanoi"):

    if not WEATHER_API_KEY:
        return "⚠️ Chưa cấu hình WEATHER_API_KEY"

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}"
        f"&appid={WEATHER_API_KEY}"
        f"&units=metric"
        f"&lang=vi"
    )

    try:

        response = requests.get(url).json()

        if response.get("cod") != 200:

            return "❌ Không tìm thấy thành phố"

        main = response["main"]

        weather_desc = response["weather"][0]["description"]

        humidity = main["humidity"]

        wind = response["wind"]["speed"]

        text = (
            f"🌤️ <b>THỜI TIẾT TẠI {city.upper()}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🌡️ Nhiệt độ: {main['temp']}°C\n"
            f"🥵 Cảm giác như: {main['feels_like']}°C\n"
            f"💧 Độ ẩm: {humidity}%\n"
            f"💨 Gió: {wind} m/s\n"
            f"📝 Trạng thái: {weather_desc.capitalize()}"
        )

        return text

    except Exception as e:

        return f"❌ Lỗi API: {e}"


# =========================
# FORECAST
# =========================

def get_weather_forecast_5days(city="Hanoi"):

    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?q={city}"
        f"&appid={WEATHER_API_KEY}"
        f"&units=metric"
        f"&lang=vi"
    )

    try:

        response = requests.get(url).json()

        if response.get("cod") != "200":

            return "❌ Không lấy được dữ liệu"

        text = (
            f"📅 <b>DỰ BÁO 5 NGÀY - {city.upper()}</b>\n"
            f"━━━━━━━━━━━━━━━\n"
        )

        seen_dates = set()

        for item in response["list"]:

            dt = datetime.datetime.strptime(
                item["dt_txt"],
                "%Y-%m-%d %H:%M:%S"
            )

            date_str = f"{dt.day:02d}/{dt.month:02d}"

            if (
                "12:00:00" in item["dt_txt"]
                and date_str not in seen_dates
            ):

                seen_dates.add(date_str)

                temp = item["main"]["temp"]

                desc = item["weather"][0]["description"]

                text += (
                    f"📆 {date_str}: "
                    f"{temp}°C | "
                    f"{desc.capitalize()}\n"
                )

                if len(seen_dates) >= 5:
                    break

        return text

    except Exception as e:

        return f"❌ Lỗi forecast: {e}"


# =========================
# CHECK RAIN
# =========================

def check_rain_today(city="Hanoi"):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}"
        f"&appid={WEATHER_API_KEY}"
        f"&units=metric"
        f"&lang=vi"
    )

    try:

        response = requests.get(url).json()

        weather = response["weather"][0]["description"].lower()

        if "mưa" in weather:

            return (
                f"🌧️ <b>Hôm nay có khả năng mưa tại {city}</b>\n"
                f"📝 {weather}"
            )

        else:

            return (
                f"☀️ <b>Hôm nay ít khả năng mưa tại {city}</b>\n"
                f"📝 {weather}"
            )

    except Exception as e:

        return f"❌ Lỗi: {e}"


# =========================
# CHECK HOT WEATHER
# =========================

def check_hot_weather(city="Hanoi"):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}"
        f"&appid={WEATHER_API_KEY}"
        f"&units=metric"
        f"&lang=vi"
    )

    try:

        response = requests.get(url).json()

        temp = response["main"]["temp"]

        if temp >= 35:

            return (
                f"🔥 <b>Hôm nay trời rất nóng tại {city}!</b>\n"
                f"🌡️ {temp}°C"
            )

        elif temp >= 30:

            return (
                f"☀️ <b>Hôm nay khá nắng tại {city}</b>\n"
                f"🌡️ {temp}°C"
            )

        else:

            return (
                f"🌤️ <b>Hôm nay thời tiết dễ chịu tại {city}</b>\n"
                f"🌡️ {temp}°C"
            )

    except Exception as e:

        return f"❌ Lỗi: {e}"


# =========================
# SCHOOL CHECK
# =========================

HOLIDAYS = [
    "01-01",
    "30-04",
    "01-05",
    "02-09"
]

def school_today():

    today = datetime.datetime.today()

    today_date = today.strftime("%d-%m")

    weekday = today.weekday()

    if today_date in HOLIDAYS:

        return (
            "🎉 <b>Hôm nay là ngày nghỉ lễ!</b>\n"
            "😄 Không cần đi học."
        )

    if weekday <= 4:

        return (
            "🏫 <b>Hôm nay có đi học nhé!</b>\n"
            "📚 Nhớ chuẩn bị bài 😄"
        )

    return (
        "🎉 <b>Hôm nay được nghỉ học!</b>"
    )


# =========================
# START / HELP / MENU
# =========================

@bot.message_handler(commands=['start', 'help', 'menu'])
def send_welcome(message):

    user_name = message.from_user.first_name

    text = (
        f"🤖 <b>Xin chào {user_name}!</b>\n\n"
        f"Mình là Bot Trợ Lý Đa Năng 🎵🌤️\n\n"

        f"📌 <b>CÁC LỆNH:</b>\n"
        f"━━━━━━━━━━━━━━━\n"

        f"/date → Xem ngày hôm nay\n"
        f"/weather hanoi → Xem thời tiết\n"
        f"/forecast hcm → Dự báo 5 ngày\n"
        f"/rain hanoi → Có mưa không\n"
        f"/hot hanoi → Có nóng không\n"
        f"/school → Có đi học không\n"
        f"/music tên bài hát → Tìm nhạc\n"
        f"/download [link] → Tải audio\n"
        f"/about → Giới thiệu bot\n\n"

        f"🎵 Hoặc nhập tên bài hát để tìm nhanh!"
    )

    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    markup.row(
        "📆 Ngày Hôm Nay",
        "🌤️ Thời Tiết"
    )

    markup.row(
        "📅 Dự Báo 5 Ngày",
        "🎓 Có Đi Học Không"
    )

    markup.row(
        "☀️ Có Nắng Không",
        "🌧️ Có Mưa Không"
    )

    markup.row(
        "🤖 Giới Thiệu Bot"
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=markup,
        parse_mode='HTML'
    )


# =========================
# DATE HANDLER
# =========================

@bot.message_handler(commands=['date'])
@bot.message_handler(func=lambda m: m.text == "📆 Ngày Hôm Nay")
def handle_date(message):

    bot.reply_to(
        message,
        get_current_date_info(),
        parse_mode='HTML'
    )


# =========================
# WEATHER HANDLER
# =========================

@bot.message_handler(commands=['weather'])
@bot.message_handler(func=lambda m: m.text == "🌤️ Thời Tiết")
def handle_weather(message):

    try:

        args = message.text.split(maxsplit=1)

        city = "Hanoi"

        if len(args) > 1:
            city = args[1]

        bot.reply_to(
            message,
            get_current_weather(city),
            parse_mode='HTML'
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"❌ Lỗi thời tiết: {e}"
        )


# =========================
# FORECAST HANDLER
# =========================

@bot.message_handler(commands=['forecast'])
@bot.message_handler(func=lambda m: m.text == "📅 Dự Báo 5 Ngày")
def handle_forecast(message):

    try:

        args = message.text.split(maxsplit=1)

        city = "Hanoi"

        if len(args) > 1:
            city = args[1]

        bot.reply_to(
            message,
            get_weather_forecast_5days(city),
            parse_mode='HTML'
        )

    except Exception as e:

        bot.reply_to(
            message,
            f"❌ Lỗi forecast: {e}"
        )


# =========================
# SCHOOL HANDLER
# =========================

@bot.message_handler(commands=['school'])
@bot.message_handler(func=lambda m: m.text == "🎓 Có Đi Học Không")
def handle_school(message):

    bot.reply_to(
        message,
        school_today(),
        parse_mode='HTML'
    )


# =========================
# RAIN HANDLER
# =========================

@bot.message_handler(commands=['rain'])
@bot.message_handler(func=lambda m: m.text == "🌧️ Có Mưa Không")
def handle_rain(message):

    args = message.text.split(maxsplit=1)

    city = "Hanoi"

    if len(args) > 1:
        city = args[1]

    bot.reply_to(
        message,
        check_rain_today(city),
        parse_mode='HTML'
    )


# =========================
# HOT WEATHER HANDLER
# =========================

@bot.message_handler(commands=['hot'])
@bot.message_handler(func=lambda m: m.text == "☀️ Có Nắng Không")
def handle_hot(message):

    args = message.text.split(maxsplit=1)

    city = "Hanoi"

    if len(args) > 1:
        city = args[1]

    bot.reply_to(
        message,
        check_hot_weather(city),
        parse_mode='HTML'
    )


# =========================
# ABOUT BOT
# =========================

@bot.message_handler(commands=['about'])
@bot.message_handler(func=lambda m: m.text == "🤖 Giới Thiệu Bot")
def handle_about(message):

    text = (
        "🤖 <b>GIỚI THIỆU BOT</b>\n"
        "━━━━━━━━━━━━━━━\n"
        "🎵 Tìm nhạc YouTube\n"
        "📥 Tải audio YouTube\n"
        "🌤️ Xem thời tiết\n"
        "📅 Dự báo thời tiết\n"
        "📆 Xem ngày Âm - Dương\n"
        "🎓 Kiểm tra lịch học\n\n"

        "⚡ Code bằng Python\n"
        "❤️ Telegram Multi Bot"
    )

    bot.reply_to(
        message,
        text,
        parse_mode='HTML'
    )


# =========================
# DOWNLOAD AUDIO
# =========================

@bot.message_handler(commands=['download'])
def handle_download(message):

    args = message.text.split(maxsplit=1)

    if len(args) < 2:

        bot.reply_to(
            message,
            "⚠️ Ví dụ:\n/download https://youtube.com/..."
        )

        return

    video_url = args[1]

    status = bot.reply_to(
        message,
        "⏳ Đang lấy link tải..."
    )

    audio_info = get_audio_download_link(video_url)

    if audio_info:

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                text="📥 Tải Audio",
                url=audio_info['download_url']
            )
        )

        bot.send_message(
            message.chat.id,
            f"🎵 <b>{audio_info['title']}</b>",
            reply_markup=markup,
            parse_mode='HTML'
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Không lấy được link tải"
        )

    bot.delete_message(
        message.chat.id,
        status.message_id
    )


# =========================
# CALLBACK DOWNLOAD
# =========================

@bot.callback_query_handler(func=lambda c: c.data.startswith("dl_"))
def callback_download(call):

    video_id = call.data.split("_")[1]

    video_url = f"https://youtube.com/watch?v={video_id}"

    audio_info = get_audio_download_link(video_url)

    if audio_info:

        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton(
                text="📥 Tải Audio",
                url=audio_info['download_url']
            )
        )

        bot.send_message(
            call.message.chat.id,
            f"🎵 <b>{audio_info['title']}</b>",
            reply_markup=markup,
            parse_mode='HTML'
        )

    else:

        bot.send_message(
            call.message.chat.id,
            "❌ Không tải được"
        )


# =========================
# MUSIC COMMAND
# =========================

@bot.message_handler(commands=['music'])
def handle_music(message):

    args = message.text.split(maxsplit=1)

    if len(args) < 2:

        bot.reply_to(
            message,
            "⚠️ Ví dụ:\n/music Sơn Tùng"
        )

        return

    query = args[1]

    search_music(message, query)


# =========================
# SEARCH MUSIC FUNCTION
# =========================

def search_music(message, query):

    status = bot.reply_to(
        message,
        f"🔍 Đang tìm nhạc: {query}"
    )

    results = search_multiple_youtube(query)

    if results:

        markup = types.InlineKeyboardMarkup()

        text_reply = (
            "🔥 <b>TOP 5 KẾT QUẢ:</b>\n\n"
        )

        for i, video in enumerate(results, 1):

            url = (
                f"https://youtube.com/watch?v={video['id']}"
            )

            text_reply += (
                f"{i}. <b>{video['title']}</b>\n"
                f"👤 {video['uploader']}\n\n"
            )

            markup.row(
                types.InlineKeyboardButton(
                    text=f"📺 Xem {i}",
                    url=url
                ),

                types.InlineKeyboardButton(
                    text=f"📥 Audio {i}",
                    callback_data=f"dl_{video['id']}"
                )
            )

        bot.send_message(
            message.chat.id,
            text_reply,
            reply_markup=markup,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

    else:

        bot.send_message(
            message.chat.id,
            "❌ Không tìm thấy kết quả"
        )

    bot.delete_message(
        message.chat.id,
        status.message_id
    )


# =========================
# SMART CHAT + MUSIC SEARCH
# =========================

@bot.message_handler(func=lambda message: True)
def smart_chat(message):

    text = message.text.lower()

    # CHAT

    if "chào" in text:

        bot.reply_to(
            message,
            "👋 Chào bạn nha!"
        )

        return

    elif "bạn là ai" in text:

        bot.reply_to(
            message,
            "🤖 Mình là Bot Trợ Lý Đa Năng!"
        )

        return

    elif "cảm ơn" in text:

        bot.reply_to(
            message,
            "❤️ Không có gì nha!"
        )

        return

    # SEARCH MUSIC

    search_music(message, message.text)


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    print("🤖 BOT ĐANG CHẠY...")

    bot.infinity_polling(skip_pending=True)