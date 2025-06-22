import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import yt_dlp
import os
from datetime import datetime

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")

def download_playlist_items(url, format_choice, button, label_status):
    try:
        button.config(state="disabled")
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

        base_options = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'ffmpeg_location': r'D:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin',
            'quiet': False,  # Set to True if you want to hide debug output
            'noplaylist': False,
        }

        if format_choice == "mp3":
            base_options['format'] = 'bestaudio/best'
            base_options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        else:
            base_options['format'] = 'bestvideo+bestaudio/best'
            base_options['merge_output_format'] = 'mp4'

        with yt_dlp.YoutubeDL(base_options) as ydl:
            info = ydl.extract_info(url, download=False)

        entries_raw = info.get('entries', [info])
        entries = []
        skipped = 0

        for entry in entries_raw:
            if not entry or not isinstance(entry, dict):
                skipped += 1
                continue
            entry_url = entry.get("webpage_url") or entry.get("url")
            title = entry.get("title")
            if entry_url and title:
                entries.append({"url": entry_url, "title": title})
            else:
                skipped += 1

        if not entries:
            label_status.config(text="")
            messagebox.showwarning(
                "Sin vídeos válidos",
                f"No se pudo descargar ningún vídeo.\nVideos omitidos o no disponibles: {skipped}"
            )
            return  # Only exit here if nothing to download

        total = len(entries)

        for i, entry in enumerate(entries, 1):
            title = entry['title']
            video_url = entry['url']
            label_status.config(text=f"Descargando {i}/{total}: {title[:50]}...")
            label_status.update()  # Force UI to refresh
            try:
                with yt_dlp.YoutubeDL(base_options) as ydl:
                    ydl.download([video_url])
            except Exception as e:
                skipped += 1
                print(f"[ERROR] {title}: {e}")
                continue
            with open("log_descargas.txt", "a", encoding="utf-8") as log_file:
                fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_file.write(f"[{fecha}] {title} - {format_choice.upper()}\n")

        msg = f"Descargas finalizadas: {total}"
        if skipped:
            msg += f"\nSaltados: {skipped} no disponibles o con errores."
        messagebox.showinfo("Proceso completado", msg)
        os.startfile(DOWNLOAD_FOLDER)

    except Exception as e:
        messagebox.showerror("Error", f"Hubo un problema:\n{str(e).encode('ascii', 'ignore').decode()}")
    finally:
        button.config(state="normal")
        label_status.config(text="")


def on_download_click(entry, format_var, button, label_status):
    url = entry.get().strip()
    format_choice = format_var.get()

    if "list=RD" in url or "start_radio=1" in url or "&rv=" in url:
        messagebox.showerror("URL inválida", "YouTube radio mixes no son compatibles.\nPor favor pega una playlist real.")
        return

    if not url:
        messagebox.showerror("Error", "Por favor, pega un enlace de YouTube.")
        return

    threading.Thread(target=download_playlist_items, args=(url, format_choice, button, label_status)).start()

def choose_folder(label):
    global DOWNLOAD_FOLDER
    folder = filedialog.askdirectory()
    if folder:
        DOWNLOAD_FOLDER = folder
        label.config(text=f"Carpeta: {folder}")

def create_gui():
    window = tk.Tk()
    window.title("YT Downloader")
    window.geometry("550x270")
    window.resizable(False, False)

    tk.Label(window, text="Pega el enlace de YouTube o de una playlist:").pack(pady=(10, 0))
    url_entry = tk.Entry(window, width=70)
    url_entry.pack(pady=(5, 10))

    format_var = tk.StringVar(value="mp3")
    format_frame = tk.Frame(window)
    tk.Label(format_frame, text="Formato:").pack(side="left")
    tk.Radiobutton(format_frame, text="MP3", variable=format_var, value="mp3").pack(side="left")
    tk.Radiobutton(format_frame, text="MP4", variable=format_var, value="mp4").pack(side="left")
    format_frame.pack()

    folder_label = tk.Label(window, text=f"Carpeta: {DOWNLOAD_FOLDER}")
    folder_label.pack(pady=(10, 0))
    tk.Button(window, text="Cambiar carpeta", command=lambda: choose_folder(folder_label)).pack()

    label_status = tk.Label(window, text="", wraplength=500, justify="center")
    label_status.pack(pady=(15, 10))

    download_button = tk.Button(window, text="Iniciar descarga", command=lambda: on_download_click(url_entry, format_var, download_button, label_status))
    download_button.pack(pady=(10, 10))

    window.mainloop()

if __name__ == "__main__":
    create_gui()
