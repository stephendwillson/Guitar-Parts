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
    QMessageBox,
    QHeaderView,
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
        self.save_button = QPushButton("Save Song")
        self.save_button.clicked.connect(self.save_song)
        self.button_layout.addWidget(self.save_button)

        self.delete_button = QPushButton("Delete Song")
        self.delete_button.clicked.connect(self.delete_song)
        self.button_layout.addWidget(self.delete_button)

        # Add button layout to main layout
        self.main_layout.addLayout(self.button_layout)

        # Text input boxes
        self.search_entry = QLineEdit()
        self.search_entry.setPlaceholderText("Search by Title or Artist")
        self.search_entry.textChanged.connect(self.update_song_list)
        self.main_layout.addWidget(self.search_entry)

        # Artist input
        self.artist_entry = QLineEdit()
        self.artist_entry.setPlaceholderText("Artist *")
        self.main_layout.addWidget(self.artist_entry)

        # Inline error message for artist
        self.artist_error_label = QLabel()
        self.artist_error_label.setStyleSheet("color: red")
        self.artist_error_label.setVisible(False)
        self.main_layout.addWidget(self.artist_error_label)

        # Title input
        self.title_entry = QLineEdit()
        self.title_entry.setPlaceholderText("Song Title *")
        self.main_layout.addWidget(self.title_entry)

        # Inline error message for title
        self.title_error_label = QLabel()
        self.title_error_label.setStyleSheet("color: red")
        self.title_error_label.setVisible(False)
        self.main_layout.addWidget(self.title_error_label)

        self.tuning_entry = QLineEdit()
        self.tuning_entry.setPlaceholderText("Tuning")
        self.main_layout.addWidget(self.tuning_entry)

        self.notes_entry = QTextEdit()
        self.notes_entry.setPlaceholderText("Notes")
        self.main_layout.addWidget(self.notes_entry)

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

        # Clear previous error messages
        self.title_error_label.clear()
        self.artist_error_label.clear()
        self.title_error_label.setVisible(False)
        self.artist_error_label.setVisible(False)

        if self.last_selected_item == item:
            self.song_tree.setCurrentItem(None)
            self.clear_inputs()
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
                QMessageBox.warning(
                    self, "Error", f"Song not found: {title} by {artist}"
                )

    def select_song_in_tree(self, title, artist):
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

        self.title_entry.setText(song.title)
        self.artist_entry.setText(song.artist)
        self.tuning_entry.setText(song.tuning)
        self.notes_entry.setText(song.notes)

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

        # Pretty up the list of genres, ie ['pop', 'rock'] -> pop, rock
        genres_display = "".join(song.genres).replace(",", ", ").rstrip(", ")
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
            song.duration,
            genres_display,
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
            logging.debug(
                "No cached album art found for %s, downloading...", song.album
            )
            track_info = self.controller.get_track_info(song.artist, song.title)
            album_art_url = track_info.get("album_art_url")
            if album_art_url:
                album_art_path = self.controller.fetch_and_cache_album_art(
                    album_art_url, song.album
                )
                if album_art_path:
                    logging.debug(
                        "Downloaded and cached album art to %s", album_art_path
                    )
                    pixmap = QPixmap(album_art_path)
                    self.album_art_label.setPixmap(
                        pixmap.scaled(
                            self.album_art_label.size(),
                            Qt.AspectRatioMode.KeepAspectRatio,
                        )
                    )
                else:
                    logging.error("Failed to download album art.")
                    self.album_art_label.clear()
            else:
                logging.error("No album art URL found.")
                self.album_art_label.clear()

    def clear_inputs(self):
        """
        Clear the input fields.
        """
        logging.debug("Clearing input fields")

        self.title_entry.clear()
        self.artist_entry.clear()
        self.tuning_entry.clear()
        self.notes_entry.clear()
        self.title_entry.setReadOnly(False)
        self.artist_entry.setReadOnly(False)
        self.last_selected_item = None

        logging.debug("Input fields cleared")

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

    def show_status_message(self, message, duration=5000):
        self.status_label.setText(message)
        QTimer.singleShot(duration, lambda: self.status_label.clear())

    def save_song(self):
        """
        Save the current song to the database.
        """
        title = titlecase(self.title_entry.text())
        artist = titlecase(self.artist_entry.text())
        tuning = self.tuning_entry.text()
        notes = self.notes_entry.toPlainText()

        # Clear previous error messages
        self.title_error_label.clear()
        self.artist_error_label.clear()
        self.title_error_label.setVisible(False)
        self.artist_error_label.setVisible(False)

        if not title or not artist:
            if not title:
                self.title_error_label.setText("Title is required.")
                self.title_error_label.setVisible(True)
            if not artist:
                self.artist_error_label.setText("Artist is required.")
                self.artist_error_label.setVisible(True)
            return

        logging.debug("Saving song: %s by %s", title, artist)
        self.show_status_message(f"Saving {title}...", 5000)

        # Handle updating if song exists, or add to db if song is new
        if self.last_selected_item:
            song = self.controller.get_song(title, artist)

            # If a song is 'selected' this should never fire
            if song is None:
                logging.error("Song not found in the database: %s by %s", title, artist)
                return

            if song.notes == notes and song.tuning == tuning:
                self.show_status_message(f"No changes detected for {title}.", 5000)
                logging.debug("No changes detected for the song")
                return

            song.notes = notes
            song.tuning = tuning
            self.controller.update_song_info(song)
            self.show_status_message(f"{title} updated successfully.", 5000)
            logging.debug("Song updated successfully")
        else:
            if self.controller.song_exists(title, artist):
                QMessageBox.warning(
                    self, "Duplicate Song", "This song already exists in the database."
                )
                logging.debug("Song already exists in the database")
                return

            # Fetch track info from Last.fm
            track_info = self.controller.get_track_info(artist, title)
            album = track_info.get("track", {}).get("album", {}).get("title", "N/A")
            duration = track_info.get("track", {}).get("duration", 0)
            genres = [
                tag["name"]
                for tag in track_info.get("track", {}).get("toptags", {}).get("tag", [])
            ]
            album_art_url = track_info.get("album_art_url")

            # Fetch and cache album art
            self.controller.fetch_and_cache_album_art(album_art_url, album)

            song = Song(
                title=title,
                artist=artist,
                tuning=tuning,
                notes=notes,
                album=album,
                duration=duration,
                genres=genres,
            )

            self.controller.save_song(song)
            self.show_status_message(
                f"Saved {title} to {self.controller.get_default_db_path()}.", 5000
            )
            logging.debug("Song saved successfully")

        self.update_song_list()
        self.select_song_in_tree(title, artist)
        self.display_song_info(song)

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

    def delete_song(self):
        """
        Delete the selected song from the database.
        """
        artist = self.artist_entry.text()
        title = self.title_entry.text()

        logging.debug("Deleting song: %s by %s", title, artist)

        self.controller.delete_song(title, artist)
        self.clear_inputs()
        self.clear_song_display_info()
        self.update_song_list()
        self.status_bar.showMessage(
            "Deleted %s by %s successfully" % (title, artist), 5000
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SongApp()
    window.show()
    sys.exit(app.exec())