import json

import requests

import os

from datetime import datetime



TOKEN = "900766790:3zB3PpKNztdoPoON6STdUjprXgEECAMHYso"



BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}/"

OFFSET_FILE = "offset.json"

DATA_FILE = "youtube_links.json"





def load_offset():

    if not os.path.exists(OFFSET_FILE):

        return 0

    with open(OFFSET_FILE, "r", encoding="utf-8") as f:

        return json.load(f)





def save_offset(offset):

    with open(OFFSET_FILE, "w", encoding="utf-8") as f:

        json.dump(offset, f)





def get_updates(offset):

    url = BASE_URL + "getUpdates"

    params = {"offset": offset, "timeout": 0}

    res = requests.get(url, params=params).json()

    return res.get("result", [])





def send_message(chat_id, text):

    url = BASE_URL + "sendMessage"

    requests.post(url, json={"chat_id": chat_id, "text": text})







def is_youtube_link(text: str) -> bool:

    if not text:

        return False

    text = text.lower().strip()

    return (

        "youtube.com" in text

        or "youtu.be" in text

        or "m.youtube.com" in text

    )





def save_youtube_link(link: str, chat_id=None):

    data = []

    if os.path.exists(DATA_FILE):

        try:

            with open(DATA_FILE, "r", encoding="utf-8") as f:

                data = json.load(f)

        except json.JSONDecodeError:

            data = [] # اگر فایل خراب باشد، خالی شروع کن



    record = {

        "link": link,

        "chat_id": chat_id,

        "saved_at": datetime.now().isoformat()

    }



    data.append(record)



    with open(DATA_FILE, "w", encoding="utf-8") as f:

        json.dump(data, f, ensure_ascii=False, indent=2)







def process_message(update):

    message = update.get("message")

    if not message:

        return



    chat_id = message["chat"]["id"]

    text = message.get("text", "")



    if text == "/start":

        send_message(chat_id, "سلام! فقط پیام‌های جدید رو بررسی می‌کنم.")

    elif is_youtube_link(text):

        save_youtube_link(text, chat_id=chat_id)

        send_message(chat_id, "✅ لینک یوتیوب دریافت و در سرور ذخیره شد.")

    else:

        send_message(chat_id, "لطفاً یک لینک معتبر یوتیوب ارسال کنید.")





def main():

    last_offset = load_offset()

    updates = get_updates(last_offset + 1)



    for update in updates:

        process_message(update)

        last_offset = update["update_id"]



    save_offset(last_offset)





main()
