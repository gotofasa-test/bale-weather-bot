import requests
BOT_TOKEN = "18466837:19kfxOWImyMAnDhqx1WQxhrllysRUh9BEa8"
CHAT_ID = "657206125"

# مختصات مرکز تهران
lat = 35.6892
lon = 51.3890

# دریافت داده هوا
weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
weather_data = requests.get(weather_url).json()

temperature = weather_data["current_weather"]["temperature"]
weathercode = weather_data["current_weather"]["weathercode"]

# دریافت کیفیت هوا
air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"
air_data = requests.get(air_url).json()

aqi = air_data["current"]["us_aqi"]

# تبدیل AQI به سطح آلودگی
if aqi <= 50:
    air_status = "🟢 پاک"
elif aqi <= 100:
    air_status = "🟡 قابل قبول"
elif aqi <= 150:
    air_status = "🟠 ناسالم برای گروه‌های حساس"
elif aqi <= 200:
    air_status = "🔴 ناسالم"
elif aqi <= 300:
    air_status = "🟣 بسیار ناسالم"
else:
    air_status = "⚫ خطرناک"

# بررسی باران یا طوفان
warning = ""
if weathercode in [61,63,65,80,81,82]:
    warning = "\n⚠️ احتمال بارندگی در تهران"
elif weathercode in [95,96,99]:
    warning = "\n⚠️ هشدار طوفان یا رعد و برق"

message = f"""
🌤 گزارش وضعیت تهران

🌡 دما: {temperature}°C

🏭 شاخص کیفیت هوا (AQI): {aqi}
وضعیت: {air_status}

{warning}
"""

requests.post(
    f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage",
    json={
        "chat_id": CHAT_ID,
        "text": message
    }
)
