import tkinter as tk
from tkinter import simpledialog, messagebox
from pytube import YouTube
from tqdm import tqdm
import os
import sys

# ─────────────────────────────────────────────
# Function to show a progress bar in terminal
# pytube calls this function with stream info
# ─────────────────────────────────────────────
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining

    percentage_of_completion = bytes_downloaded / total_size * 100
    pbar.n = bytes_downloaded
    pbar.refresh()

# ─────────────────────────────────────────────
# Setup basic popup interface
# ─────────────────────────────────────────────
root = tk.Tk()
root.withdraw()

url = simpledialog.askstring("YouTube Downloader", "Paste the YouTube video link:")
if not url:
    messagebox.showinfo("Cancelled", "No URL provided. Exiting.")
    sys.exit()

format_choice = simpledialog.askstring("Format", "Download as MP3 or MP4? (type mp3 or mp4)")
if not format_choice or format_choice.lower() not in ["mp3", "mp4"]:
    messagebox.showerror("Invalid Input", "You must type 'mp3' or 'mp4'.")
    sys.exit()

format_choice = format_choice.lower()

try:
    # ─────────────────────────────────────────────
    # Attach progress callback to YouTube object
    # ─────────────────────────────────────────────
    yt = YouTube(url, on_progress_callback=on_progress)
    title = yt.title

    # Choose stream based on format
    stream = yt.streams.get_audio_only() if format_choice == "mp3" else yt.streams.get_highest_resolution()

    # ─────────────────────────────────────────────
    # Set up tqdm progress bar
    # ─────────────────────────────────────────────
    print(f"\nDownloading: {title}")
    pbar = tqdm(total=stream.filesize, unit='B', unit_scale=True, desc='Progress', ncols=70)

    # Download file
    download_path = stream.download()
    pbar.close()

    if format_choice == "mp3":
        from moviepy.editor import AudioFileClip
        mp3_path = os.path.splitext(download_path)[0] + ".mp3"
        print("Converting to MP3...")
        audio_clip = AudioFileClip(download_path)
        audio_clip.write_audiofile(mp3_path)
        audio_clip.close()
        os.remove(download_path)
        messagebox.showinfo("Success", f"MP3 downloaded: {mp3_path}")
    else:
        messagebox.showinfo("Success", f"MP4 downloaded: {download_path}")

except Exception as e:
    messagebox.showerror("Error", str(e))
