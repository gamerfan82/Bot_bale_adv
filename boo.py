import requests

import json



# اطلاعات اولیه فایل (می‌توانید اینها را تغییر دهید)

file_name = "test.JPG"

file_size = 21878  # حجم فایل به بایت

file_mime = "image/jpeg"

password = ""  # رمز عبور در صورت نیاز

expiry_hours = 12

gallery_visible = 0

gallery_title = ""



# کوکی‌ها (این را با کوکی‌های خودتان جایگزین کنید)

cookies = {

    "pp_vid": "1e93c0e6f53587b29b5d333ae1be6f78",

    "PHPSESSID": "0463492c8a821cb83a292e61b7e88a5e"

}



# ----------- مرحله اول: ارسال اطلاعات اولیه فایل -----------

url_init = "https://punkpaste.ir/upload/init"

headers_init = {

    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",

    "Accept": "*/*",

    "Origin": "https://punkpaste.ir",

    "Sec-Fetch-Site": "same-origin",

    "Sec-Fetch-Mode": "cors",

    "Sec-Fetch-Dest": "empty",

    "Referer": "https://punkpaste.ir/",

    "Accept-Encoding": "gzip, deflate, br",

    "Accept-Language": "en,en-US;q=0.9,fa;q=0.8"

}

payload_init = {

    "name": file_name,

    "size": file_size,

    "mime": file_mime,

    "password": password,

    "expiry_hours": expiry_hours,

    "gallery_visible": gallery_visible,

    "gallery_title": gallery_title

}



response_init = requests.post(url_init, headers=headers_init, cookies=cookies, data=payload_init)



if response_init.status_code == 200:

    try:

        init_data = response_init.json()

        upload_id = init_data.get("upload_id")

        print(f"شناسه آپلود دریافت شد: {upload_id}")



        # ----------- مرحله دوم: ارسال تکه فایل -----------

        # فرض می‌کنیم فایل در مسیر فعلی قرار دارد. اگر در مسیر دیگری است، مسیر کامل را بدهید.

        file_path = file_name

        chunk_index = 0

        url_chunk = f"https://punkpaste.ir/upload/chunk/{upload_id}?index={chunk_index}"

        headers_chunk = {

            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",

            "Content-Type": "application/octet-stream",

            "Accept": "*/*",

            "Origin": "https://punkpaste.ir",

            "Sec-Fetch-Site": "same-origin",

            "Sec-Fetch-Mode": "cors",

            "Sec-Fetch-Dest": "empty",

            "Referer": "https://punkpaste.ir/",

            "Accept-Encoding": "gzip, deflate, br",

            "Accept-Language": "en,en-US;q=0.9,fa;q=0.8"

        }



        with open(file_path, 'rb') as f:

            file_data = f.read()



        response_chunk = requests.post(url_chunk, headers=headers_chunk, cookies=cookies, data=file_data)



        if response_chunk.status_code == 200:

            print("تکه فایل با موفقیت ارسال شد.")



            # ----------- مرحله سوم: تکمیل آپلود -----------

            url_complete = f"https://punkpaste.ir/upload/complete/{upload_id}"

            headers_complete = {

                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",

                "Content-Length": "0",

                "Accept": "*/*",

                "Origin": "https://punkpaste.ir",

                "Sec-Fetch-Site": "same-origin",

                "Sec-Fetch-Mode": "cors",

                "Sec-Fetch-Dest": "empty",

                "Referer": "https://punkpaste.ir/",

                "Accept-Encoding": "gzip, deflate, br",

                "Accept-Language": "en,en-US;q=0.9,fa;q=0.8"

            }



            response_complete = requests.post(url_complete, headers=headers_complete, cookies=cookies)



            if response_complete.status_code == 200:

                print("آپلود با موفقیت کامل شد!")

                try:

                    complete_data = response_complete.json()

                    print("لینک فایل:", complete_data.get("link"))

                except json.JSONDecodeError:

                    print("پاسخ تکمیل آپلود JSON معتبر نیست.")

            else:

                print(f"خطا در تکمیل آپلود. کد وضعیت: {response_complete.status_code}")

                print("پاسخ:", response_complete.text)

        else:

            print(f"خطا در ارسال تکه فایل. کد وضعیت: {response_chunk.status_code}")

            print("پاسخ:", response_chunk.text)

    except json.JSONDecodeError:

        print("پاسخ اولیه آپلود JSON معتبر نیست.")

        print("پاسخ:", response_init.text)

else:

    print(f"خطا در مرحله اولیه آپلود. کد وضعیت: {response_init.status_code}")

    print("پاسخ:", response_init.text)

