import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import threading
import yt_dlp
import os

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")

def download_playlist_items(url, format_choice, button, label_status, progress_bar):
    try:
        button.config(state="disabled")
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

        base_options = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'ffmpeg_location': r'D:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin',
            'quiet': True,  # evita prints de consola
            'noplaylist': False,
        }

        # Formato
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

        # Extraemos lista sin descargar aún
        with yt_dlp.YoutubeDL(base_options) as ydl:
            info = ydl.extract_info(url, download=False)

        if 'entries' in info:
            entries = info['entries']
        else:
            entries = [info]

        total = len(entries)
        progress_bar.config(maximum=total)
        progress_bar['value'] = 0

        for i, entry in enumerate(entries, 1):
            title = entry.get('title', 'Desconocido')
            label_status.config(text=f"Descargando {i}/{total}: {title[:50]}...")
            with yt_dlp.YoutubeDL(base_options) as ydl:
                ydl.download([entry['webpage_url']])
            progress_bar['value'] = i

        messagebox.showinfo("Éxito", "Todas las descargas han finalizado.")
        os.startfile(DOWNLOAD_FOLDER)

    except Exception as e:
        messagebox.showerror("Error", f"Hubo un problema:\n{str(e).encode('ascii', 'ignore').decode()}")
    finally:
        button.config(state="normal")
        label_status.config(text="")
        progress_bar['value'] = 0

def on_download_click(entry, format_var, button, label_status, progress_bar):
    url = entry.get().strip()
    format_choice = format_var.get()
    if not url:
        messagebox.showerror("Error", "Por favor, pega un enlace de YouTube.")
        return
    threading.Thread(target=download_playlist_items, args=(url, format_choice, button, label_status, progress_bar)).start()

def choose_folder(label):
    global DOWNLOAD_FOLDER
    folder = filedialog.askdirectory()
    if folder:
        DOWNLOAD_FOLDER = folder
        label.config(text=f"Carpeta: {folder}")

def create_gui():
    window = tk.Tk()
    window.title("YT Downloader")
    window.geometry("550x310")
    window.resizable(False, False)

    # Entrada de enlace
    tk.Label(window, text="Pega el enlace de YouTube o de una playlist:").pack(pady=(10, 0))
    url_entry = tk.Entry(window, width=70)
    url_entry.pack(pady=(5, 10))

    # Selector de formato
    format_var = tk.StringVar(value="mp3")
    format_frame = tk.Frame(window)
    tk.Label(format_frame, text="Formato:").pack(side="left")
    tk.Radiobutton(format_frame, text="MP3", variable=format_var, value="mp3").pack(side="left")
    tk.Radiobutton(format_frame, text="MP4", variable=format_var, value="mp4").pack(side="left")
    format_frame.pack()

    # Carpeta
    folder_label = tk.Label(window, text=f"Carpeta: {DOWNLOAD_FOLDER}")
    folder_label.pack(pady=(10, 0))
    tk.Button(window, text="Cambiar carpeta", command=lambda: choose_folder(folder_label)).pack()

    # Estado y barra
    label_status = tk.Label(window, text="", wraplength=500, justify="center")
    label_status.pack(pady=(15, 5))

    progress_bar = ttk.Progressbar(window, orient="horizontal", mode="determinate", length=450)
    progress_bar.pack(pady=(0, 10))

    # Botón
    download_button = tk.Button(window, text="Iniciar descarga", command=lambda: on_download_click(url_entry, format_var, download_button, label_status, progress_bar))
    download_button.pack(pady=(10, 10))

    window.mainloop()

if __name__ == "__main__":
    create_gui()
