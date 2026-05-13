import json
import requests
import os

TOKEN = "900766790:3zB3PpKNztdoPoON6STdUjprXgEECAMHYso"

BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}/"

QUEUE_FILE = "queue.json"


def load_queue():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue, f, ensure_ascii=False, indent=2)


def get_updates(offset=None):
    url = BASE_URL + "getUpdates"
    params = {"timeout": 0}
    if offset:
        params["offset"] = offset

    res = requests.get(url, params=params).json()
    return res.get("result", [])


def send_message(chat_id, text):
    url = BASE_URL + "sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": text})


def process_message(msg):
    chat_id = msg["message"]["chat"]["id"]
    text = msg["message"].get("text", "")

    # Example command:
    if text == "/start":
        send_message(chat_id, "سلام! ربات بعد ۲۰ دقیقه پیام‌هات رو بررسی می‌کنه.")
    else:
        send_message(chat_id, f"پیام دریافت شد:\n{text}")


def main():
    queue = load_queue()

    # Fetch new updates
    latest_update_id = None
    if queue:
        latest_update_id = queue[-1]["update_id"] + 1

    updates = get_updates(offset=latest_update_id)

    # Add new updates to queue
    if updates:
        queue.extend(updates)
        save_queue(queue)

    # Process queued messages
    for msg in queue:
        process_message(msg)

    # Clear queue after processing
    save_queue([])


if __name__ == "__main__":
    main()
