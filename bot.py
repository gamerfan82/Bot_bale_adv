import json
import requests
import os

TOKEN = "900766790:3zB3PpKNztdoPoON6STdUjprXgEECAMHYso"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}/"
OFFSET_FILE = "offset.json"


def load_offset():
    if not os.path.exists(OFFSET_FILE):
        return 0
    with open(OFFSET_FILE, "r") as f:
        return json.load(f)


def save_offset(offset):
    with open(OFFSET_FILE, "w") as f:
        json.dump(offset, f)


def get_updates(offset):
    url = BASE_URL + "getUpdates"
    res = requests.get(url, params={"offset": offset}).json()
    return res.get("result", [])


def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


def process_message(msg):
    message = msg.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        send_message(chat_id, "سلام! فقط پیام‌های جدید رو بررسی می‌کنم.")
    else:
        send_message(chat_id, f"پیام جدید دریافت شد:\n{text}")


def main():
    last_offset = load_offset()

    updates = get_updates(last_offset + 1)

    for msg in updates:
        process_message(msg)
        last_offset = msg["update_id"]

    save_offset(last_offset)


if __name__ == "__main__":
    main()
