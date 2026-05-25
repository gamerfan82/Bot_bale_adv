
import subprocess
import tempfile
import os
import sys
import zipfile
from pathlib import Path
import shutil
import requests
import json



def process_message(update):
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        send_message(chat_id, "سلام! فقط پیام‌های جدید رو بررسی می‌کنم.")
    elif is_youtube_link(text):
        print(f"link={text}")
        # دانلود ویدیو و ساخت فایل زیپ
        download_youtube_video(text)   # فایل video.zip ساخته می‌شود

        zip_path = "video.zip"
        if not os.path.exists(zip_path):
            send_message(chat_id, "❌ خطا در ساخت فایل زیپ.")
            return

        file_size = os.path.getsize(zip_path)
        max_size = 19 * 1024 * 1024  # 19 مگابایت

        if file_size <= max_size:
            # فایل کوچک است، مستقیماً ارسال کن
            send_message(chat_id, "✅ دانلود تمام شد. فایل در حال ارسال...")
            send_document(chat_id, zip_path)
        else:
            # فایل بزرگتر از 19 مگ، باید قطعه‌قطعه شود
            send_message(chat_id, "⚠️ حجم فایل بیش از ۱۹ مگابایت است. در حال خرد کردن و ارسال قطعات...")
            part_files = split_file(zip_path, max_size)
            total_parts = len(part_files)
            for idx, part in enumerate(part_files, start=1):
                caption = f"بخش {idx} از {total_parts}"
                send_document(chat_id, part, caption=caption)
            # پاکسازی قطعات بعد از ارسال (اختیاری)
            for part in part_files:
                try:
                    os.remove(part)
                except:
                    pass

        # پاکسازی فایل زیپ اصلی (اختیاری)
        try:
            os.remove(zip_path)
        except:
            pass
        send_message(chat_id, "✅ ارسال کامل شد.")
    else:
        send_message(chat_id, "لطفاً یک لینک معتبر یوتیوب ارسال کنید.")

def get_common_flags(quality, output_dir):
    """پرچم‌های مشترک yt-dlp بر اساس نوع کیفیت."""
    base = [
        "--output", f"{output_dir}/%(title)s.%(ext)s",
        "--no-part",
        "--no-playlist",
        "--retries", "5",
        "--fragment-retries", "5",
        "--no-check-certificates",
        "--concurrent-fragments", "8",
        "--buffer-size", "16K",
        "--http-chunk-size", "10M",
        "--progress",
        "--newline",
        "--no-cache-dir",
    ]
    if quality == "audio":
        base.extend([
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
        ])
    else:
        # برای ویدیو (شامل qualityهای رزولوشن و "best")
        base.extend([
            "--merge-output-format", "mp4",
            "--write-thumbnail",
            "--convert-thumbnails", "jpg",
        ])
        if quality == "best":
            # مرتب‌سازی برای بهترین کیفیت
            base.append("--format-sort")
            base.append("res,+codec:vp9.1,+size")
    return base


def get_format_string(quality):
    """رشته فرمت ویدیو بر اساس کیفیت درخواستی."""
    if quality == "audio":
        return "bestaudio/bestaudio*/best"
    if quality == "best":
        return "bestvideo+bestaudio/bestvideo*+bestaudio*/best"
    if quality in ("2160", "4k"):
        return "bestvideo[height<=2160]+bestaudio/bestvideo[height<=2160]*+bestaudio*/bestvideo+bestaudio/best"
    if quality in ("1440", "2k"):
        return "bestvideo[height<=1440]+bestaudio/bestvideo[height<=1440]*+bestaudio*/bestvideo+bestaudio/best"
    if quality == "1080":
        return "bestvideo[height<=1080]+bestaudio/bestvideo[height<=1080]*+bestaudio*/bestvideo+bestaudio/best"
    if quality == "720":
        return "bestvideo[height<=720]+bestaudio/bestvideo[height<=720]*+bestaudio*/bestvideo+bestaudio/best"
    if quality == "480":
        return "bestvideo[height<=480]+bestaudio/bestvideo[height<=480]*+bestaudio*/bestvideo+bestaudio/best"
    if quality == "360":
        return "bestvideo[height<=360]+bestaudio/bestvideo[height<=360]*+bestaudio*/bestvideo+bestaudio/best"
    # پیش‌فرض
    return "bestvideo+bestaudio/bestvideo*+bestaudio*/best"


