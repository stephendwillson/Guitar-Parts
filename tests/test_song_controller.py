import pytest
from unittest.mock import patch, MagicMock
from controllers.song_controller import SongController
from models.song import Song


@pytest.fixture
def song_controller():
    with patch('controllers.song_controller.initialize_db') as mock_init_db:
        mock_init_db.return_value = (MagicMock(), MagicMock())
        return SongController()


def test_initialization(song_controller):
    assert song_controller is not None
    assert song_controller.conn is not None
    assert song_controller.cursor is not None


def test_song_exists(song_controller):
    with patch('controllers.song_controller.song_exists') as mock_song_exists:
        mock_song_exists.return_value = True
        assert song_controller.song_exists("Test Song", "Test Artist") is True
        mock_song_exists.return_value = False
        assert not song_controller.song_exists(
            "Nonexistent Song", "Unknown Artist")


def test_get_song(song_controller):
    with patch('controllers.song_controller.get_song') as mock_get_song:
        mock_song = Song("Test Song", "Test Artist")
        mock_get_song.return_value = mock_song
        result = song_controller.get_song("Test Song", "Test Artist")
        assert result == mock_song


def test_get_all_songs(song_controller):
    with patch('controllers.song_controller.load_songs') as mock_load_songs:
        mock_songs = [Song("Song1", "Artist1"), Song("Song2", "Artist2")]
        mock_load_songs.return_value = mock_songs
        result = song_controller.get_all_songs()
        assert result == mock_songs


def test_save_song(song_controller):
    with patch('controllers.song_controller.save_song') as mock_save_song, \
         patch.object(song_controller, 'song_exists') as mock_song_exists, \
         patch.object(song_controller, 'get_track_info') as mock_get_track_info:

        mock_song_exists.return_value = False
        mock_get_track_info.return_value = None

        song = Song("New Song", "New Artist")
        success, message = song_controller.save_song(song)

        assert success is True
        assert message == "Song saved successfully"
        mock_save_song.assert_called_once()


def test_delete_song(song_controller):
    with patch('controllers.song_controller.delete_song') as mock_delete_song:
        success, message = song_controller.delete_song("Test Song", "Test Artist")
        assert success is True
        assert message == "Song deleted successfully"
        mock_delete_song.assert_called_once_with(
            song_controller.cursor, "Test Song", "Test Artist"
        )


def test_update_song_info(song_controller):
    with patch('controllers.song_controller.update_song_info') as mock_update_song_info:
        song = Song("Updated Song", "Updated Artist")
        success, message = song_controller.update_song_info(song)
        assert success is True
        assert message == "Song updated successfully"
        mock_update_song_info.assert_called_once_with(song_controller.cursor, song)


def test_get_track_info(song_controller):
    with patch('controllers.song_controller.get_track_info') as mock_get_track_info:
        mock_track_info = {"track": {"name": "Test Track"}}
        mock_get_track_info.return_value = mock_track_info
        result = song_controller.get_track_info("Test Artist", "Test Track")
        assert result == mock_track_info


def test_get_cached_album_art(song_controller):
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True
        result = song_controller.get_cached_album_art("Test Album")
        assert result is not None

        mock_exists.return_value = False
        result = song_controller.get_cached_album_art("Nonexistent Album")
        assert result is None
