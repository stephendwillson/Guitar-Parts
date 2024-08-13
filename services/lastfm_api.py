"""
Wrapper for the Last.fm API.
"""

from datetime import timedelta
import requests
import os
import logging
from dotenv import load_dotenv
from utils.utils import setup_logging

load_dotenv()

API_ROOT = "http://ws.audioscrobbler.com/2.0/"
API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

if not API_KEY or not API_SECRET:
    raise ValueError("API_KEY and API_SECRET must be set as environment variables.")

setup_logging()


def get_track_info(artist, track):
    """
    Get info about a track from Last.fm API.

    Args:
        artist (str): The artist name.
        track (str): The track name.

    Returns:
        dict: Dictionary containing track info.
    """
    method = "track.getInfo"
    artist = artist.replace(" ", "+")
    track = track.replace(" ", "+")
    api_key_str = "&api_key=" + API_KEY
    method_call = f"{API_ROOT}?method={method}"
    track_info_query = f"&artist={artist}&track={track}"
    call = f"{method_call}{track_info_query}{api_key_str}&format=json"

    try:
        response = requests.get(call, timeout=5)
        response.raise_for_status()
        track_info = response.json()

        # Extract album art URL
        images = track_info.get("track", {}).get("album", {}).get("image", [])
        album_art_url = images[-1]["#text"] if images else None  # Get the largest image
        track_info["album_art_url"] = album_art_url
        return track_info
    except requests.exceptions.RequestException as e:
        print(f"Error fetching track info: {e}")
        return {}


def get_album_name(artist, track):
    """
    Get the album name for a given track.

    Args:
        artist (str): The artist name.
        track (str): The track name.

    Returns:
        str: The album name.
    """
    track_info = get_track_info(artist, track)
    return track_info.get("track", {}).get("album", {}).get("title", "N/A")


def get_track_duration(artist, track):
    """
    Get the duration of a given track.

    Args:
        artist (str): The artist name.
        track (str): The track name.

    Returns:
        timedelta: The duration of the track.
    """
    track_info = get_track_info(artist, track)
    return timedelta(milliseconds=int(track_info.get("track", {}).get("duration", 0)))


def get_genre(artist, track):
    """
    Get the genre(s) of a given track.

    Args:
        artist (str): The artist name.
        track (str): The track name.

    Returns:
        list: A list of genres.
    """
    track_info = get_track_info(artist, track)
    genres = [
        tag["name"]
        for tag in track_info.get("track", {}).get("toptags", {}).get("tag", [])
    ]
    return genres


def fetch_and_cache_album_art(album_art_url, album_name, cache_dir):
    try:
        logging.debug("Fetching album art from %s", album_art_url)
        response = requests.get(album_art_url, timeout=5)
        response.raise_for_status()
        album_art_path = os.path.join(cache_dir, f"{album_name}.jpg")
        with open(album_art_path, "wb") as f:
            f.write(response.content)
        return album_art_path
    except requests.exceptions.RequestException as e:
        logging.warning("Error fetching album art: %s", e)
        return None
