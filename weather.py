import requests
from datetime import datetime

BOT_TOKEN = "18466837:19kfxOWImyMAnDhqx1WQxhrllysRUh9BEa8"
CHAT_ID = "657206125"

lat = 35.6892
lon = 51.3890

# دریافت اطلاعات هوا
weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
weather = requests.get(weather_url).json()

temp = weather["current_weather"]["temperature"]
weathercode = weather["current_weather"]["weathercode"]

# دریافت کیفیت هوا
air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
air = requests.get(air_url).json()

aqi = air["current"]["us_aqi"]

# وضعیت کیفیت هوا
if aqi <= 50:
    air_status = "🟢 پاک"
elif aqi <= 100:
    air_status = "🟡 قابل قبول"
elif aqi <= 150:
    air_status = "🟠 ناسالم برای حساس‌ها"
elif aqi <= 200:
    air_status = "🔴 ناسالم"
elif aqi <= 300:
    air_status = "🟣 بسیار ناسالم"
else:
    air_status = "⚫ خطرناک"

# ایموجی وضعیت هوا
weather_emoji = "🌤"
weather_text = "نیمه ابری"

if weathercode == 0:
    weather_emoji = "☀️"
    weather_text = "آفتابی"

elif weathercode in [1,2,3]:
    weather_emoji = "⛅"
    weather_text = "نیمه ابری"

elif weathercode in [45,48]:
    weather_emoji = "🌫"
    weather_text = "مه آلود"

elif weathercode in [61,63,65,80,81,82]:
    weather_emoji = "🌧"
    weather_بارانی"

elif weathercode in [95,96,99]:
    weather_emoji = "⛈"
    weather_text = "طوفانی"

# هشدار
warning = ""

if weathercode in [61,63,65,80,81,82]:
    warning = "⚠️ هشدار: احتمال بارندگی"

if weathercode in [95,96,99]:
    warning = "⚠️ هشدار: احتمال طوفان و رعد و برق"

# زمان بروزرسانی
time = datetime.now().
