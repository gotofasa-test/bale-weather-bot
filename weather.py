import os
import requests
from datetime import datetime
import pytz

# تنظیمات اصلی از محیط (Secrets)
BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CITY_LAT = "35.6944"  # تهران
CITY_LON = "51.4215"

def get_weather():
    try:
        # ۱. دریافت داده‌های هواشناسی با Timeout 15 ثانیه
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={CITY_LAT}&longitude={CITY_LON}&current_weather=true&hourly=temperature_2m&timezone=Asia%2FTehran"
        res = requests.get(weather_url, timeout=15)
        res.raise_for_status() # اگر خطا داد، اینجا متوقف شو
        data = res.json()

        current = data.get("current_weather", {})
        temp = current.get("temperature", "N/A")
        wind = current.get("windspeed", "N/A")
        
        # تحلیل دمای ۲۴ ساعت آینده
        hourly_temps = data.get("hourly", {}).get("temperature_2m", [])[:24]
        max_t = max(hourly_temps) if hourly_temps else "N/A"
        min_t = min(hourly_temps) if hourly_temps else "N/A"

        # ۲. دریافت شاخص آلودگی (AQI)
        air_url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={CITY_LAT}&longitude={CITY_LON}&current=us_aqi"
        air_res = requests.get(air_url, timeout=15)
        air_res.raise_for_status()
        aqi = air_res.json().get("current", {}).get("us_aqi", "N/A")

        return temp, max_t, min_t, wind, aqi
    except Exception as e:
        print(f"❌ Error fetching data: {e}")
        return None

def send_to_bale(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ Secrets are missing!")
        return
    
    url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("✅ Message sent successfully!")
        else:
            print(f"❌ Bale API error: {response.text}")
    except Exception as e:
        print(f"❌ Failed to connect to Bale: {e}")

def main():
    data = get_weather()
    if not data:
        return # اگر داده‌ای نگرفتیم، ادامه نده

    temp, max_t, min_t, wind, aqi = data
    tehran_time = datetime.now(pytz.timezone("Asia/Tehran")).strftime("%H:%M")
    
    # تعیین وضعیت آلودگی
    aqi_status = "🟢 پاک" if aqi <= 50 else "🟡 متوسط" if aqi <= 100 else "🔴 ناسالم"

    msg = (
        f"🌡 *گزارش وضعیت هوای تهران*\n\n"
        f"🕒 زمان: {tehran_time}\n"
        f"🌡 دمای فعلی: {temp}°C\n"
        f"🔼 حداکثر (۲۴س): {max_t}°C\n"
        f"🔽 حداقل (۲۴س): {min_t}°C\n"
        f"💨 سرعت باد: {wind} km/h\n"
        f"😷 شاخص آلودگی: {aqi} ({aqi_status})\n\n"
        f"📌 *توصیه:* " + ("امروز هوا برای پیاده‌روی عالیه!" if aqi <= 50 else "مراقب سلامتی خود باشید.")
    )
    
    send_to_bale(msg)

if __name__ == "__main__":
    main()
