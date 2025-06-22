from yt_dlp import YoutubeDL
import os

def download_youtube_single(url, download_dir, format_choice="mp3"):
    if not url.startswith("http"):
        raise ValueError("Invalid YouTube URL.")

    os.makedirs(download_dir, exist_ok=True)

    ydl_opts = {
        'outtmpl': os.path.join(download_dir, '%(title)s.%(ext)s'),
        'quiet': True,
    }

    if format_choice == "mp3":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })
    elif format_choice == "mp4":
        ydl_opts.update({'format': 'bestvideo+bestaudio/best'})

    with YoutubeDL(ydl_opts) as ydl:
        try:
            print(f" Downloading {url} as {format_choice.upper()}")
            ydl.download([url])
            with open("log_downloads.txt", "a", encoding="utf-8") as log:
                log.write(f"{url} [{format_choice}]\n")
        except Exception as e:
            with open("log_failed.txt", "a", encoding="utf-8") as log:
                log.write(f"{url} - {str(e)}\n")
            raise
