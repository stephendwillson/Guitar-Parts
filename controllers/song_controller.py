"""
Module for the SongController class that manages song-related operations
like adding, updating, and deleting songs. It also handles album art
caching and interactions with the Last.FM API.
"""

import os
import logging
import random

from services.db import (
    initialize_db,
    save_song,
    load_songs,
    delete_song,
    update_song_info,
    song_exists,
    get_song,
    get_unique_genres,
    get_unique_tunings,
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
        logging.debug(f"Getting song: {title} by {artist}")
        song = get_song(self.cursor, title, artist)
        if song:
            logging.info(f"Found song: {title} by {artist}")
        else:
            logging.info(f"Song not found: {title} by {artist}")
        return song

    def get_all_songs(self):
        """
        Retrieve all songs from the database.

        Returns:
            list: A list of dictionaries, each containing song details.
        """
        logging.debug("Getting all songs from the database")
        songs = load_songs(self.cursor)
        logging.info(f"Retrieved {len(songs)} songs from the database")
        return songs

    def save_song(self, song, is_custom=False):
        """
        Save a new song to the database.

        Args:
            song (Song): A Song object containing song details.
            is_custom (bool): Whether the song is a custom entry.

        Returns:
            tuple: (bool, str) A tuple containing a success flag and a message.
        """
        try:
            if not self.song_exists(song.title, song.artist):
                if not is_custom:
                    logging.debug(
                        "Song does not exist, fetching track info: %s by %s",
                        song.title,
                        song.artist,
                    )
                    track_info = self.get_track_info(song.artist, song.title)
                    if track_info and "error" not in track_info:
                        # Update song with additional info from Last.fm
                        track = track_info.get("track", {})
                        song.album = track.get("album", {}).get("title", "Unknown")
                        song.duration = track.get("duration", 0)
                        song.genres = [
                            tag["name"]
                            for tag in track.get("toptags", {}).get("tag", [])
                        ]

                        # Fetch and cache album art
                        album_images = track.get("album", {}).get("image", [])
                        if album_images:
                            album_art_url = album_images[-1].get("#text")
                            if album_art_url:
                                self.fetch_and_cache_album_art(
                                    album_art_url, song.album
                                )
                    else:
                        return False, (
                            "Song not found on Last.FM. Check your spelling, "
                            "or did you mean to add as a custom song?"
                        )

            save_song(self.cursor, song)
            self.conn.commit()
            logging.info(f"Song saved successfully: {song.title} by {song.artist}")
            return True, "Song saved successfully"
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error saving song {song.title} by {song.artist}: {str(e)}")
            return False, "Unable to save the song. Please try again."

    def delete_song(self, title, artist):
        """
        Delete a song from the database.

        Args:
            title (str): The title of the song.
            artist (str): The artist of the song.
        """
        logging.info(f"Attempting to delete song: {title} by {artist}")
        try:
            delete_song(self.cursor, title, artist)
            self.conn.commit()
            logging.info(f"Successfully deleted song: {title} by {artist}")
            return True, "Song deleted successfully"
        except Exception as e:
            self.conn.rollback()
            logging.error(f"Error deleting song {title} by {artist}: {str(e)}")
            return False, "Unable to delete the song. Please try again."

    def update_song_info(self, song):
        """
        Update the information for an existing song in the database.

        Args:
            song (dict): A dictionary containing updated song details.
        """
        logging.info(f"Updating song info for: {song.title} by {song.artist}")
        try:
            update_song_info(self.cursor, song)
            logging.info(
                f"Successfully updated song info for: {song.title} by {song.artist}"
            )
            return True, "Song updated successfully"
        except Exception as e:
            logging.error(
                f"Error updating song info for {song.title} by {song.artist}: {str(e)}"
            )
            return False, "Unable to update the song. Please try again."

    def get_track_info(self, artist, track):
        """
        Retrieve track information from the Last.FM API.

        Args:
            artist (str): The artist of the track.
            track (str): The name of the track.

        Returns:
            dict: A dictionary containing track information.
        """
        logging.debug(f"Getting track info for {track} by {artist}")
        track_info = get_track_info(artist, track)
        if track_info:
            logging.info(f"Retrieved track info for {track} by {artist}")
        else:
            logging.warning(f"Failed to retrieve track info for {track} by {artist}")
        return track_info

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
        if os.path.exists(album_art_path):
            logging.info(f"Found cached album art for {album_name}")
        else:
            logging.info(f"No cached album art found for {album_name}")
        return album_art_path if os.path.exists(album_art_path) else None

    def get_unique_genres(self):
        """
        Get all unique genres from the database.
        """
        return get_unique_genres(self.cursor)

    def get_unique_tunings(self):
        """
        Get all unique tunings from the database.
        """
        return get_unique_tunings(self.cursor)

    def search_songs(self, search_text):
        """
        Search for songs by title or artist.

        Args:
            search_text (str): The text to search for in titles and artists.

        Returns:
            list: A list of Song objects matching the search criteria.
        """
        search_text = search_text.lower()
        return [song for song in self.get_all_songs() if
                search_text in song.title.lower() or
                search_text in song.artist.lower()]

    def filter_songs(self, artist='', title='', album='', genre='', tunings=None,
                     num_songs=0):
        """Filter songs based on given criteria"""
        songs = self.get_all_songs()
        filtered_songs = []

        for song in songs:
            if (
                (not artist or artist.lower() in song.artist.lower()) and
                (not title or title.lower() in song.title.lower()) and
                (not album or album.lower() in song.album.lower()) and
                (not genre or genre in song.genres) and
                (not tunings or song.tuning in tunings)
            ):
                filtered_songs.append(song)

        if num_songs > 0:
            filtered_songs = random.sample(
                filtered_songs,
                min(num_songs, len(filtered_songs))
            )

        return filtered_songs
