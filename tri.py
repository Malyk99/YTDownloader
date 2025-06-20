from pytube import YouTube

try:
    yt = YouTube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print("Title:", yt.title)
    print("Length:", yt.length, "seconds")
    print("Streams found:", yt.streams.count())
except Exception as e:
    print("Error:", e)