import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import threading

CONFIG_FILE = "config.json"

def load_last_directory():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get("last_directory", os.getcwd())
    return os.getcwd()

def save_last_directory(path):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"last_directory": path}, f)

class DownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube/Spotify Downloader")
        self.root.geometry("600x400")
        self.last_directory = load_last_directory()

        self.input_type = tk.StringVar(value="youtube")
        self.input_path = tk.StringVar()
        self.status_text = tk.StringVar(value="Waiting for input...")
        self.format_choice = tk.StringVar(value="mp3")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Enter a link or select a .txt file:").pack(pady=10)
        input_frame = tk.Frame(self.root)
        input_frame.pack()

        self.entry = tk.Entry(input_frame, textvariable=self.input_path, width=50)
        self.entry.pack(side=tk.LEFT, padx=(0, 5))

        tk.Button(input_frame, text="Browse File", command=self.browse_txt).pack(side=tk.LEFT)

        tk.Label(self.root, text="Select input type:").pack(pady=(10, 0))
        self.type_dropdown = ttk.Combobox(
            self.root,
            textvariable=self.input_type,
            values=["txt", "youtube", "youtube_playlist", "spotify_playlist"],
            state="readonly"
        )
        self.type_dropdown.pack()

        # Format option (only shown if input is YouTube link)
        self.format_frame = tk.Frame(self.root)
        self.format_label = tk.Label(self.format_frame, text="Format:")
        self.format_dropdown = ttk.Combobox(
            self.format_frame,
            textvariable=self.format_choice,
            values=["mp3", "mp4"],
            state="readonly",
            width=5
        )
        self.format_label.pack(side=tk.LEFT)
        self.format_dropdown.pack(side=tk.LEFT)
        self.format_frame.pack(pady=(5, 0))

        tk.Label(self.root, text="Select download folder:").pack(pady=(20, 0))
        self.folder_label = tk.Label(self.root, text=self.last_directory)
        self.folder_label.pack()
        tk.Button(self.root, text="Change Folder", command=self.select_folder).pack()

        tk.Button(self.root, text="Start Download", command=self.start_download).pack(pady=15)
        self.status_box = tk.Label(self.root, textvariable=self.status_text, fg="blue")
        self.status_box.pack(pady=(10, 0))

        self.type_dropdown.bind("<<ComboboxSelected>>", self.on_input_type_change)
        self.on_input_type_change()

    def browse_txt(self):
        file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if file:
            self.input_path.set(file)
            self.input_type.set("txt")

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.last_directory = folder
            self.folder_label.config(text=folder)
            save_last_directory(folder)

    def on_input_type_change(self, event=None):
        if self.input_type.get() == "youtube":
            self.format_frame.pack(pady=(5, 0))
        else:
            self.format_frame.pack_forget()

    def start_download(self):
        input_path = self.input_path.get().strip()
        input_type = self.input_type.get()
        output_dir = self.last_directory
        format_choice = self.format_choice.get()

        if not input_path:
            messagebox.showerror("Error", "Please provide a valid input.")
            return

        self.status_text.set("Preparing...")
        self.root.update_idletasks()

        # Desactiva el botón para evitar doble clic
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button) and widget["text"] == "Start Download":
                widget.config(state="disabled")

        def threaded_task():
            try:
                if input_type == "txt":
                    from logic_list import download_from_txt
                    self.status_text.set("Downloading from list...")
                    download_from_txt(input_path, output_dir)

                elif input_type == "youtube":
                    from logic_youtube import download_youtube_single
                    self.status_text.set(f"Downloading as {format_choice}...")
                    download_youtube_single(input_path, output_dir, format_choice)

                elif input_type == "youtube_playlist":
                    from logic_playlist import download_playlist_items
                    self.status_text.set("Downloading YouTube playlist...")
                    download_playlist_items(input_path, output_dir, format_choice)

                elif input_type == "spotify_playlist":
                    from logic_spotify import process_spotify_playlist_simple
                    self.status_text.set("Fetching songs from Spotify...")
                    txt_path = process_spotify_playlist_simple(input_path)
                    self.status_text.set("Downloading from generated list...")
                    from logic_list import download_from_txt
                    download_from_txt(txt_path, output_dir)

                self.status_text.set("Download complete.")

            except Exception as e:
                self.status_text.set("An error occurred. Check log_failed.txt.")
                with open("log_failed.txt", "a", encoding="utf-8") as f:
                    f.write(f"{input_path} - {str(e)}\n")
                print(f"Error: {e}")

            finally:
                # Reactiva el botón tras la descarga
                for widget in self.root.winfo_children():
                    if isinstance(widget, tk.Button) and widget["text"] == "Start Download":
                        widget.config(state="normal")

        threading.Thread(target=threaded_task).start()



def run_gui():
    root = tk.Tk()
    app = DownloaderGUI(root)
    root.mainloop()
