import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import yt_dlp
import os

# Carpeta por defecto
DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")

# Función principal de descarga
def download_video(url, format_choice, button):
    try:
        button.config(state="disabled")
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

        options = {
            'format': 'bestaudio/best' if format_choice == "mp3" else 'bestvideo+bestaudio/best',
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'ffmpeg_location': r'D:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin',
        }

        if format_choice == "mp3":
            options['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        messagebox.showinfo("Éxito", f"Descarga completada como {format_choice.upper()}")
        os.startfile(DOWNLOAD_FOLDER)

    except Exception as e:
        messagebox.showerror("Error", f"Hubo un problema:\n{str(e).encode('ascii', 'ignore').decode()}")
    finally:
        button.config(state="normal")

# Maneja clic en botón
def on_download_click(entry, format_var, button):
    url = entry.get().strip()
    format_choice = format_var.get()
    if not url:
        messagebox.showerror("Error", "Por favor, pega un enlace de YouTube.")
        return
    threading.Thread(target=download_video, args=(url, format_choice, button)).start()

# Selector de carpeta
def choose_folder(label):
    global DOWNLOAD_FOLDER
    folder = filedialog.askdirectory()
    if folder:
        DOWNLOAD_FOLDER = folder
        label.config(text=f"Carpeta: {folder}")

# Construye GUI
def create_gui():
    window = tk.Tk()
    window.title("YouTube Downloader")
    window.geometry("500x260")
    window.resizable(False, False)

    # Instrucciones
    tk.Label(window, text="Pega el enlace de YouTube:").pack(pady=(10, 0))
    url_entry = tk.Entry(window, width=60)
    url_entry.pack(pady=(5, 10))

    # Selector de formato
    format_var = tk.StringVar(value="mp3")
    format_frame = tk.Frame(window)
    tk.Label(format_frame, text="Formato:").pack(side="left")
    tk.Radiobutton(format_frame, text="MP3", variable=format_var, value="mp3").pack(side="left")
    tk.Radiobutton(format_frame, text="MP4", variable=format_var, value="mp4").pack(side="left")
    format_frame.pack()

    # Carpeta destino
    folder_label = tk.Label(window, text=f"Carpeta: {DOWNLOAD_FOLDER}")
    folder_label.pack(pady=(10, 0))
    tk.Button(window, text="Cambiar carpeta", command=lambda: choose_folder(folder_label)).pack(pady=(0, 10))

    # Botón descargar
    download_button = tk.Button(window, text="Descargar", command=lambda: on_download_click(url_entry, format_var, download_button))
    download_button.pack()

    window.mainloop()

if __name__ == "__main__":
    create_gui()
