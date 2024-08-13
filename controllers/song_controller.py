"""
Module for the SongController class that manages song-related operations
like adding, updating, and deleting songs. It also handles album art
caching and interactions with the Last.FM API.
"""

import os
import logging

from services.db import (
    initialize_db,
    save_song,
    load_songs,
    delete_song,
    update_song_info,
    song_exists,
    get_song,
)
from services.lastfm_api import get_track_info, fetch_and_cache_album_art
from utils.utils import get_default_db_path, get_resource_path, create_cache_directory


class SongController:
    def __init__(self):
        """
        Initialize the SongController with the given database path.

        Args:
            db_path (str): The path to the database.
        """
        self.conn, self.cursor = initialize_db()
        self.cache_dir = create_cache_directory()

    def song_exists(self, title, artist):
        """
        Check if a song exists in the database.

        Args:
            title (str): The title of the song.
            artist (str): The artist of the song.

        Returns:
            bool: True if the song exists, False otherwise.
        """
        return song_exists(self.cursor, title, artist)

    def get_song(self, title, artist):
        """
        Retrieve a song from the database.

        Args:
            title (str): The title of the song.
            artist (str): The artist of the song.

        Returns:
            dict: A dictionary containing song details.
        """
        return get_song(self.cursor, title, artist)

    def get_all_songs(self):
        """
        Retrieve all songs from the database.

        Returns:
            list: A list of dictionaries, each containing song details.
        """
        return load_songs(self.cursor)

    def save_song(self, song):
        """
        Save a new song to the database.

        Args:
            song (dict): A dictionary containing song details.
        """
        save_song(self.cursor, song)

    def delete_song(self, title, artist):
        """
        Delete a song from the database.

        Args:
            title (str): The title of the song.
            artist (str): The artist of the song.
        """
        delete_song(self.cursor, title, artist)

    def update_song_info(self, song):
        """
        Update the information for an existing song in the database.

        Args:
            song (dict): A dictionary containing updated song details.
        """
        update_song_info(self.cursor, song)

    def get_track_info(self, artist, track):
        """
        Retrieve track information from the Last.FM API.

        Args:
            artist (str): The artist of the track.
            track (str): The name of the track.

        Returns:
            dict: A dictionary containing track information.
        """
        return get_track_info(artist, track)

    def get_default_db_path(self):
        """
        Get the default database path.

        Returns:
            str: The default database path.
        """
        return get_default_db_path()

    def get_resource_path(self, relative_path):
        """
        Get the absolute path to a resource file.

        Args:
            relative_path (str): The relative path to the resource file.

        Returns:
            str: The absolute path to the resource file.
        """
        return get_resource_path(relative_path)

    def create_cache_directory(self):
        """
        Create a directory for caching album art.
        """
        db_path = get_default_db_path()
        cache_dir = os.path.join(os.path.dirname(db_path), "album_art_cache")
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_dir = cache_dir

    def get_cache_dir(self):
        """
        Get the directory where album art is cached.

        Returns:
            str: The path to the cache directory.
        """
        return self.cache_dir

    def fetch_and_cache_album_art(self, album_art_url, album_name):
        """
        Fetch and cache album art from the given URL.

        Args:
            album_art_url (str): The URL for the album art.
            album_name (str): The name of the album.
        """
        fetch_and_cache_album_art(album_art_url, album_name, self.cache_dir)

    def get_cached_album_art(self, album_name):
        """
        Get the cached album art for the given album.

        Args:
            album_name (str): The name of the album.

        Returns:
            str or None: The path to the cached album art if it exists, otherwise None.
        """
        if not album_name:
            logging.info("No album name provided, skipping album art fetch.")
            return None

        album_art_path = os.path.join(self.cache_dir, f"{album_name}.jpg")
        return album_art_path if os.path.exists(album_art_path) else None
