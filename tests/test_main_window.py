import os
import sys
import pytest
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QTextEdit,
    QDialog,
    QLabel,
    QDialogButtonBox,
    QCheckBox,
)
from unittest.mock import patch, MagicMock
import logging

# Make sure project root dir is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from views.main_window import SongApp  # noqa: E402 - Import not at top of file
from models.song import Song  # noqa: E402 - Import not at top of file

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


@patch("controllers.song_controller.SongController.get_song")
@patch("controllers.song_controller.SongController.save_song")
@patch("controllers.song_controller.SongController.update_song_info")
def test_save_song(mock_update_song_info, mock_save_song, mock_get_song, song_app):
    # Test adding a new song
    mock_get_song.return_value = None
    mock_save_song.return_value = (True, "Song saved successfully")

    song_app.save_song("Test Artist", "Test Song", "Test Notes", "Standard")

    mock_save_song.assert_called_once()
    saved_song = mock_save_song.call_args[0][0]
    assert isinstance(saved_song, Song)
    assert saved_song.title == "Test Song"
    assert saved_song.artist == "Test Artist"
    assert saved_song.tuning == "Standard"
    assert saved_song.notes == "Test Notes"

    # Test updating an existing song
    mock_get_song.reset_mock()
    mock_save_song.reset_mock()
    mock_update_song_info.reset_mock()

    existing_song = Song(title="Test Song", artist="Test Artist")
    mock_get_song.return_value = existing_song
    mock_update_song_info.return_value = (True, "Song updated successfully")

    song_app.save_song("Test Artist", "Test Song", "Updated Notes", "New Tuning")

    mock_update_song_info.assert_called_once()
    updated_song = mock_update_song_info.call_args[0][0]
    assert updated_song.notes == "Updated Notes"
    assert updated_song.tuning == "New Tuning"
    mock_save_song.assert_not_called()


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
    mock_item = MagicMock()
    mock_item.text.side_effect = ["Test Artist", "Test Song"]
    song_app.last_selected_item = mock_item
    mock_delete_song.return_value = (True, "Song deleted successfully")

    with patch.object(
        song_app, "show_status_message"
    ) as mock_show_status, patch.object(
        song_app, "update_song_list"
    ) as mock_update_song_list:
        song_app.delete_song()

    mock_delete_song.assert_called_once_with("Test Song", "Test Artist")
    mock_show_status.assert_called_once_with(
        "Deleted Test Song by Test Artist successfully"
    )
    mock_update_song_list.assert_called_once()


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

    assert song_app.title_label.text() == "Title: Test Song"
    assert song_app.artist_label.text() == "Artist: Test Artist"
    assert song_app.album_label.text() == "Album: Test Album"
    assert song_app.tuning_label.text() == "Tuning: Standard"
    assert song_app.notes_label.text() == "Notes: Test Notes"


def test_show_status_message(song_app):
    """
    Test if the status message is displayed correctly.
    """
    test_message = "Test Status Message"
    song_app.show_status_message(test_message)

    assert song_app.status_label.text() == test_message


@patch("PyQt6.QtWidgets.QDialog.exec")
@patch("controllers.song_controller.SongController.save_song")
def test_add_song(mock_save_song, mock_dialog_exec, song_app):
    """
    Test if a new song is added correctly, including custom song functionality.
    """
    mock_dialog_exec.return_value = QDialog.DialogCode.Accepted

    with patch.object(QLineEdit, "text") as mock_line_edit_text, patch.object(
        QTextEdit, "toPlainText"
    ) as mock_text_edit_text, patch.object(
        QCheckBox, "isChecked"
    ) as mock_checkbox_checked:

        # Test adding a non-custom song
        mock_line_edit_text.side_effect = ["Test Artist", "Test Song", "Standard"]
        mock_text_edit_text.return_value = "Test Notes"
        mock_checkbox_checked.return_value = False
        mock_save_song.return_value = (True, "Song saved successfully")

        song_app.add_song()

        mock_save_song.assert_called_once()
        saved_song = mock_save_song.call_args[0][0]
        assert isinstance(saved_song, Song)
        assert saved_song.title == "Test Song"
        assert saved_song.artist == "Test Artist"
        assert saved_song.tuning == "Standard"
        assert saved_song.notes == "Test Notes"
        assert not mock_save_song.call_args[0][1]  # is_custom should be False

        # Reset mocks
        mock_save_song.reset_mock()
        mock_line_edit_text.reset_mock()
        mock_text_edit_text.reset_mock()
        mock_checkbox_checked.reset_mock()

        # Test adding a custom song
        mock_line_edit_text.side_effect = [
            "Custom Artist",
            "Custom Song",
            "Drop D",
            "Custom Album",
            "3:30",
            "Rock, Metal",
        ]
        mock_text_edit_text.return_value = "Custom Notes"
        mock_checkbox_checked.return_value = True
        mock_save_song.return_value = (True, "Custom song saved successfully")

        song_app.add_song()

        mock_save_song.assert_called_once()
        saved_song = mock_save_song.call_args[0][0]
        assert isinstance(saved_song, Song)
        assert saved_song.title == "Custom Song"
        assert saved_song.artist == "Custom Artist"
        assert saved_song.tuning == "Drop D"
        assert saved_song.notes == "Custom Notes"
        assert saved_song.album == "Custom Album"
        assert saved_song.duration == "210000"  # 3:30 in milliseconds
        assert saved_song.genres == ["Rock", "Metal"]
        assert mock_save_song.call_args[0][1]  # is_custom should be True


