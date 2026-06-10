import requests
import os
from datetime import datetime
from datetime import datetime, timedelta, timezone

# دریافت توکن‌ها از محیط امن گیت‌هاب
BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# مختصات تهران
lat, lon = 35.6892, 51.3890

def get_weather():
    try:
        # دریافت داده‌های فعلی و پیش‌بینی ۲۴ ساعته
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,weathercode&timezone=Asia%2FTehran"
        res = requests.get(url).json()
        
        current = res["current_weather"]
        hourly = res["hourly"]
        
        temp_now = current["temperature"]
        w_code = current["weathercode"]
        
        # تحلیل ۲۴ ساعت آینده
        temps_24h = hourly["temperature_2m"][:24]
        max_temp = max(temps_24h)
        min_temp = min(temps_24h)
        
        # پیدا کردن ساعت وقوع دماهای حدی
        max_hour = temps_24h.index(max_temp)
        min_hour = temps_24h.index(min_temp)

        # دریافت کیفیت هوا
        air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
        aqi = requests.get(air_url).json()["current"]["us_aqi"]

        # ایموجی و متن وضعیت
        status_map = {
            0: ("☀️", "آفتابی"),
            1: ("🌤", "عمدتاً صاف"), 2: ("⛅", "نیمه ابری"), 3: ("☁️", "ابری"),
            45: ("🌫", "مه‌الود"), 48: ("🌫", "مه یخی"),
            61: ("🌧", "باران ملایم"), 63: ("🌧", "باران متوسط"), 65: ("🌧", "رگبار شدید"),
            95: ("⛈", "رعد و برق")
        }
        emoji, text = status_map.get(w_code, ("🌡", "نامشخص"))

        # تحلیل و توصیه
        advice = ""
        if min_temp < 15:
            advice = "🧥 شب یا صبح زود هوا خنک میشه، لباس گرم یادت نره!"
        elif max_temp > 35:
            advice = "☀️ ظهر هوا خیلی گرمه، زیاد بیرون نمون."
        
        if aqi > 100:
            advice += "\n😷 آلودگی بالاست، ترجیحاً ماسک بزن."

        # ساخت پیام نهایی با ساختار جدید
        offset = timezone(timedelta(hours=3, minutes=30))
        tehran_time = datetime.now(offset).strftime("%H:%M")
        message = (
            f"..."
            f"🕒 بروزرسانی: {tehran_time}"
        )

        
        message = (
            f"📊 **گزارش تحلیلی هوای تهران**\n\n"
            f"{emoji} وضعیت فعلی: {text}\n"
            f"🌡 دمای الان: {temp_now}°C\n"
            f"🏭 شاخص آلودگی: {aqi}\n\n"
            f"📈 پیش‌بینی ۲۴ ساعت آینده:\n"
            f"🔺 حداکثر دما: {max_temp}°C (ساعت {max_hour}:00)\n"
            f"🔻 حداقل دما: {min_temp}°C (ساعت {min_hour}:00)\n\n"
            f"💡 **توصیه مجید:**\n"
            f"{advice if advice else '✅ شرایط جوی برای فعالیت عادی مساعد است.'}\n\n"
            f"🕒 بروزرسانی: {now_time}"
        )

        # ارسال به بله
        requests.post(
            f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
        )
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_weather()
