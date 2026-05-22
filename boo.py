import requests

BOT_TOKEN = "900766790:3zB3PpKNztdoPoON6STdUjprXgEECAMHYso"


from flask import Flask, request

BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

app = Flask(__name__)

def send_photo(chat_id, file_path="test.jpg", caption=""):
    url = f"{BASE_URL}/sendPhoto"
    with open(file_path, "rb") as photo:
        files = {"photo": photo}
        data = {"chat_id": chat_id, "caption": caption}
        return requests.post(url, data=data, files=files).json()

@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json()

    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")

    if text == "start":
        send_photo(chat_id, "test.jpg", "این فایل test.jpg است")

    return "ok"

if __name__ == "__main__":
    app.run(port=5000)



