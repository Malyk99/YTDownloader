import yt_dlp

url = "https://www.youtube.com/watch?v=uBOnYAK3WZ4"

options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

with yt_dlp.YoutubeDL(options) as ydl:
    ydl.download([url])