# ----------------------------------------------------------------------
# توابع دانلود (۸ روش مختلف)
# ----------------------------------------------------------------------
def download_method_1(url, fmt, output_dir, proxy):
    """web + deno + ejs:github + proxy"""
    cmd = ["yt-dlp", "--proxy", proxy, "--format", fmt]
    cmd.extend(get_common_flags("video", output_dir))
    cmd.extend([
        "--extractor-args", "youtube:player_client=web",
        "--js-runtimes", "deno",
        "--remote-components", "ejs:github",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "--add-header", "Accept-Language:en-US,en;q=0.9",
        url
    ])
    return run_cmd(cmd)

def download_method_2(url, fmt, output_dir, proxy):
    """web + deno + ejs:npm + proxy"""
    cmd = ["yt-dlp", "--proxy", proxy, "--format", fmt]
    cmd.extend(get_common_flags("video", output_dir))
    cmd.extend([
        "--extractor-args", "youtube:player_client=web",
        "--js-runtimes", "deno",
        "--remote-components", "ejs:npm",
        "--user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "--add-header", "Accept-Language:en-US,en;q=0.9",
        url
    ])
    return run_cmd(cmd)

def download_method_3(url, fmt, output_dir, proxy):
    """web,mweb,android_vr + deno + ejs:github + proxy"""
    cmd = ["yt-dlp", "--proxy", proxy, "--format", fmt]
    cmd.extend(get_common_flags("video", output_dir))
    cmd.extend([
        "--extractor-args", "youtube:player_client=web,mweb,android_vr",
        "--js-runtimes", "deno",
        "--remote-components", "ejs:github",
        url
    ])
    return run_cmd(cmd)

def download_method_4(url, fmt, output_dir, proxy):
    """mweb + proxy"""
    cmd = ["yt-dlp", "--proxy", proxy, "--format", fmt]
    cmd.extend(get_common_flags("video", output_dir))
    cmd.extend([
        "--extractor-args", "youtube:player_client=mweb",
        url
    ])
    return run_cmd(cmd)

def download_method_5(url, fmt, output_dir, proxy):
    """android_vr + proxy"""
    cmd = ["yt-dlp", "--proxy", proxy, "--format", fmt]
    cmd.extend(get_common_flags("video", output_dir))
    cmd.extend([
        "--extractor-args", "youtube:player_client=android_vr",
        url
    ])
    return run_cmd(cmd)

def download_method_6(url, fmt, output_dir):
    """web + deno + ejs:github بدون پروکسی"""
    cmd = ["yt-dlp", "--format", fmt]
    cmd.extend(get_common_flags("video", output_dir))
    cmd.extend([
        "--extractor-args", "youtube:player_client=web",
        "--js-runtimes", "deno",
        "--remote-components", "ejs:github",
        url
    ])
    return run_cmd(cmd)

def download_method_7(url, fmt, output_dir):
    """mweb بدون پروکسی"""
    cmd = ["yt-dlp", "--format", fmt]
    cmd.extend(get_common_flags("video", output_dir))
    cmd.extend([
        "--extractor-args", "youtube:player_client=mweb",
        url
    ])
    return run_cmd(cmd)

def download_method_8(url, fmt, output_dir, proxy):
    """android + proxy (آخرین راهکار)"""
    cmd = ["yt-dlp", "--proxy", proxy, "--format", fmt]
    cmd.extend(get_common_flags("video", output_dir))
    cmd.extend([
        "--extractor-args", "youtube:player_client=android",
        "--user-agent", "Mozilla/5.0 (Linux; Android 12; SM-S906N Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36",
        url
    ])
    return run_cmd(cmd)


