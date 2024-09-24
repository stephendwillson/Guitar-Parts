"""
Module for database stuffs.
"""

import sqlite3
import logging
from models.song import Song
from utils.utils import get_default_db_path, get_resource_path, setup_logging

setup_logging()


def initialize_db(db_file=None, schema_file="db/schema.sql"):
    """
    Init database.

    Args:
        db_file (str): Path to the database file.
        schema_file (str): Path to the schema file.

    Returns:
        tuple: Tuple containing the database connection and cursor.
    """
    if db_file is None:
        db_file = get_default_db_path()

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    schema_path = get_resource_path(schema_file)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = f.read()

    cursor.executescript(schema)
    conn.commit()
    return conn, cursor


def get_song(cursor, title, artist):
    """
    Get a song from the database.

    Args:
        cursor (sqlite3.Cursor): The database cursor.
        title (str): The title of the song.
        artist (str): The artist of the song.

    Returns:
        Song: The song object if found, None otherwise.
    """
    logging.debug("Fetching song: %s by %s", title, artist)
    cursor.execute(
        "SELECT title, artist, tuning, notes, album, duration, genres FROM songs "
        "WHERE LOWER(title) = LOWER(?) AND LOWER(artist) = LOWER(?)",
        (title.lower(), artist.lower()),
    )
    row = cursor.fetchone()
    if row:
        logging.debug("Song found: %s by %s", row[0], row[1])
        return Song(
            title=row[0],
            artist=row[1],
            tuning=row[2],
            notes=row[3],
            album=row[4],
            duration=row[5],
            genres=row[6].split(", "),  # Convert genres back to a list
        )
    logging.debug("Song not found: %s by %s", title, artist)
    return None


def save_song(cursor, song):
    """
    Save a song to the database.

    Args:
        cursor (sqlite3.Cursor): The database cursor.
        song (Song): The song object to save.
    """
    cursor.execute(
        "INSERT INTO songs (title, artist, tuning, notes, album, duration, genres) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (
            song.title.lower(),
            song.artist.lower(),
            song.tuning,
            song.notes,
            song.album,
            song.duration,
            ", ".join(song.genres),  # Convert genres to a comma-separated string
        ),
    )
    cursor.connection.commit()


def load_songs(cursor):
    """
    Load all songs from the database.

    Args:
        cursor (sqlite3.Cursor): The database cursor.

    Returns:
        list of Song: List of Song objects.
    """
    cursor.execute(
        "SELECT title, artist, tuning, notes, album, duration, genres FROM songs"
    )
    rows = cursor.fetchall()
    return [
        Song(
            title=row[0],
            artist=row[1],
            tuning=row[2],
            notes=row[3],
            album=row[4],
            duration=row[5],
            genres=row[6].split(", "),  # Convert genres back to a list
        )
        for row in rows
    ]


def delete_song(cursor, title, artist):
    """
    Delete a song from the database.

    Args:
        cursor (sqlite3.Cursor): The database cursor.
        title (str): The title of the song.
        artist (str): The artist for the song.
    """
    cursor.execute(
        "DELETE FROM songs WHERE LOWER(title) = LOWER(?) AND LOWER(artist) = LOWER(?)",
        (title, artist),
    )
    cursor.connection.commit()


def update_song_info(cursor, song):
    """
    Update the song information in the database.

    Args:
        cursor (sqlite3.Cursor): The database cursor.
        song (Song): The song object with updated information.
    """
    query = """
    UPDATE songs
    SET notes = ?, tuning = ?, album = ?, duration = ?, genres = ?
    WHERE LOWER(artist) = LOWER(?) AND LOWER(title) = LOWER(?)
    """
    cursor.execute(
        query,
        (
            song.notes,
            song.tuning,
            song.album,
            song.duration,
            ", ".join(song.genres),  # Convert genres to a comma-separated string
            song.artist.lower(),
            song.title.lower(),
        ),
    )
    cursor.connection.commit()


def song_exists(cursor, title, artist):
    """
    Check if a song exists in the database.

    Args:
        cursor (sqlite3.Cursor): The database cursor.
        title (str): The title of the song.
        artist (str): The artist for the song.

    Returns:
        bool: True if the song exists, False otherwise.
    """
    cursor.execute(
        "SELECT COUNT(*) FROM songs WHERE LOWER(title) = LOWER(?) AND "
        "LOWER(artist) = LOWER(?)",
        (title.lower(), artist.lower()),
    )
    return cursor.fetchone()[0] > 0


def get_unique_genres(cursor):
    """
    Fetch all unique genres from the database, excluding artist names.
    """
    cursor.execute(
        "SELECT DISTINCT genres, artist FROM songs "
        "WHERE genres IS NOT NULL AND genres != ''"
    )
    all_genres = cursor.fetchall()
    unique_genres = set()
    artists = set()
    for genres_string, artist in all_genres:
        genres = genres_string.split(", ")
        artists.add(artist.lower())
        unique_genres.update(genre.lower() for genre in genres)

    # Remove genres that match artist names
    filtered_genres = unique_genres - artists

    return sorted(filtered_genres)


def get_unique_tunings(cursor):
    """
    Fetch all unique tunings from the database, case-insensitive.
    """
    cursor.execute(
        "SELECT DISTINCT tuning FROM songs WHERE tuning IS NOT NULL AND tuning != ''"
    )
    tunings = [tuning[0] for tuning in cursor.fetchall()]

    def format_tuning(tuning):
        if len(tuning) == 6 and tuning.isupper():
            return tuning
        return ' '.join(word.capitalize() for word in tuning.split())

    return sorted(set(format_tuning(tuning) for tuning in tunings))
