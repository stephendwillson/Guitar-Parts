import os
import sys
import pytest
from PyQt6.QtWidgets import QApplication
from unittest.mock import patch, MagicMock

# Make sure project root dir is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from views.main_window import SongApp  # noqa: E402 - Import not at top of file

# Initialize the Qt Application
app = QApplication(sys.argv)


@pytest.fixture
def song_app():
    """
    Fixture to init the SongApp.
    """
    with patch("services.db.initialize_db") as mock_initialize_db:
        mock_initialize_db.return_value = (MagicMock(), MagicMock())
        app = SongApp()
        yield app
        app.controller.conn.close()


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


@patch("controllers.song_controller.SongController.get_all_songs")
def test_update_song_list(mock_get_all_songs, song_app):
    """
    Test if the song list updates correctly.
    """
    mock_get_all_songs.return_value = [
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


@patch("controllers.song_controller.SongController.get_all_songs")
def test_select_song_in_tree(mock_get_all_songs, song_app):
    """
    Test if a song is selected correctly in the tree view.
    """
    mock_song = MagicMock(
        title="Test Song", artist="Test Artist", album="Test Album", tuning="Standard"
    )
    mock_get_all_songs.return_value = [mock_song]

    song_app.update_song_list()
    song_app.select_song_in_tree("Test Song", "Test Artist")

    selected_item = song_app.song_tree.selectedItems()[0]
    assert selected_item.text(0) == "Test Artist"
    assert selected_item.text(1) == "Test Song"
    assert selected_item.text(2) == "Test Album"
    assert selected_item.text(3) == "Standard"


@patch("controllers.song_controller.SongController.save_song")
def test_save_song(mock_save_song, song_app):
    """
    Test if a song is saved correctly.
    """
    song_app.title_entry.setText("Test Song")
    song_app.artist_entry.setText("Test Artist")
    song_app.tuning_entry.setText("Standard")
    song_app.notes_entry.setPlainText("Test Notes")
    song_app.save_song()
    mock_save_song.assert_called_once()
    saved_song = mock_save_song.call_args[0][0]
    assert saved_song.title == "Test Song"
    assert saved_song.artist == "Test Artist"
    assert saved_song.tuning == "Standard"
    assert saved_song.notes == "Test Notes"


@patch("controllers.song_controller.SongController.get_all_songs")
def test_load_songs(mock_get_all_songs, song_app):
    """
    Test if songs are loaded correctly.
    """
    mock_song = MagicMock(
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        tuning="Standard",
        notes="Test Notes",
    )
    mock_get_all_songs.return_value = [mock_song]

    song_app.load_songs()

    assert song_app.song_tree.topLevelItemCount() == 1
    item = song_app.song_tree.topLevelItem(0)
    assert item.text(0) == "Test Artist"
    assert item.text(1) == "Test Song"
    assert item.text(2) == "Test Album"
    assert item.text(3) == "Standard"


@patch("controllers.song_controller.SongController.delete_song")
def test_delete_song(mock_delete_song, song_app):
    """
    Test if a song is deleted correctly.
    """
    song_app.title_entry.setText("Test Song")
    song_app.artist_entry.setText("Test Artist")
    song_app.delete_song()
    mock_delete_song.assert_called_once_with("Test Song", "Test Artist")


def test_display_song_info(song_app):
    """
    Test if song info is displayed correctly.
    """
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
    assert song_app.title_label.text() == "Title: Test Song"
    assert song_app.artist_label.text() == "Artist: Test Artist"
    assert song_app.album_label.text() == "Album: Test Album"
    assert song_app.tuning_label.text() == "Tuning: Standard"
    assert song_app.notes_label.text() == "Notes: Test Notes"


def test_clear_inputs(song_app):
    """
    Test if the input fields are cleared correctly.
    """
    song_app.title_entry.setText("Test Song")
    song_app.artist_entry.setText("Test Artist")
    song_app.tuning_entry.setText("Standard")
    song_app.notes_entry.setPlainText("Test Notes")

    song_app.clear_inputs()

    assert song_app.title_entry.text() == ""
    assert song_app.artist_entry.text() == ""
    assert song_app.tuning_entry.text() == ""
    assert song_app.notes_entry.toPlainText() == ""


def test_clear_song_display_info(song_app):
    """
    Test if the info displayed for a song is cleared correctly.
    """
    song_app.title_label.setText("Test Song")
    song_app.artist_label.setText("Test Artist")
    song_app.tuning_label.setText("Standard")
    song_app.notes_label.setText("Test Notes")

    song_app.clear_song_display_info()

    assert song_app.title_label.text() == "Title: N/A"
    assert song_app.artist_label.text() == "Artist: N/A"
    assert song_app.tuning_label.text() == "Tuning: N/A"
    assert song_app.notes_label.text() == "Notes: N/A"


def test_show_status_message(song_app):
    """
    Test if the status message is displayed correctly.
    """
    test_message = "Test Status Message"
    song_app.show_status_message(test_message)

    assert song_app.status_label.text() == test_message