def run_cmd(cmd):
    """اجرای یک دستور و برگرداندن True در صورت موفقیت."""
    print(f"[*] Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)  # خروجی را در ترمینال نشان می‌دهیم
    return result.returncode == 0


# ----------------------------------------------------------------------
# تابع اصلی دانلود و زیپ کردن
# ----------------------------------------------------------------------
def download_youtube_video(url, quality="480", proxy="socks5://127.0.0.1:1080", zip_password="erfan", output_zip="video.zip"):
    """
    دانلود ویدیو از یوتیوب با استفاده از روش‌های مختلف.
    سپس فایل ویدیویی را در فایل زیپ (با رمز اختیاری) ذخیره می‌کند.
    """
    # ایجاد دایرکتوری موقت برای دانلود
    tmp_dir = tempfile.mkdtemp(prefix="yt_download_")
    print(f"[+] Temporary download directory: {tmp_dir}")

    # تعیین رشته فرمت و پرچم‌های کیفیت
    fmt_str = get_format_string(quality)
    if quality == "audio":
        flag_quality = "audio"
    else:
        flag_quality = "video"  # از توابع مشترک استفاده می‌کنیم

    # لیست توابع دانلود (نام، فراخوانی، نیاز به proxy)
    methods = [
        ("method 1 (web+deno+ejs:github+proxy)", lambda: download_method_1(url, fmt_str, tmp_dir, proxy)),
        ("method 2 (web+deno+ejs:npm+proxy)", lambda: download_method_2(url, fmt_str, tmp_dir, proxy)),
        ("method 3 (web,mweb,android_vr+deno+ejs:github+proxy)", lambda: download_method_3(url, fmt_str, tmp_dir, proxy)),
        ("method 4 (mweb+proxy)", lambda: download_method_4(url, fmt_str, tmp_dir, proxy)),
        ("method 5 (android_vr+proxy)", lambda: download_method_5(url, fmt_str, tmp_dir, proxy)),
        ("method 6 (web+deno+ejs:github - no proxy)", lambda: download_method_6(url, fmt_str, tmp_dir)),
        ("method 7 (mweb - no proxy)", lambda: download_method_7(url, fmt_str, tmp_dir)),
        ("method 8 (android+proxy - last resort)", lambda: download_method_8(url, fmt_str, tmp_dir, proxy)),
    ]

    download_success = False
    for name, func in methods:
        print(f"\n[>] Trying {name}...")
        if func():
            print(f"[✓] {name} succeeded.")
            download_success = True
            break
        else:
            print(f"[✗] {name} failed. Moving to next method.")

    if not download_success:
        print("[✗] All download methods failed.")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        sys.exit(1)

    # پاکسازی فایل‌های ناقص و thumbnail (همانند workflow)
    for f in Path(tmp_dir).glob("*.part"):
        os.remove(f)
    for ext in ["*.jpg", "*.webp"]:
        for f in Path(tmp_dir).glob(ext):
            os.remove(f)

    # پیدا کردن فایل ویدیویی دانلود شده
    video_file = None
    for ext in ["*.mp4", "*.webm", "*.mkv"]:
        candidates = list(Path(tmp_dir).glob(ext))
        if candidates:
            video_file = str(candidates[0])
            break

    if not video_file:
        print("[✗] No video file found in download directory.")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        sys.exit(1)

    print(f"[+] Downloaded video: {video_file}")

    # ایجاد فایل زیپ (در صورت داشتن رمز، رمزگذاری شود)
    try:
        if zip_password:
            print(f"[*] Creating encrypted zip: {output_zip}")
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.setpassword(zip_password.encode('utf-8'))
                zf.write(video_file, arcname=os.path.basename(video_file))
        else:
            print(f"[*] Creating zip: {output_zip}")
            with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(video_file, arcname=os.path.basename(video_file))
        print(f"[✓] Video zipped successfully -> {output_zip}")
    except Exception as e:
        print(f"[✗] Failed to create zip: {e}")
        shutil.rmtree(tmp_dir, ignore_errors=True)
        sys.exit(1)

    # پاکسازی دایرکتوری موقت
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print("[+] Temporary files cleaned up.")


#------------------------------------------------------------------
# bot bale

TOKEN = "900766790:3zB3PpKNztdoPoON6STdUjprXgEECAMHYso"
BASE_URL = f"https://tapi.bale.ai/bot{TOKEN}/"
OFFSET_FILE = "offset.json"
DATA_FILE = "youtube_links.json"

# ---------- توابع کمکی ----------
def split_file(file_path, chunk_size=19*1024*1024):
    """
    فایل را به قطعات chunk_size بایتی تقسیم کرده و لیست نام فایل‌های قطعه را برمی‌گرداند.
    """
    part_files = []
    base_name = file_path
    with open(file_path, 'rb') as f:
        part_num = 1
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            part_name = f"{base_name}.part{part_num}"
            with open(part_name, 'wb') as part_file:
                part_file.write(chunk)
            part_files.append(part_name)
            part_num += 1
    return part_files

def send_document(chat_id, file_path, caption=None):
    try:
        with open(file_path, 'rb') as f:
            files = {'document': (file_path.split('/')[-1], f)}
            payload = {"chat_id": chat_id}
            if caption:
                payload["caption"] = caption
            response = requests.post(f"{BASE_URL}sendDocument", data=payload, files=files, timeout=30)
            response.raise_for_status()
            print(f"فایل '{file_path}' به {chat_id} ارسال شد.")
    except FileNotFoundError:
        print(f"خطا: فایل در مسیر '{file_path}' پیدا نشد.")
    except requests.exceptions.RequestException as e:
        print(f"خطا در ارسال فایل به {chat_id}: {e}")
    except Exception as e:
        print(f"خطای ناشناخته در send_document: {e}")

# سایر توابع بدون تغییر (get_common_flags, get_format_string, download_method_*, ...)

# در تابع process_message، بخش پس از دانلود را به‌روز کنید:

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



def process_message(update):
    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if text == "/start":
        send_message(chat_id, "سلام! فقط پیام‌های جدید رو بررسی می‌کنم.")
    elif is_youtube_link(text):
        print(f"link={text}")
        download_youtube_video(text)
        send_message(chat_id, "✅ لینک یوتیوب دریافت و در سرور ذخیره شد.")
        send_document(chat_id, "video.zip")
    else:
        send_message(chat_id, "لطفاً یک لینک معتبر یوتیوب ارسال کنید.")


def main():
    last_offset = load_offset()
    updates = get_updates(last_offset + 1)

    for update in updates:
        process_message(update)
        last_offset = update["update_id"]

    save_offset(last_offset)


# ----------------------------------------------------------------------
# رابط خط فرمان
# ----------------------------------------------------------------------
# def main():
#     parser = argparse.ArgumentParser(
#         description="دانلود ویدیو از یوتیوب با روش‌های متعدد (مشابه workflow گیت‌هاب)."
#     )
#     parser.add_argument("--url", required=True, help="آدرس ویدیوی یوتیوب")
#     parser.add_argument(
#         "--quality", default="480",
#         choices=["audio", "best", "2160", "1440", "1080", "720", "480", "360"],
#         help="کیفیت دانلود (پیش‌فرض: 480)"
#     )
#     parser.add_argument(
#         "--proxy", default="socks5://127.0.0.1:1080",
#         help="پروکسی SOCKS5 (پیش‌فرض: socks5://127.0.0.1:1080)"
#     )
#     parser.add_argument("--password", help="رمز فایل زیپ (اختیاری)")
#     parser.add_argument(
#         "--output", default="video.zip",
#         help="مسیر فایل زیپ خروجی (پیش‌فرض: video.zip)"
#     )
#     args = parser.parse_args()

#     # بررسی وجود yt-dlp
#     if shutil.which("yt-dlp") is None:
#         print("[✗] yt-dlp پیدا نشد. لطفاً آن را نصب کنید: pip install yt-dlp")
#         sys.exit(1)

#     download_youtube_video(
#         url=args.url,
#         quality=args.quality,
#         proxy=args.proxy,
#         zip_password=args.password,
#         output_zip=args.output
#     )


if __name__ == "__main__":
    main()
