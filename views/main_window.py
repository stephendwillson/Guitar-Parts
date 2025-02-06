"""
Main application module.
"""

import sys
import os
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
    QCheckBox,
    QMessageBox,
    QComboBox,
    QSpinBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QAction

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

        self.filter_settings = {
            'artist': '',
            'title': '',
            'album': '',
            'genre': '',
            'tuning': '',
            'num_songs': 0
        }

        self.setup_ui()
        logging.debug("UI setup complete")

    def setup_ui(self):
        """
        Set up the UI.
        """
        # Create menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        # Add settings action
        settings_action = QAction('Settings', self)
        settings_action.triggered.connect(self.show_settings_dialog)
        file_menu.addAction(settings_action)

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
        self.select_songs_button.clicked.connect(self.show_select_songs_dialog)
        self.button_layout.addWidget(self.select_songs_button)

        # Add button layout to main layout
        self.main_layout.addLayout(self.button_layout)

        # Search input
        self.search_input = QLineEdit(self)
        self.search_input.setPlaceholderText("Search by Title or Artist")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.main_layout.addWidget(self.search_input)

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

        self.load_songs()

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

    def update_song_list(self, songs):
        """
        Update the song list in the UI.
        """
        self.song_tree.clear()
        for song in songs:
            item = QTreeWidgetItem(
                [titlecase(song.artist), titlecase(song.title), song.album, song.tuning]
            )
            self.song_tree.addTopLevelItem(item)
        self.song_tree.sortItems(0, Qt.SortOrder.AscendingOrder)

    def display_song_info(self, song):
        logging.debug("Displaying song info: %s by %s", song.title, song.artist)

        self.artist_label.setText(f"Artist: {titlecase(song.artist)}")
        self.title_label.setText(f"Title: {titlecase(song.title)}")
        self.album_label.setText(f"Album: {song.album}")

        if song.duration:
            try:
                minutes, seconds = divmod(int(song.duration) // 1000, 60)
                duration_str = f"{minutes:02d}:{seconds:02d}"
            except ValueError:
                duration_str = "Unknown"
        else:
            duration_str = "Unknown"

        self.duration_label.setText(f"Duration: {duration_str}")

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
            duration_str,
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

    def validate_duration(self, duration):
        """
        Validate the duration input.

        Args:
            duration (str): The duration string to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not duration:  # Allow empty duration
            return True

        # Check if it's in the format of "mm:ss" or just seconds
        if ":" in duration:
            parts = duration.split(":")
            if len(parts) != 2:
                return False
            minutes, seconds = parts
            return minutes.isdigit() and seconds.isdigit() and int(seconds) < 60
        else:
            return duration.isdigit()

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

        custom_song_checkbox = QCheckBox("Custom Song")
        layout.addWidget(custom_song_checkbox)

        # Create custom fields
        album_input = QLineEdit(dialog)
        album_input.setPlaceholderText("Album (optional)")

        duration_input = QLineEdit(dialog)
        duration_input.setPlaceholderText("Duration (optional, format: MM:SS)")

        genres_input = QLineEdit(dialog)
        genres_input.setPlaceholderText("Genres (optional, comma-separated)")

        custom_fields_layout = QVBoxLayout()
        custom_fields_layout.addWidget(album_input)
        custom_fields_layout.addWidget(duration_input)
        custom_fields_layout.addWidget(genres_input)
        custom_fields_widget = QWidget()
        custom_fields_widget.setLayout(custom_fields_layout)
        custom_fields_widget.hide()
        layout.addWidget(custom_fields_widget)

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

        def toggle_custom_fields():
            is_custom = custom_song_checkbox.isChecked()
            custom_fields_widget.setVisible(is_custom)
            dialog.adjustSize()
            logging.debug(f"Custom Song checkbox state changed. Checked: {is_custom}")
            logging.debug(
                f"Custom fields visibility: {custom_fields_widget.isVisible()}"
            )

        custom_song_checkbox.stateChanged.connect(lambda: toggle_custom_fields())

        # Log initial state
        logging.debug(
            f"Initial Custom Song checkbox state: {custom_song_checkbox.isChecked()}"
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            artist = artist_input.text().strip()
            title = title_input.text().strip()
            notes = notes_input.toPlainText().strip()
            tuning = tuning_input.text().strip()
            is_custom = custom_song_checkbox.isChecked()

            logging.debug(f"Dialog accepted. Is custom: {is_custom}")

            if artist and title:
                logging.debug(
                    f"Adding {'custom ' if is_custom else ''}song: {title} by {artist}"
                )
                if is_custom:
                    album = album_input.text().strip()
                    duration = duration_input.text().strip()
                    genres = [
                        genre.strip()
                        for genre in genres_input.text().split(",")
                        if genre.strip()
                    ]

                    # Validate duration
                    if not self.validate_duration(duration):
                        error_label.setText(
                            "Invalid duration format. Use 'mm:ss' or seconds."
                        )
                        return

                    # Convert duration to milliseconds if it's valid
                    if duration:
                        if ":" in duration:
                            minutes, seconds = map(int, duration.split(":"))
                            duration = str((minutes * 60 + seconds))
                        else:
                            duration = str(int(duration))

                    self.save_song(
                        artist, title, notes, tuning, album, duration, genres, is_custom
                    )
                else:
                    self.save_song(
                        artist, title, notes, tuning, None, None, None, is_custom
                    )
            else:
                error_label.setText("Artist and Title are required.")
                return

    def save_song(
        self,
        artist,
        title,
        notes,
        tuning,
        album=None,
        duration=None,
        genres=None,
        is_custom=False,
    ):
        """
        Save or update a song in the database.
        """
        logging.debug(
            f"Saving {'custom ' if is_custom else ''}song: {title} by {artist}"
        )
        # Check if the song already exists
        existing_song = self.controller.get_song(title, artist)

        if existing_song:
            # Update existing song
            logging.debug(f"Updating existing song: {title} by {artist}")
            existing_song.notes = notes
            existing_song.tuning = tuning
            if is_custom:
                existing_song.album = album
                existing_song.duration = duration
                existing_song.genres = genres
            success, message = self.controller.update_song_info(existing_song)
        else:
            # Create a new song object
            song = Song(
                title=title,
                artist=artist,
                tuning=tuning,
                notes=notes,
                album=album,
                duration=duration,
                genres=genres,
            )

            # Save the new song, which will fetch track info if needed
            success, message = self.controller.save_song(song, is_custom)

        if success:
            self.show_status_message(message)
            self.update_song_list(self.controller.get_all_songs())
        else:
            if "Check your spelling" in message:
                # Show a more prominent message for songs not found on Last.FM
                QMessageBox.warning(self, "Song Not Found", message)
            else:
                self.show_status_message(message, error=True)

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
                        self.update_song_list(self.controller.get_all_songs())
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
            success, message = self.controller.delete_song(title, artist)
            if success:
                self.clear_song_display_info()
                self.update_song_list(self.controller.get_all_songs())
                self.show_status_message(f"Deleted '{title}' by {artist} successfully")
            else:
                self.show_status_message(
                    f"Failed to delete song: {message}", error=True)
        except Exception as e:
            self.show_status_message(
                "Unable to delete the song. Please try again.", error=True
            )
            logging.exception(f"Error in delete_song: {str(e)}")

    def show_select_songs_dialog(self):
        logging.debug("Opening Select Songs dialog")
        songs = self.controller.get_all_songs()

        if not songs:
            self.show_status_message("No songs in the database to filter")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Select Songs")
        layout = QVBoxLayout()
        logging.debug("Select Songs button pressed")

        # Create input fields
        input_fields = {}
        for field in ['artist', 'title', 'album']:
            input_fields[field] = QLineEdit()
            input_fields[field].setText(self.filter_settings[field])
            layout.addWidget(QLabel(f"{field.capitalize()}:"))
            layout.addWidget(input_fields[field])

        # Create dropdown fields
        dropdown_fields = {}

        # Genre dropdown
        dropdown_fields['genre'] = QComboBox()
        dropdown_fields['genre'].addItem("")  # Empty option
        dropdown_fields['genre'].addItems(self.controller.get_unique_genres())
        dropdown_fields['genre'].setCurrentText(self.filter_settings['genre'])
        layout.addWidget(QLabel("Genre:"))
        layout.addWidget(dropdown_fields['genre'])

        # Tuning dropdown
        dropdown_fields['tuning'] = QComboBox()
        dropdown_fields['tuning'].addItem("")  # Empty option
        dropdown_fields['tuning'].addItems(self.controller.get_unique_tunings())
        dropdown_fields['tuning'].setCurrentText(self.filter_settings['tuning'])
        layout.addWidget(QLabel("Tuning:"))
        layout.addWidget(dropdown_fields['tuning'])

        # Number of songs input
        num_songs_label = QLabel("Number of songs (0 for all):")
        layout.addWidget(num_songs_label)
        num_songs_input = QSpinBox()
        num_songs_input.setRange(0, 1000)
        num_songs_input.setValue(self.filter_settings['num_songs'])
        layout.addWidget(num_songs_input)

        # Add summary text area
        summary_text = QTextEdit()
        summary_text.setReadOnly(True)
        layout.addWidget(QLabel("Filter Summary:"))
        layout.addWidget(summary_text)

        # Add buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        clear_button = QPushButton("Clear Filters")
        button_box.addButton(clear_button, QDialogButtonBox.ButtonRole.ResetRole)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        # Connect signals
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        def clear_filters():
            logging.debug("Clearing all filters")
            for field in input_fields.values():
                field.clear()
            for field in dropdown_fields.values():
                field.setCurrentIndex(0)
            num_songs_input.setValue(0)
            summary_text.clear()

        clear_button.clicked.connect(clear_filters)

        def update_summary():
            summary = []
            for field, input_widget in input_fields.items():
                if input_widget.text():
                    summary.append(f"{field.capitalize()}: {input_widget.text()}")
            for field, dropdown in dropdown_fields.items():
                if dropdown.currentText():
                    summary.append(f"{field.capitalize()}: {dropdown.currentText()}")
            if num_songs_input.value() > 0:
                summary.append(f"Number of songs: {num_songs_input.value()}")
            summary_text.setText("\n".join(summary))

        for input_field in input_fields.values():
            input_field.textChanged.connect(update_summary)
        for dropdown in dropdown_fields.values():
            dropdown.currentTextChanged.connect(update_summary)
        num_songs_input.valueChanged.connect(update_summary)

        # Initialize summary
        update_summary()

        # Show the dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            logging.debug("Select Songs dialog accepted")
            self.filter_settings = {
                'artist': input_fields['artist'].text(),
                'title': input_fields['title'].text(),
                'album': input_fields['album'].text(),
                'genre': dropdown_fields['genre'].currentText(),
                'tuning': dropdown_fields['tuning'].currentText(),
                'num_songs': num_songs_input.value()
            }
            filtered_songs = self.controller.filter_songs(
                artist=self.filter_settings['artist'],
                title=self.filter_settings['title'],
                album=self.filter_settings['album'],
                genre=self.filter_settings['genre'],
                tuning=self.filter_settings['tuning'],
                num_songs=self.filter_settings['num_songs']
            )
            self.update_song_list(filtered_songs)
            self.show_status_message(f"Filtered to {len(filtered_songs)} songs")
        else:
            logging.debug("Select Songs dialog cancelled")

    def show_settings_dialog(self):
        """Show settings dialog for API configuration"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Settings")
        layout = QVBoxLayout(dialog)

        # API Key input
        api_key_label = QLabel("Last.fm API Key:")
        api_key_input = QLineEdit()
        api_key_input.setText(os.getenv('API_KEY', ''))
        layout.addWidget(api_key_label)
        layout.addWidget(api_key_input)

        # API Secret input
        api_secret_label = QLabel("Last.fm API Secret:")
        api_secret_input = QLineEdit()
        api_secret_input.setText(os.getenv('API_SECRET', ''))
        layout.addWidget(api_secret_label)
        layout.addWidget(api_secret_input)

        # Info label
        info_label = QLabel("Restart application after changing API credentials")
        info_label.setStyleSheet("color: gray;")
        layout.addWidget(info_label)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                from utils.utils import save_settings
                save_settings(api_key_input.text(), api_secret_input.text())
                self.show_status_message(
                    "API settings saved. Please restart the application."
                )
            except Exception as e:
                logging.error(f"Failed to save settings: {str(e)}")
                self.show_status_message(
                    "Failed to save settings. Please check permissions.",
                    error=True
                )

    def load_songs(self):
        """
        Load songs from the database and populate the tree widget.
        """
        logging.debug("Loading songs from database")
        songs = self.controller.get_all_songs()
        self.update_song_list(songs)
        logging.debug("Songs loaded into tree view")

    def on_search_text_changed(self, text):
        """
        Handle search text changes and update the song list.
        """
        if text:
            songs = self.controller.search_songs(text)
        else:
            songs = self.controller.get_all_songs()

        self.update_song_list(songs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SongApp()
    window.show()
    sys.exit(app.exec())
