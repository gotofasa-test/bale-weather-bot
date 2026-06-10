import requests

BOT_TOKEN = "18466837:19kfxOWImyMAnDhqx1WQxhrllysRUh9BEa8"
CHAT_ID = "657206125"

weather = requests.get("https://wttr.in/Tehran?format=3").text

text = f"وضعیت آب و هوای تهران:\n\n{weather}"

requests.post(
    f"https://tapi.bale.ai/bot{BOT_TOKEN}/sendMessage",
    json={
        "chat_id": CHAT_ID,
        "text": text
    }
)
