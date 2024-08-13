import sys
import os
import pytest

# Make sure project root dir is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.db import (  # noqa: E402 - Import not at top of file
    initialize_db,
    save_song,
    load_songs,
    delete_song,
    update_song_info,
    song_exists,
)
from models.song import Song  # noqa: E402 - Import not at top of file


@pytest.fixture
def db_cursor():
    """
    Fixture to initialize the database and provide a cursor.
    """
    conn, cursor = initialize_db(":memory:", "db/schema.sql")
    yield cursor

    conn.close()


def test_initialize_db(db_cursor):
    """
    Test if the database schema is created correctly.
    """
    db_cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='songs';"
    )
    assert db_cursor.fetchone() is not None


def test_save_song(db_cursor):
    """
    Test saving a song to the database.
    """
    song = Song(
        title="Test Song",
        artist="Test Artist",
        tuning="Standard",
        notes="Test notes",
        album="Test Album",
        duration="3:30",
        genres=["Rock"],
    )
    save_song(db_cursor, song)
    db_cursor.execute(
        "SELECT * FROM songs WHERE title='test song' AND artist='test artist';"
    )
    result = db_cursor.fetchone()
    assert result is not None


def test_load_songs(db_cursor):
    """
    Test loading songs from the database.
    """
    song = Song(
        title="Test Song",
        artist="Test Artist",
        tuning="Standard",
        notes="Test notes",
        album="Test Album",
        duration="3:30",
        genres=["Rock"],
    )
    save_song(db_cursor, song)
    songs = load_songs(db_cursor)
    assert len(songs) == 1
    assert songs[0].title == "test song"
    assert songs[0].artist == "test artist"


def test_delete_song(db_cursor):
    """
    Test deleting a song from the database.
    """
    song = Song(
        title="Test Song",
        artist="Test Artist",
        tuning="Standard",
        notes="Test notes",
        album="Test Album",
        duration="3:30",
        genres=["Rock"],
    )
    save_song(db_cursor, song)
    delete_song(db_cursor, "Test Song", "Test Artist")
    db_cursor.execute(
        "SELECT * FROM songs WHERE title='test song' AND artist='test artist';"
    )
    result = db_cursor.fetchone()
    assert result is None


def test_update_song_info(db_cursor):
    """
    Test updating song data in the database.
    """
    song = Song(
        title="Test Song",
        artist="Test Artist",
        tuning="Standard",
        notes="Test notes",
        album="Test Album",
        duration="3:30",
        genres=["Rock"],
    )
    save_song(db_cursor, song)
    song.notes = "Updated notes"
    update_song_info(db_cursor, song)
    db_cursor.execute(
        "SELECT notes FROM songs WHERE title='test song' AND artist='test artist';"
    )
    result = db_cursor.fetchone()
    assert result[0] == "Updated notes"


def test_song_exists(db_cursor):
    """
    Test if a song exists in the database.
    """
    song = Song(
        title="Test Song",
        artist="Test Artist",
        tuning="Standard",
        notes="Test notes",
        album="Test Album",
        duration="3:30",
        genres=["Rock"],
    )
    save_song(db_cursor, song)
    assert song_exists(db_cursor, "Test Song", "Test Artist")
    assert not song_exists(db_cursor, "Bogus Song", "Bunk Artist")
