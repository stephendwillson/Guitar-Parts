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
    QComboBox,
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
    assert song_app.song_tree.columnCount() == 5
    assert song_app.song_tree.headerItem().text(0) == "Artist"
    assert song_app.song_tree.headerItem().text(1) == "Title"
    assert song_app.song_tree.headerItem().text(2) == "Album"
    assert song_app.song_tree.headerItem().text(3) == "Tuning"
    assert song_app.song_tree.headerItem().text(4) == "Progress"


@patch("controllers.song_controller.SongController.get_all_songs")
def test_update_song_list(mock_get_all_songs, song_app):
    """Test updating the song list."""
    test_song = Song(
        "Test Song", "Test Artist", album="Test Album", progress="Not Started")
    mock_get_all_songs.return_value = [test_song]

    song_app.update_song_list(mock_get_all_songs.return_value)

    assert song_app.song_tree.topLevelItemCount() == 1
    item = song_app.song_tree.topLevelItem(0)
    assert item.text(0) == test_song.artist
    assert item.text(1) == test_song.title
    assert item.text(2) == test_song.album
    assert item.text(4) == test_song.progress


@patch("controllers.song_controller.SongController.get_all_songs")
def test_select_song_in_tree(mock_get_all_songs, song_app):
    """
    Test if a song is selected correctly in the tree view.
    """
    mock_song = MagicMock(
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        tuning="Standard",
        notes="Test Notes",
        progress="Not Started",
        __str__=lambda x: "Test Song by Test Artist"
    )
    mock_get_all_songs.return_value = [mock_song]

    song_app.update_song_list(song_app.controller.get_all_songs())
    song_app.select_song_in_tree("Test Song", "Test Artist")

    selected_item = song_app.song_tree.selectedItems()[0]
    assert selected_item.text(0) == "Test Artist"
    assert selected_item.text(1) == "Test Song"
    assert selected_item.text(2) == "Test Album"
    assert selected_item.text(3) == "Standard"


@patch("controllers.song_controller.SongController.get_song")
@patch("controllers.song_controller.SongController.save_song")
@patch("controllers.song_controller.SongController.update_song_info")
@patch("controllers.song_controller.SongController.get_all_songs")
def test_save_song(
    mock_get_all_songs,
    mock_update_song_info,
    mock_save_song,
    mock_get_song,
    song_app
):
    # Test adding a new song
    mock_get_song.return_value = None
    mock_save_song.return_value = (True, "Song saved successfully")
    mock_get_all_songs.return_value = [
        Song("Test Song", "Test Artist", album="Test Album", tuning="Standard")
    ]

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
        progress="Not Started"
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
        "Deleted 'Test Song' by Test Artist successfully"
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
@patch("controllers.song_controller.SongController.get_all_songs")
def test_add_song(mock_get_all_songs, mock_save_song, mock_dialog_exec, song_app):
    """
    Test if a song is added correctly.
    """
    mock_dialog_exec.return_value = QDialog.DialogCode.Accepted
    mock_save_song.return_value = (True, "Song saved successfully")
    mock_get_all_songs.return_value = [
        Song("Custom Song", "Custom Artist", album="Custom Album", tuning="Drop D")
    ]

    with patch.object(QLineEdit, "text") as mock_line_edit_text, \
         patch.object(QTextEdit, "toPlainText") as mock_text_edit_text, \
         patch.object(QComboBox, "currentText") as mock_combo_box_text, \
         patch.object(QCheckBox, "isChecked") as mock_checkbox_checked:

        mock_line_edit_text.side_effect = [
            "Custom Artist",
            "Custom Song",
            "Drop D",
            "Custom Album",
            "210000",
            "Rock, Metal",
        ]
        mock_text_edit_text.return_value = "Custom Notes"
        mock_combo_box_text.return_value = "Drop D"
        mock_checkbox_checked.return_value = True

        song_app.add_song()

        mock_save_song.assert_called_once()
        saved_song = mock_save_song.call_args[0][0]
        assert isinstance(saved_song, Song)
        assert saved_song.title == "Custom Song"
        assert saved_song.artist == "Custom Artist"
        assert saved_song.tuning == "Drop D"
        assert saved_song.notes == "Custom Notes"
        assert saved_song.album == "Custom Album"
        assert saved_song.duration == "210000"
        assert saved_song.genres == ["Rock", "Metal"]
        assert saved_song.progress == "Not Started"
        assert mock_save_song.call_args[0][1]  # is_custom should be True


