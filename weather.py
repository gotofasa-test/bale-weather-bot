import requests
from datetime import datetime

# تنظیمات اصلی
BOT_TOKEN = "18466837:19kfxOWImyMAnDhqx1WQxhrllysRUh9BEa8"
CHAT_ID = "657206125"

# مختصات مرکز تهران
lat = 35.6892
lon = 51.3890

try:
    # 1. دریافت اطلاعات هواشناسی
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=weathercode"
    weather_res = requests.get(weather_url)
    weather_data = weather_res.json()

    temp = weather_data["current_weather"]["temperature"]
    weathercode = weather_data["current_weather"]["weathercode"]
    
    # بررسی پیش‌بینی 12 ساعت آینده برای هشدار
    future_codes = weather_data["hourly"]["weathercode"][:12]
    rain_upcoming = any(c in [61, 63, 65, 80, 81, 82] for c in future_codes)
    storm_upcoming = any(c in [95, 96, 99] for c in future_codes)

    # 2. دریافت کیفیت هوا
    air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
    air_res = requests.get(air_url)
    air_data = air_res.json()
    aqi = air_data["current"]["us_aqi"]

    # تعیین وضعیت کیفیت هوا
    if aqi <= 50:
        air_status = "پاک 🟢"
    elif aqi <= 100:
        air_status = "قابل قبول 🟡"
    elif aqi <= 150:
        air_status = "ناسالم برای گروه‌های حساس 🟠"
    elif aqi <= 200:
        air_status = "ناسالم 🔴"
    elif aqi <= 300:
        air_status = "بسیار ناسالم 🟣"
    else:
        air_status = "خطرناک ⚫"

    # تعیین وضعیت کلی و ایموجی
    w_emoji = "🌤"
    w_text = "نیمه ابری"
    
    if weathercode == 0:
        w_emoji, w_text = "☀️", "آفتابی"
    elif weathercode in [1, 2, 3]:
        w_emoji, w_text = "⛅", "نیمه ابری"
    elif weathercode in [45, 48]:
        w_emoji, w_text = "🌫", "مه آلود"
    elif weathercode in [61, 63, 65, 80, 81, 82]:
        w_emoji, w_text = "🌧", "بارانی"
    elif weathercode in [95, 96, 99]:
        w_emoji, w_text = "⛈", "طوفانی"

    # ساخت متن هشدار
    warnings = ""
    if aqi > 150:
        warnings += "\n🚨 هشدار: آلودگی شدید هوا!"
    if rain_upcoming:
        warnings += "\n⚠️ پیش‌بینی: احتمال بارش باران در ساعات آتی"
    if storm_upcoming:
        warnings += "\n⚠️ پیش‌بینی: احتمال رعد و برق و طوفان"

    # زمان بروزرسانی
    now = datetime.now().strftime("%H:%M")

    # ساخت پیام نهایی
    message = (
        f"🌍 گزارش وضعیت تهران\n\n"
        f"{w_emoji} وضعیت: {w_text}\n"
        f"🌡 دما: {temp}°C\n"
        f"🏭 شاخص کیفیت هوا: {aqi}\n"
        f"📊 وضعیت: {air_status}\n"
        f"{warnings}\n\n"
        f"🕒 بروزرسانی: {now}"
    )

    # ارسال به بله
    requests.post(
        f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": message}
    )
    print("Message sent successfully!")

except Exception as e:
    print(f"Error occurred: {e}")

