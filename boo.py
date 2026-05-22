import requests

BOT_TOKEN = "900766790:3zB3PpKNztdoPoON6STdUjprXgEECAMHYso"

import time
FILE_PATH = "test.jpg"

BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

def get_updates(offset=None):
    url = f"{BASE_URL}/getUpdates"
    params = {
        "offset": offset,
        "timeout": 30
    }
    try:
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("Error in get_updates:", e)
        return {"result": []}

def send_photo(chat_id, file_path):
    url = f"{BASE_URL}/sendPhoto"
    try:
        with open(file_path, "rb") as photo:
            files = {"photo": photo}
            data = {"chat_id": chat_id}
            r = requests.post(url, data=data, files=files)
            r.raise_for_status()
            return r.json()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print("Error in send_photo:", e)

def main():
    offset = 0
    print("Bot is running...")
    if 1>0:
        updates = get_updates(offset)

        for update in updates.get("result", []):
            offset = update["update_id"] + 1

            message = update.get("message")
            if not message:
                continue

            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            # برای هر پیام، عکس را ارسال می‌کند
            print(f"Message received from {chat_id}: {text}")
            send_photo(chat_id, FILE_PATH)

        

if __name__ == "__main__":
    main()