@patch("PyQt6.QtWidgets.QDialog.exec")
@patch("controllers.song_controller.SongController.save_song")
def test_add_song_validation(mock_save_song, mock_dialog_exec, song_app):
    """
    Test if the add song dialog validates required fields correctly.
    """
    mock_dialog_exec.return_value = QDialog.DialogCode.Accepted

    with patch.object(QLineEdit, "text") as mock_line_edit_text, patch.object(
        QTextEdit, "toPlainText"
    ) as mock_text_edit_text, patch.object(
        QLabel, "setText"
    ) as mock_label_set_text, patch.object(
        QDialogButtonBox, "button"
    ) as mock_button:

        # Mock the OK button
        mock_ok_button = MagicMock()
        mock_button.return_value = mock_ok_button

        # Test with empty artist and title
        mock_line_edit_text.side_effect = ["", "", "Standard"]
        mock_text_edit_text.return_value = "Test Notes"

        song_app.add_song()

        mock_label_set_text.assert_any_call("Artist and Title are required.")
        mock_save_song.assert_not_called()
        mock_ok_button.setEnabled.assert_called()

        # Reset mocks
        mock_line_edit_text.reset_mock()
        mock_text_edit_text.reset_mock()
        mock_label_set_text.reset_mock()
        mock_ok_button.reset_mock()

        # Test with valid artist and title
        mock_line_edit_text.side_effect = ["Test Artist", "Test Song", "Standard"]
        mock_text_edit_text.return_value = "Test Notes"
        mock_save_song.return_value = (True, "Song saved successfully")

        song_app.add_song()

        mock_save_song.assert_called_once()
        mock_ok_button.setEnabled.assert_called()


@patch("PyQt6.QtWidgets.QDialog.exec")
@patch("controllers.song_controller.SongController.update_song_info")
@patch("controllers.song_controller.SongController.get_song")
def test_edit_song(mock_get_song, mock_update_song, mock_dialog_exec, song_app):
    """
    Test if a song is edited correctly and metadata is updated.
    """
    mock_dialog_exec.return_value = QDialog.DialogCode.Accepted

    song_app.last_selected_item = MagicMock()
    song_app.last_selected_item.text.side_effect = ["Test Artist", "Test Song"]

    mock_song = MagicMock(notes="Old Notes", tuning="Old Tuning")
    updated_mock_song = MagicMock(notes="New Notes", tuning="New Tuning")
    mock_get_song.side_effect = [mock_song, updated_mock_song]
    mock_update_song.return_value = (True, "Song updated successfully")

    with patch.object(QLineEdit, "text") as mock_line_edit_text, patch.object(
        QTextEdit, "toPlainText"
    ) as mock_text_edit_text, patch.object(
        song_app, "display_song_info"
    ) as mock_display_song_info, patch.object(
        song_app, "update_song_list"
    ) as mock_update_song_list, patch.object(
        song_app, "select_song_in_tree"
    ) as mock_select_song_in_tree:

        mock_line_edit_text.return_value = "New Tuning"
        mock_text_edit_text.return_value = "New Notes"

        song_app.edit_song()

    mock_update_song.assert_called_once()
    mock_update_song_list.assert_called_once()
    mock_select_song_in_tree.assert_called_once_with("Test Song", "Test Artist")
    mock_display_song_info.assert_called_once_with(updated_mock_song)

    # Update these assertions to use the mock_display_song_info call
    mock_display_song_info.assert_called_once()
    args, _ = mock_display_song_info.call_args
    displayed_song = args[0]
    assert displayed_song.tuning == "New Tuning"
    assert displayed_song.notes == "New Notes"


def test_edit_song_no_selection(song_app):
    """
    Test if edit_song handles no song selection correctly.
    """
    song_app.last_selected_item = None
    with patch.object(song_app, "show_status_message") as mock_show_status:
        song_app.edit_song()
    mock_show_status.assert_called_once_with(
        "Please select a song to edit.", error=True
    )


def test_delete_song_no_selection(song_app):
    """
    Test if delete_song handles no song selection correctly.
    """
    song_app.last_selected_item = None
    with patch.object(song_app, "show_status_message") as mock_show_status:
        song_app.delete_song()
    mock_show_status.assert_called_once_with(
        "Please select a song to delete.", error=True
    )


@patch("controllers.song_controller.SongController.get_all_songs")
def test_select_songs_empty_database(mock_get_all_songs, song_app):
    """
    Test if select_songs handles empty database correctly.
    """
    mock_get_all_songs.return_value = []
    with patch.object(song_app, "show_status_message") as mock_show_status:
        song_app.select_songs()
    mock_show_status.assert_called_once_with("No songs in the database to filter")


@patch("controllers.song_controller.SongController.get_all_songs")
def test_select_songs(mock_get_all_songs, song_app, caplog):
    """
    Test if the select songs button logs correctly.
    """
    mock_get_all_songs.return_value = []
    with caplog.at_level(logging.DEBUG):
        song_app.select_songs()

    assert "Select Songs button pressed" in caplog.text
    assert "No songs in the database to filter" in caplog.text
