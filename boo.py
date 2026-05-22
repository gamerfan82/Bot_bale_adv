import requests

BOT_TOKEN = "900766790:3zB3PpKNztdoPoON6STdUjprXgEECAMHYso"
BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"

def send_photo(chat_id, file_path="test.jpg", caption=""):
    url = f"{BASE_URL}/sendPhoto"
    
    with open(file_path, "rb") as photo:
        files = {
            "photo": photo
        }
        data = {
            "chat_id": chat_id,
            "caption": caption
        }
        response = requests.post(url, data=data, files=files)
    
    return response.json()

if __name__ == "__main__":
    chat_id = "USER_CHAT_ID"
    result = send_photo(chat_id, "test.jpg", "این هم فایل شما")
    print(result)
