"""
Module for database stuffs.
"""

import sqlite3
import logging
from models.song import Song
from utils.utils import get_default_db_path, get_resource_path, setup_logging

setup_logging()


def get_current_schema_version(cursor):
    """Get the current database schema version"""
    try:
        cursor.execute("SELECT version FROM schema_version")
        return cursor.fetchone()[0]
    except sqlite3.OperationalError:
        # Table doesn't exist - this is a new or pre-versioning database
        return 0


def set_schema_version(cursor, version):
    """Update the schema version in the database"""
    cursor.execute("INSERT OR REPLACE INTO schema_version (id, version) VALUES (1, ?)",
                   (version,))
    cursor.connection.commit()


def add_schema_version_table(cursor):
    """Migration 1: Add schema version tracking"""
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            version INTEGER NOT NULL
        )
    """)
    # Initialize with version 1 if table is empty
    cursor.execute("INSERT OR IGNORE INTO schema_version (id, version) VALUES (1, 1)")


def add_progress_column(cursor):
    """Migration 2: Add progress column to songs table"""
    try:
        # First try to add column to existing table
        cursor.execute("""
            ALTER TABLE songs ADD COLUMN progress TEXT DEFAULT 'Not Started'
        """)
    except sqlite3.OperationalError:
        # If table doesn't exist, create it with all columns
        cursor.execute("""
            CREATE TABLE songs (
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                tuning TEXT,
                notes TEXT,
                album TEXT,
                duration TEXT,
                genres TEXT,
                progress TEXT DEFAULT 'Not Started',
                PRIMARY KEY (title, artist)
            )
        """)


def migrate_database(cursor):
    """
    Handle all database migrations in order.
    Each migration should be idempotent.
    """
    current_version = get_current_schema_version(cursor)
    logging.info(f"Current database version: {current_version}")

    # List of migrations to apply
    migrations = [
        add_schema_version_table,
        add_progress_column,
        # Future migrations will be added here
    ]

    # Apply any migrations that haven't been run yet
    for version, migration in enumerate(migrations, start=1):
        if current_version < version:
            logging.info(f"Applying migration {version}: {migration.__name__}")
            try:
                migration(cursor)
                set_schema_version(cursor, version)
                cursor.connection.commit()
                logging.info(f"Migration {version} completed successfully")
            except Exception as e:
                cursor.connection.rollback()
                logging.error(f"Migration {version} failed: {str(e)}")
                raise


def initialize_db(db_path=None, schema_path=None):
    """Initialize the database with the given schema"""
    if db_path is None:
        db_path = get_default_db_path()
    if schema_path is None:
        schema_path = get_resource_path("db/schema.sql")

    logging.info(f"Initializing database at {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Run migrations
    logging.info("Running database migrations")
    migrate_database(cursor)

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
        "SELECT title, artist, tuning, notes, album, duration, genres, progress "
        "FROM songs WHERE LOWER(title) = LOWER(?) AND LOWER(artist) = LOWER(?)",
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
            progress=row[7],
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
        "INSERT INTO songs (title, artist, tuning, notes, album, duration, "
        "genres, progress) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (
            song.title.lower(),
            song.artist.lower(),
            song.tuning,
            song.notes,
            song.album,
            song.duration,
            ", ".join(song.genres),  # Convert genres to a comma-separated string
            song.progress,
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
        "SELECT title, artist, tuning, notes, album, duration, genres, progress "
        "FROM songs"
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
            progress=row[7],
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
    SET notes = ?, tuning = ?, album = ?, duration = ?, genres = ?, progress = ?
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
            song.progress,
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
