import requests
import os
from datetime import datetime, timedelta, timezone

# دریافت توکن‌ها از محیط امن گیت‌هاب (Secrets)
BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# مختصات تهران
lat, lon = 35.6892, 51.3890

def get_weather():
    try:
        # ۱. دریافت داده‌های فعلی و پیش‌بینی ۲۴ ساعته (با تنظیم تایم‌زون در API)
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,weathercode&timezone=Asia%2FTehran"
        weather_res = requests.get(weather_url).json()
        
        current = weather_res["current_weather"]
        hourly = weather_res["hourly"]
        
        temp_now = current["temperature"]
        w_code = current["weathercode"]
        
        # ۲. تحلیل ۲۴ ساعت آینده برای استخراج حداکثر و حداقل دما
        temps_24h = hourly["temperature_2m"][:24]
        max_temp = max(temps_24h)
        min_temp = min(temps_24h)
        
        # پیدا کردن ساعت وقوع (Index نشان‌دهنده ساعت است)
        max_hour = temps_24h.index(max_temp)
        min_hour = temps_24h.index(min_temp)

        # ۳. دریافت کیفیت هوا (AQI)
        air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
        air_res = requests.get(air_url).json()
        aqi = air_res["current"]["us_aqi"]

        # ۴. نقشه‌برداری وضعیت هوا به ایموجی و متن فارسی
        status_map = {
            0: ("☀️", "آفتابی"),
            1: ("🌤", "عمدتاً صاف"), 2: ("⛅", "نیمه ابری"), 3: ("☁️", "ابری"),
            45: ("🌫", "مه‌الود"), 48: ("🌫", "مه یخی"),
            61: ("🌧", "باران ملایم"), 63: ("🌧", "باران متوسط"), 65: ("🌧", "رگبار شدید"),
            80: ("🌦", "رگبار ملایم"), 95: ("⛈", "رعد و برق")
        }
        emoji, text = status_map.get(w_code, ("🌡", "مشخصات نامشخص"))

        # ۵. سیستم توصیه هوشمند مجید
        advice = ""
        if min_temp < 12:
            advice = "🧥 هوا رو به سردیه، حتماً لباس گرم همراهت باشه."
        elif max_temp > 34:
            advice = "☀️ اوج گرما بیرون نرو و آب زیاد بنوش."
        
        if aqi > 100:
            advice += "\n😷 آلودگی هوا بالاست، ترجیحاً ماسک بزن."

        # ۶. تنظیم دقیق ساعت بروزرسانی به وقت تهران (UTC+3:30)
        # این بخش مشکل اختلاف ساعت گیت‌هاب را حل می‌کند
        tz_tehran = timezone(timedelta(hours=3, minutes=30))
        tehran_time = datetime.now(tz_tehran).strftime("%H:%M")

        # ۷. ساخت بدنه پیام با فرمت Markdown
        message = (
            f"📊 *گزارش تحلیلی هوای تهران*\n\n"
            f"{emoji} وضعیت فعلی: {text}\n"
            f"🌡 دمای الان: {temp_now}°C\n"
            f"🏭 شاخص آلودگی: {aqi}\n\n"
            f"📈 *پیش‌بینی ۲۴ ساعت آینده:*\n"
            f"🔺 حداکثر دما: {max_temp}°C (ساعت {max_hour}:00)\n"
            f"🔻 حداقل دما: {min_temp}°C (ساعت {min_hour}:00)\n\n"
            f"💡 *توصیه به مجید:*\n"
            f"{advice if advice else '✅ شرایط جوی برای فعالیت‌های روزانه مناسب است.'}\n\n"
            f"🕒 بروزرسانی: {tehran_time}"
        )

        # ۸. ارسال درخواست به API پیام‌رسان بله
        url_bale = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url_bale, json=payload)
        
        if response.status_code == 200:
            print(f"Success: Message sent at {tehran_time}")
        else:
            print(f"Failed: {response.text}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    get_weather()
