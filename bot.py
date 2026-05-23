import requests

import json



BOT_TOKEN = "900766790:3zB3PpKNztdoPoON6STdUjprXgEECAMHYso"

FILE_PATH = "test.jpg"

DATA_FILE = "youtube_links.json"





BASE_URL = f"https://tapi.bale.ai/bot{BOT_TOKEN}"



def save_youtube_link(data):

    with open(DATA_FILE, "w", encoding="utf-8") as f:

        json.dump(data, f, ensure_ascii=False, indent=2)





def send_document(chat_id, file_path):

    try:

        with open(file_path, 'rb') as f:

            files = {'document': (file_path.split('/')[-1], f)}

            payload = {

                "chat_id": chat_id,

                # می‌توانید caption هم اضافه کنید

                # "caption": "فایل zip شما"

            }

            response = requests.post(f"{BASE_URL}/sendDocument", data=payload, files=files, timeout=30)

            response.raise_for_status()

            print(f"فایل '{file_path}' به {chat_id} ارسال شد.")

    except FileNotFoundError:

        print(f"خطا: فایل در مسیر '{file_path}' پیدا نشد.")

    except requests.exceptions.RequestException as e:

        print(f"خطا در ارسال فایل به {chat_id}: {e}")

    except Exception as e:

        print(f"خطای ناشناخته در send_document: {e}")



def main():

        with open(DATA_FILE, "r", encoding="utf-8") as f:

            ret = json.load(f)

            i = ret.pop()

            chat_id = i["chat_id"]

            name_file = i["link"][-5:] + ".zip"

            print(name_file)

            send_document(chat_id, FILE_PATH)

            if len(ret) > 0:

                save_youtube_link(ret)

            else:

                print("mession compelet")





main()
