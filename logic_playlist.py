import os
from datetime import datetime
from tkinter import messagebox
import yt_dlp

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "downloads")

def download_playlist_items(url, format_choice, button, label_status):
    try:
        button.config(state="disabled")
        os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

        base_options = {
            'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
            'ffmpeg_location': r'D:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin',
            'quiet': False,
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
            return

        total = len(entries)

        for i, entry in enumerate(entries, 1):
            title = entry['title']
            video_url = entry['url']
            label_status.config(text=f"Descargando {i}/{total}: {title[:50]}...")
            label_status.update()
            try:
                with yt_dlp.YoutubeDL(base_options) as ydl:
                    ydl.download([video_url])
            except Exception as e:
                skipped += 1
                print(f"[ERROR] {title}: {e}")
                with open("log_failed.txt", "a", encoding="utf-8") as failed_log:
                    failed_log.write(f"{title} - {e}\n")
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
