import pytest
from PyQt6.QtWidgets import QApplication
from gui.main_window import SongApp
from unittest.mock import patch, MagicMock
import os
import sys

# Initialize the Qt Application
app = QApplication(sys.argv)


@pytest.fixture
def song_app():
    """
    Fixture to init the SongApp.
    """
    app = SongApp()
    yield app
    app.conn.close()


def test_initialization(song_app):
    """
    Test if SongApp initializes correctly.
    """
    assert song_app.windowTitle() == "Guitar Parts"
    assert song_app.minimumWidth() == 800
    assert song_app.minimumHeight() == 600


def test_ui_setup(song_app):
    """
    Test if the UI is set up correctly.
    """
    assert song_app.song_tree.columnCount() == 4
    assert song_app.song_tree.headerItem().text(0) == "Artist"
    assert song_app.song_tree.headerItem().text(1) == "Title"
    assert song_app.song_tree.headerItem().text(2) == "Album"
    assert song_app.song_tree.headerItem().text(3) == "Tuning"


@patch("gui.main_window.load_songs")
def test_update_song_list(mock_load_songs, song_app):
    """
    Test if the song list updates correctly.
    """
    mock_load_songs.return_value = [
        MagicMock(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            tuning="Standard",
        )
    ]
    song_app.update_song_list()
    assert song_app.song_tree.topLevelItemCount() == 1
    item = song_app.song_tree.topLevelItem(0)
    assert item.text(0) == "Test Artist"
    assert item.text(1) == "Test Song"
    assert item.text(2) == "Test Album"
    assert item.text(3) == "Standard"


@patch("gui.main_window.get_track_info")
def test_display_song_info(mock_get_track_info, song_app):
    """
    Test if song info is displayed correctly.
    """
    mock_get_track_info.return_value = {
        "track": {
            "name": "Test Song",
            "artist": {"name": "Test Artist"},
            "album": {"title": "Test Album"},
            "duration": "300000",
            "toptags": {"tag": [{"name": "Rock"}, {"name": "Alternative"}]},
        }
    }
    song = MagicMock(
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        tuning="Standard",
        notes="Test Notes",
    )
    song_app.display_song_info(song)
    assert song_app.title_entry.text() == "Test Song"
    assert song_app.artist_entry.text() == "Test Artist"
    assert song_app.tuning_entry.text() == "Standard"
    assert song_app.notes_entry.toPlainText() == "Test Notes"


@patch("gui.main_window.os.path.exists")
@patch("gui.main_window.os.makedirs")
def test_create_cache_directory(mock_makedirs, mock_exists, song_app):
    """
    Test if the cache directory is created correctly.
    """
    mock_exists.return_value = False
    song_app.create_cache_directory()
    mock_makedirs.assert_called_once_with(
        os.path.expanduser("~/.cache/album_art"), exist_ok=True
    )