@patch("PyQt6.QtWidgets.QDialog.exec")
@patch("controllers.song_controller.SongController.save_song")
@patch("controllers.song_controller.SongController.get_all_songs")
def test_add_song_validation(
    mock_get_all_songs,
    mock_save_song,
    mock_dialog_exec,
    song_app
):
    """
    Test if the add song dialog validates required fields correctly.
    """
    mock_dialog_exec.return_value = QDialog.DialogCode.Accepted
    mock_get_all_songs.return_value = []

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
        mock_line_edit_text.side_effect = ["", "", "Standard", "", "", ""]
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
        mock_line_edit_text.side_effect = [
            "Test Artist", "Test Song", "Standard", "Test Artist", "Test Song"
        ]
        mock_text_edit_text.return_value = "Test Notes"
        mock_save_song.return_value = (True, "Song saved successfully")

        song_app.add_song()

        mock_save_song.assert_called_once()
        mock_ok_button.setEnabled.assert_called()


@patch("PyQt6.QtWidgets.QDialog.exec")
@patch("controllers.song_controller.SongController.update_song_info")
@patch("controllers.song_controller.SongController.get_song")
@patch("controllers.song_controller.SongController.get_all_songs")
def test_edit_song(mock_get_all_songs, mock_get_song, mock_update_song,
                   mock_dialog_exec, song_app):
    """Test editing a song."""
    mock_dialog_exec.return_value = QDialog.DialogCode.Accepted
    mock_update_song.return_value = (True, "Song updated successfully")
    test_song = Song("Test Song", "Test Artist", progress="Not Started")
    mock_get_song.return_value = test_song

    # Mock the selected item
    mock_item = MagicMock()
    mock_item.text.side_effect = ["Test Artist", "Test Song"]
    song_app.last_selected_item = mock_item

    with patch.object(QTextEdit, "toPlainText") as mock_text_edit_text, \
         patch.object(QLineEdit, "text") as mock_line_edit_text, \
         patch.object(QComboBox, "currentText") as mock_combo_box_text:

        mock_text_edit_text.return_value = "Updated Notes"
        mock_line_edit_text.return_value = "Drop D"
        mock_combo_box_text.return_value = "Learning"

        song_app.edit_song()

        mock_update_song.assert_called_once()
        updated_song = mock_update_song.call_args[0][0]
        assert isinstance(updated_song, Song)
        assert updated_song.progress == "Learning"


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
@patch("controllers.song_controller.SongController.get_unique_genres")
@patch("controllers.song_controller.SongController.get_unique_tunings")
def test_show_select_songs_dialog_empty_database(
    mock_get_unique_tunings,
    mock_get_unique_genres,
    mock_get_all_songs,
    song_app
):
    """
    Test if show_select_songs_dialog handles empty database correctly.
    """
    mock_get_all_songs.return_value = []
    mock_get_unique_genres.return_value = []
    mock_get_unique_tunings.return_value = []
    with patch.object(song_app, "show_status_message") as mock_show_status, \
         patch("PyQt6.QtWidgets.QDialog.exec") as mock_dialog_exec:
        mock_dialog_exec.return_value = QDialog.DialogCode.Rejected
        song_app.show_select_songs_dialog()
    mock_show_status.assert_called_once_with("No songs in the database to filter")


@patch("controllers.song_controller.SongController.get_all_songs")
@patch("controllers.song_controller.SongController.get_unique_genres")
@patch("controllers.song_controller.SongController.get_unique_tunings")
def test_show_select_songs_dialog(
    mock_get_unique_tunings,
    mock_get_unique_genres,
    mock_get_all_songs,
    song_app,
    caplog
):
    """
    Test if the show select songs dialog logs correctly.
    """
    mock_get_all_songs.return_value = [MagicMock()]
    mock_get_unique_genres.return_value = ["Rock", "Pop"]
    mock_get_unique_tunings.return_value = ["Standard", "Drop D"]
    with caplog.at_level(logging.DEBUG), \
         patch("PyQt6.QtWidgets.QDialog.exec") as mock_dialog_exec:
        mock_dialog_exec.return_value = QDialog.DialogCode.Rejected
        song_app.show_select_songs_dialog()

    assert "Opening Select Songs dialog" in caplog.text
    assert "Select Songs button pressed" in caplog.text


