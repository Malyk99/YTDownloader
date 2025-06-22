import re
import os
from datetime import datetime
from tkinter import messagebox
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

from logic_list import download_from_txt

CLIENT_ID = "20671393f87d44909efee094f5ea4ce1"
CLIENT_SECRET = "ba791bee9fa645e3bac06ab221828ff7"
REDIRECT_URI = "http://127.0.0.1:8888/callback"
SCOPE = "playlist-read-private playlist-read-collaborative"
OUTPUT_FILE = "spotify_tracks.txt"


def extract_playlist_id(url):
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    if match:
        return match.group(1)
    raise ValueError("No valid playlist ID found in the URL.")


def get_playlist_tracks(playlist_id, sp):
    tracks = []
    results = sp.playlist_items(playlist_id, additional_types=["track"])
    while results:
        for item in results["items"]:
            track = item.get("track")
            if not track:
                continue
            name = track.get("name")
            artists = ", ".join([artist["name"] for artist in track.get("artists", [])])
            if name and artists:
                tracks.append(f"{artists} - {name}")
        if results["next"]:
            results = sp.next(results)
        else:
            break
    return tracks


def save_tracks_to_file(tracks, filename):
    with open(filename, "w", encoding="utf-8") as f:
        for track in tracks:
            f.write(track + "\n")


def process_spotify_playlist(link, format_choice, button, label_status):
    try:
        button.config(state="disabled")
        label_status.config(text="Convirtiendo Spotify playlist a texto...")
        label_status.update()

        playlist_id = extract_playlist_id(link)
        sp = Spotify(auth_manager=SpotifyOAuth(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            redirect_uri=REDIRECT_URI,
            scope=SCOPE
        ))

        tracks = get_playlist_tracks(playlist_id, sp)
        if not tracks:
            messagebox.showwarning("Lista vacía", "No se encontraron canciones en la playlist.")
            return

        save_tracks_to_file(tracks, OUTPUT_FILE)
        os.startfile(OUTPUT_FILE)

        # Confirmar descarga
        proceed = messagebox.askyesno("Descargar canciones", "¡Se ha generado la lista! ¿Quieres comenzar la descarga?")
        if proceed:
            download_from_list(OUTPUT_FILE, format_choice, button, label_status)
        else:
            label_status.config(text="Descarga cancelada por el usuario.")

    except Exception as e:
        messagebox.showerror("Error", f"Hubo un problema:{str(e).encode('ascii', 'ignore').decode()}")
    finally:
        button.config(state="normal")

def process_spotify_playlist_simple(link, output_path="spotify_tracks.txt"):
    playlist_id = extract_playlist_id(link)
    sp = Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE
    ))
    tracks = get_playlist_tracks(playlist_id, sp)
    if not tracks:
        raise Exception("No tracks found in the playlist.")
    save_tracks_to_file(tracks, output_path)
    return output_path

        