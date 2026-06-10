import requests
import os
from datetime import datetime, timedelta, timezone

BOT_TOKEN = os.getenv("BALE_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

lat = 35.6892
lon = 51.3890


def fetch_weather():
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=temperature_2m,weathercode&timezone=Asia%2FTehran"

    res = requests.get(url, timeout=20)
    res.raise_for_status()

    return res.json()


def fetch_air_quality():
    url = f"https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}&current=us_aqi"

    res = requests.get(url, timeout=20)
    res.raise_for_status()

    return res.json()


def send_bale_message(message):
    url = f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    res = requests.post(url, json=payload, timeout=20)
    res.raise_for_status()

    return res.json()


def analyze_weather(data):
    current = data.get("current_weather")
    hourly = data.get("hourly")

    if not current or not hourly:
        raise ValueError("Weather data structure invalid")

    temp_now = current["temperature"]
    weather_code = current["weathercode"]

    temps = hourly.get("temperature_2m", [])[:24]

    if len(temps) == 0:
        raise ValueError("No hourly temperature data")

    max_temp = max(temps)
    min_temp = min(temps)

    max_hour = temps.index(max_temp)
    min_hour = temps.index(min_temp)

    return temp_now, weather_code, max_temp, min_temp, max_hour, min_hour


def weather_status(code):
    mapping = {
        0: ("☀️", "آفتابی"),
        1: ("🌤", "عمدتاً صاف"),
        2: ("⛅", "نیمه ابری"),
        3: ("☁️", "ابری"),
        45: ("🌫", "مه"),
        48: ("🌫", "مه یخی"),
        61: ("🌧", "باران ملایم"),
        63: ("🌧", "باران متوسط"),
        65: ("🌧", "باران شدید"),
        80: ("🌦", "رگبار"),
        95: ("⛈", "رعد و برق")
    }

    return mapping.get(code, ("🌡", "نامشخص"))


def generate_advice(min_temp, max_temp, aqi):
    advice = []

    if min_temp < 12:
        advice.append("🧥 هوا سرد می‌شود، لباس گرم همراه داشته باش.")

    if max_temp > 34:
        advice.append("☀️ گرمای شدید؛ آب زیاد بنوش.")

    if aqi > 100:
        advice.append("😷 آلودگی هوا بالاست؛ بهتر است ماسک بزن.")

    if not advice:
        advice.append("✅ شرایط جوی مناسب است.")

    return "\n".join(advice)


def build_message(temp_now, weather_code, max_temp, min_temp, max_hour, min_hour, aqi):
    emoji, text = weather_status(weather_code)

    tz = timezone(timedelta(hours=3, minutes=30))
    now = datetime.now(tz).strftime("%H:%M")

    advice = generate_advice(min_temp, max_temp, aqi)

    message = (
        f"📊 *گزارش هوای تهران*\n\n"
        f"{emoji} وضعیت: {text}\n"
        f"🌡 دمای فعلی: {temp_now}°C\n"
        f"🏭 شاخص آلودگی: {aqi}\n\n"
        f"📈 *پیش‌بینی ۲۴ ساعت آینده*\n"
        f"🔺 بیشینه: {max_temp}°C (ساعت {max_hour}:00)\n"
        f"🔻 کمینه: {min_temp}°C (ساعت {min_hour}:00)\n\n"
        f"💡 *توصیه*\n"
        f"{advice}\n\n"
        f"🕒 بروزرسانی: {now}"
    )

    return message


def main():
    try:
        weather_data = fetch_weather()
        air_data = fetch_air_quality()

        temp_now, code, max_temp, min_temp, max_hour, min_hour = analyze_weather(weather_data)

        aqi = air_data["current"]["us_aqi"]

        message = build_message(
            temp_now,
            code,
            max_temp,
            min_temp,
            max_hour,
            min_hour,
            aqi
        )

        send_bale_message(message)

        print("✅ Weather message sent successfully")

    except Exception as e:
        print("❌ Error:", e)


if __name__ == "__main__":
    main()
