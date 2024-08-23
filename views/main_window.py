"""
Main application module.
"""

import sys
import logging
from titlecase import titlecase

from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QTextEdit,
    QScrollArea,
    QApplication,
    QTreeWidgetItem,
    QHeaderView,
    QDialog,
    QDialogButtonBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

from controllers.song_controller import SongController
from models.song import Song
from utils.utils import setup_logging

setup_logging()


class SongApp(QMainWindow):
    """
    Main app class.
    """

    def __init__(self):
        """
        Init main window and set up the UI.
        """
        super().__init__()

        self.setWindowTitle("Guitar Parts")
        self.setMinimumSize(800, 600)
        logging.debug("Initializing main window")

        # Init controller
        self.controller = SongController()
        logging.debug("Controller initialized")

        # Grab cache dir for album art thumbnails
        self.cache_dir = self.controller.get_cache_dir()

        # Setup central widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        self.last_selected_item = None

        self.setup_ui()
        logging.debug("UI setup complete")

    def setup_ui(self):
        """
        Set up the UI.
        """
        # Song tree
        self.song_tree = QTreeWidget()
        self.song_tree.setColumnCount(4)
        self.song_tree.setHeaderLabels(["Artist", "Title", "Album", "Tuning"])
        self.song_tree.itemClicked.connect(self.on_treeview_click)
        self.song_tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.main_layout.addWidget(self.song_tree)

        # Enable sorting on column click
        self.song_tree.setSortingEnabled(True)

        # Set default sort order alphabetical based on first column
        self.song_tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Let users resize columns and stretch columns to fill window
        header = self.song_tree.header()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        # Set columns to equal width
        column_count = self.song_tree.columnCount()
        for column in range(column_count):
            header.resizeSection(column, self.song_tree.width() // column_count)

        # Buttons
        self.button_layout = QHBoxLayout()

        self.add_song_button = QPushButton("Add Song")
        self.add_song_button.clicked.connect(self.add_song)
        self.button_layout.addWidget(self.add_song_button)

        self.delete_button = QPushButton("Delete Song")
        self.delete_button.clicked.connect(self.delete_song)
        self.button_layout.addWidget(self.delete_button)

        self.edit_button = QPushButton("Edit Song")
        self.edit_button.clicked.connect(self.edit_song)
        self.button_layout.addWidget(self.edit_button)

        self.select_songs_button = QPushButton("Select Songs...")
        self.select_songs_button.clicked.connect(self.select_songs)
        self.button_layout.addWidget(self.select_songs_button)

        # Add button layout to main layout
        self.main_layout.addLayout(self.button_layout)

        # Search input
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Title or Artist")
        self.search_entry.textChanged.connect(self.update_song_list)
        self.main_layout.addWidget(self.search_entry)

        # Metadata display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.metadata_widget = QWidget()
        self.metadata_layout = QVBoxLayout(self.metadata_widget)

        self.artist_label = QLabel("Artist: N/A")
        self.title_label = QLabel("Title: N/A")
        self.album_label = QLabel("Album: N/A")
        self.duration_label = QLabel("Duration: N/A")
        self.genres_label = QLabel("Genres: N/A")
        self.tuning_label = QLabel("Tuning: N/A")
        self.notes_label = QLabel("Notes: N/A")

        self.metadata_layout.addWidget(self.artist_label)
        self.metadata_layout.addWidget(self.title_label)
        self.metadata_layout.addWidget(self.album_label)
        self.metadata_layout.addWidget(self.duration_label)
        self.metadata_layout.addWidget(self.genres_label)
        self.metadata_layout.addWidget(self.tuning_label)
        self.metadata_layout.addWidget(self.notes_label)

        self.scroll_area.setWidget(self.metadata_widget)

        # Create horizontal layout for metadata and album art
        self.metadata_album_layout = QHBoxLayout()
        self.metadata_album_layout.addWidget(self.scroll_area)

        self.album_art_label = QLabel()
        self.album_art_label.setFixedSize(300, 300)
        self.album_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.metadata_album_layout.addWidget(self.album_art_label)
        self.main_layout.addLayout(self.metadata_album_layout)

        self.update_song_list()

        # Status bar
        self.status_bar = self.statusBar()
        self.status_label = QLabel()
        self.status_bar.addWidget(self.status_label)

    def on_treeview_click(self, item, column):
        """
        Handle treeview item click event.

        Args:
            item (QTreeWidgetItem): The clicked item.
            column (int): The column of the clicked item.
        """
        artist = item.text(0)
        title = item.text(1)
        logging.debug("Treeview item clicked: %s by %s", title, artist)

        if self.last_selected_item == item:
            self.song_tree.setCurrentItem(None)
            self.clear_song_display_info()
            self.last_selected_item = None
            logging.debug("Deselected item")
        else:
            song = self.controller.get_song(title, artist)
            if song:
                self.display_song_info(song)
                self.last_selected_item = item
                logging.debug("Selected song: %s by %s", song.title, song.artist)
            else:
                logging.error("Song not found: %s by %s", title, artist)
                self.show_status_message(
                    f"Song not found: {title} by {artist}", error=True
                )

    def select_song_in_tree(self, title, artist):
        """
        Select a specific song in the tree view.

        This method searches for a song with the given title and artist
        in the song tree and selects it if found.

        Args:
            title (str): The title of the song to select.
            artist (str): The artist of the song to select.
        """
        for i in range(self.song_tree.topLevelItemCount()):
            item = self.song_tree.topLevelItem(i)
            if item.text(0) == artist and item.text(1) == title:
                self.song_tree.setCurrentItem(item)
                self.last_selected_item = item
                break

    def update_song_list(self):
        """
        Update the song list in the UI.
        """
        self.song_tree.clear()
        songs = self.controller.get_all_songs()
        for song in songs:
            item = QTreeWidgetItem(
                [titlecase(song.artist), titlecase(song.title), song.album, song.tuning]
            )
            self.song_tree.addTopLevelItem(item)

    def display_song_info(self, song):
        logging.debug("Displaying song info: %s by %s", song.title, song.artist)

        self.artist_label.setText(f"Artist: {titlecase(song.artist)}")
        self.title_label.setText(f"Title: {titlecase(song.title)}")
        self.album_label.setText(f"Album: {song.album}")

        # Show duration as minutes:seconds
        if song.duration:
            minutes, seconds = divmod(int(song.duration) // 1000, 60)
            formatted_duration = f"{minutes}:{seconds:02}"
        else:
            formatted_duration = "N/A"
        self.duration_label.setText(f"Duration: {formatted_duration}")

        self.genres_label.setText(
            f"Genres: {', '.join(song.genres) if song.genres else 'N/A'}"
        )
        self.tuning_label.setText(f"Tuning: {song.tuning}")
        self.notes_label.setText(f"Notes: {song.notes}")

        logging.debug(
            "Song metadata displayed: Title=%s, Artist=%s, Album=%s, Duration=%s, "
            "Genres=%s, Tuning=%s, Notes=%s",
            song.title,
            song.artist,
            song.album,
            formatted_duration,
            ", ".join(song.genres) if song.genres else "N/A",
            song.tuning,
            song.notes,
        )

        # Display album art
        album_art_path = self.controller.get_cached_album_art(song.album)
        if album_art_path:
            logging.debug("Using cached album art from %s", album_art_path)
            pixmap = QPixmap(album_art_path)
            self.album_art_label.setPixmap(
                pixmap.scaled(
                    self.album_art_label.size(), Qt.AspectRatioMode.KeepAspectRatio
                )
            )
        else:
            logging.debug("No album art found for %s", song.album)
            self.album_art_label.setText("No album art available")
            self.album_art_label.setStyleSheet(
                "background-color: #f0f0f0; color: #888888;"
            )

    def clear_song_display_info(self):
        """
        Clear the song display info.
        """
        logging.debug("Clearing song display info")

        self.artist_label.setText("Artist: N/A")
        self.title_label.setText("Title: N/A")
        self.album_label.setText("Album: N/A")
        self.duration_label.setText("Duration: N/A")
        self.genres_label.setText("Genres: N/A")
        self.tuning_label.setText("Tuning: N/A")
        self.notes_label.setText("Notes: N/A")
        self.album_art_label.clear()

        logging.debug("Song display info cleared")

    def show_status_message(self, message, error=False, duration=5000):
        self.status_label.setText(message)
        if error:
            self.status_label.setStyleSheet("color: red;")
        else:
            self.status_label.setStyleSheet("color: black;")
        logging.info(f"Status message: {message}")

        # Set a timer to clear the message after the specified duration
        QTimer.singleShot(duration, self.status_label.clear)

    def add_song(self):
        """
        Prompt user for new song details and add to database.
        """
        logging.debug("Opening add song dialog")
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Song")
        layout = QVBoxLayout(dialog)

        artist_input = QLineEdit(dialog)
        artist_input.setPlaceholderText("Artist (required)")
        layout.addWidget(artist_input)

        title_input = QLineEdit(dialog)
        title_input.setPlaceholderText("Title (required)")
        layout.addWidget(title_input)

        notes_input = QTextEdit(dialog)
        notes_input.setPlaceholderText("Notes (optional)")
        layout.addWidget(notes_input)

        tuning_input = QLineEdit(dialog)
        tuning_input.setPlaceholderText("Tuning (optional)")
        layout.addWidget(tuning_input)

        error_label = QLabel()
        error_label.setStyleSheet("color: red;")
        layout.addWidget(error_label)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        ok_button.setEnabled(False)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        def validate_inputs():
            artist = artist_input.text().strip()
            title = title_input.text().strip()
            if artist and title:
                ok_button.setEnabled(True)
                error_label.clear()
            else:
                ok_button.setEnabled(False)
                error_label.setText("Artist and Title are required.")

        artist_input.textChanged.connect(validate_inputs)
        title_input.textChanged.connect(validate_inputs)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            artist = artist_input.text().strip()
            title = title_input.text().strip()
            notes = notes_input.toPlainText().strip()
            tuning = tuning_input.text().strip()

            if artist and title:
                logging.debug(f"Adding song: {title} by {artist}")
                self.save_song(artist, title, notes, tuning)
            else:
                error_label.setText("Artist and Title are required.")
                return

    def save_song(self, artist, title, notes, tuning):
        """
        Save or update a song in the database.
        """
        logging.debug(f"Saving song: {title} by {artist}")
        # Check if the song already exists
        existing_song = self.controller.get_song(title, artist)

        if existing_song:
            # Update existing song
            logging.debug(f"Updating existing song: {title} by {artist}")
            existing_song.notes = notes
            existing_song.tuning = tuning
            success, message = self.controller.update_song_info(existing_song)
        else:
            # Create a new song object
            song = Song(
                title=title,
                artist=artist,
                tuning=tuning,
                notes=notes,
            )

            # Save the new song, which will fetch track info if needed
            success, message = self.controller.save_song(song)

        self.show_status_message(message, error=not success)
        if success:
            self.update_song_list()

    def edit_song(self):
        if not self.last_selected_item:
            self.show_status_message("Please select a song to edit.", error=True)
            logging.warning("Edit attempt failed: No song selected")
            return

        try:
            artist = self.last_selected_item.text(0)
            title = self.last_selected_item.text(1)
            song = self.controller.get_song(title, artist)

            if song:
                dialog = QDialog(self)
                dialog.setWindowTitle("Edit Song")
                layout = QVBoxLayout(dialog)

                notes_input = QTextEdit(dialog)
                notes_input.setPlaceholderText("Notes")
                notes_input.setText(song.notes)
                layout.addWidget(notes_input)

                tuning_input = QLineEdit(dialog)
                tuning_input.setPlaceholderText("Tuning")
                tuning_input.setText(song.tuning)
                layout.addWidget(tuning_input)

                button_box = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok
                    | QDialogButtonBox.StandardButton.Cancel
                )
                button_box.accepted.connect(dialog.accept)
                button_box.rejected.connect(dialog.reject)
                layout.addWidget(button_box)

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    song.notes = notes_input.toPlainText()
                    song.tuning = tuning_input.text()
                    success, message = self.controller.update_song_info(song)
                    if success:
                        self.show_status_message(message)
                        self.update_song_list()
                        self.select_song_in_tree(title, artist)
                        updated_song = self.controller.get_song(title, artist)
                        self.display_song_info(updated_song)
                    else:
                        self.show_status_message(message, error=True)
        except Exception as e:
            logging.error(f"Error in edit_song: {str(e)}")
            self.show_status_message(
                "An error occurred while editing the song.", error=True
            )

    def delete_song(self):
        """
        Delete the selected song from the database.
        """
        if not self.last_selected_item:
            self.show_status_message("Please select a song to delete.", error=True)
            return

        artist = self.last_selected_item.text(0)
        title = self.last_selected_item.text(1)

        logging.debug("Deleting song: %s by %s", title, artist)

        try:
            self.controller.delete_song(title, artist)
            self.clear_song_display_info()
            self.update_song_list()
            self.show_status_message(f"Deleted {title} by {artist} successfully")
        except Exception as e:
            self.show_status_message(
                "Unable to delete the song. Please try again.", error=True
            )
            logging.exception(f"Error in delete_song: {str(e)}")

    def select_songs(self):
        """
        Placeholder for select songs functionality.
        """
        logging.debug("Select Songs button pressed")
        songs = self.controller.get_all_songs()
        if not songs:
            self.show_status_message("No songs in the database to filter")
            return

        self.show_status_message("Select Songs button pressed")

    def load_songs(self):
        """
        Load songs from the database and populate the tree widget.
        """
        songs = self.controller.get_all_songs()
        self.song_tree.clear()
        for song in songs:
            item = QTreeWidgetItem(
                [titlecase(song.artist), titlecase(song.title), song.album, song.tuning]
            )
            self.song_tree.addTopLevelItem(item)
        logging.debug("Songs loaded into tree view")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SongApp()
    window.show()
    sys.exit(app.exec())
