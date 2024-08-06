"""
Module for database stuffs.
"""

import sqlite3
import os
import sys
from models.song import Song


def get_resource_path(relative_path):
    """
    Get the absolute path to a resource file.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def get_default_db_path():
    """
    Get the default path for the database file.

    Returns:
        str: The default path to the database file.
    """
    home_dir = os.path.expanduser("~")
    db_dir = os.path.join(home_dir, ".guitar_parts")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "songs.db")


def initialize_db(db_file=None, schema_file="db/schema.sql"):
    """
    Init database by connecting to it and creating the schema.

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
