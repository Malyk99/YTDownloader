import os
from yt_dlp import YoutubeDL

def download_from_txt(txt_path, download_dir):
    if not os.path.exists(txt_path):
        print(" .txt file not found.")
        return

    with open(txt_path, 'r', encoding='utf-8') as f:
        songs = [line.strip() for line in f if line.strip()]

    # Create a subfolder for this batch
    batch_folder = os.path.join(download_dir, "batch_downloads")
    os.makedirs(batch_folder, exist_ok=True)

    success_log = open("log_downloads.txt", "a", encoding="utf-8")
    fail_log = open("log_failed.txt", "a", encoding="utf-8")

    for index, song in enumerate(songs, start=1):
        print(f"🔎 [{index}/{len(songs)}] Searching: {song}")
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': os.path.join(batch_folder, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': True,
                'noplaylist': True
            }

            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([f"ytsearch1:{song}"])

            success_log.write(f"{song}\n")
            print(f"Downloaded: {song}")

        except Exception as e:
            fail_log.write(f"{song} - {str(e)}\n")
            print(f"Failed: {song}")

    success_log.close()
    fail_log.close()