@patch("PyQt6.QtWidgets.QDialog.exec")
@patch("controllers.song_controller.SongController.update_song_info")
@patch("controllers.song_controller.SongController.get_song")
@patch("controllers.song_controller.SongController.get_all_songs")
def test_edit_song_progress(mock_get_all_songs, mock_get_song, mock_update_song,
                            mock_dialog_exec, song_app):
    """Test editing song progress."""
    mock_dialog_exec.return_value = QDialog.DialogCode.Accepted
    mock_update_song.return_value = (True, "Song updated successfully")
    test_song = Song("Test Song", "Test Artist", progress="Not Started")
    mock_get_song.return_value = test_song

    # Mock the selected item
    mock_item = MagicMock()
    mock_item.text.side_effect = ["Test Artist", "Test Song"]
    song_app.last_selected_item = mock_item

    with patch.object(QTextEdit, "toPlainText") as mock_text_edit_text, \
         patch.object(QLineEdit, "text") as mock_line_edit_text, \
         patch.object(QComboBox, "currentText") as mock_combo_box_text:

        mock_text_edit_text.return_value = "Updated Notes"
        mock_line_edit_text.return_value = "Drop D"
        mock_combo_box_text.return_value = "Learning"

        song_app.edit_song()

        mock_update_song.assert_called_once()
        updated_song = mock_update_song.call_args[0][0]
        assert isinstance(updated_song, Song)
        assert updated_song.progress == "Learning"


@patch("controllers.song_controller.SongController.get_all_songs")
@patch("controllers.song_controller.SongController.get_unique_genres")
@patch("controllers.song_controller.SongController.get_unique_tunings")
def test_select_songs_dialog_exclude_mastered(
    mock_get_unique_tunings,
    mock_get_unique_genres,
    mock_get_all_songs,
    song_app
):
    """Test selecting songs with exclude mastered option."""
    # Setup mock data
    mock_get_unique_genres.return_value = ["Rock", "Metal"]
    mock_get_unique_tunings.return_value = ["Standard", "Drop D"]
    mock_get_all_songs.return_value = [
        Song("Song 1", "Artist 1", progress="Mastered"),
        Song("Song 2", "Artist 2", progress="Learning"),
        Song("Song 3", "Artist 3", progress="Not Started")
    ]

    # Show dialog and interact with it
    with patch.object(QDialog, "exec") as mock_dialog_exec:
        mock_dialog_exec.return_value = QDialog.DialogCode.Accepted

        # Mock the checkbox state
        with patch.object(QCheckBox, "isChecked") as mock_checkbox:
            mock_checkbox.return_value = True  # Exclude mastered songs

            # Call the method
            song_app.show_select_songs_dialog()

            # Verify filter settings were updated
            assert song_app.filter_settings["exclude_mastered"] is True


@patch("controllers.song_controller.SongController.get_all_songs")
def test_filter_songs_exclude_mastered(mock_get_all_songs, song_app):
    """Test filtering out mastered songs."""
    # Create test songs
    songs = [
        Song("Song 1", "Artist 1", progress="Mastered"),
        Song("Song 2", "Artist 2", progress="Learning"),
        Song("Song 3", "Artist 3", progress="Not Started")
    ]
    mock_get_all_songs.return_value = songs

    # Filter songs
    filtered_songs = song_app.controller.filter_songs(exclude_mastered=True)

    # Verify results
    assert len(filtered_songs) == 2
    assert all(song.progress != "Mastered" for song in filtered_songs)
    assert any(song.title == "Song 2" for song in filtered_songs)
    assert any(song.title == "Song 3" for song in filtered_songs)


def test_filter_songs(song_app):
    """Test filtering songs with various criteria."""
    # Create test songs
    songs = [
        Song("Test Song", "Test Artist", album="Test Album",
             genres=["Rock"], tuning="E Standard", progress="Learning"),
        Song("Another Song", "Another Artist", album="Another Album",
             genres=["Metal"], tuning="Drop D", progress="Mastered"),
    ]

    with patch.object(song_app.controller, "get_all_songs", return_value=songs):
        # Test filtering with various criteria
        filtered = song_app.controller.filter_songs(
            artist="Test",
            title="Song",
            album="Album",
            genre="Rock",
            tunings={"E Standard"},
            exclude_mastered=False  # Add this parameter
        )
        assert len(filtered) == 1
        assert filtered[0].title == "Test Song"

        # Test excluding mastered songs
        filtered = song_app.controller.filter_songs(exclude_mastered=True)
        assert len(filtered) == 1
        assert filtered[0].progress != "Mastered"
