import os
import sys
from unittest.mock import patch, Mock, mock_open
from datetime import timedelta

# Make sure project root dir is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.lastfm_api import (  # noqa: E402 - Import not at top of file
    get_track_info,
    get_album_name,
    get_track_duration,
    get_genre,
    fetch_and_cache_album_art,
)

# Sample mock data for API responses
mock_track_info = {
    "track": {
        "name": "Test Track",
        "artist": {"name": "Test Artist"},
        "album": {
            "title": "Test Album",
            "image": [
                {"#text": "small.jpg"},
                {"#text": "medium.jpg"},
                {"#text": "large.jpg"},
            ],
        },
        "duration": "300000",
        "toptags": {
            "tag": [
                {"name": "Rock"},
                {"name": "Alternative"},
            ]
        },
    }
}


@patch("services.lastfm_api.requests.get")
def test_get_track_info(mock_get):
    """
    Test fetching track info from Last.fm API.
    """
    mock_response = Mock()
    mock_response.json.return_value = mock_track_info
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    track_info = get_track_info("Test Artist", "Test Track")
    assert track_info["track"]["name"] == "Test Track"
    assert track_info["track"]["album"]["title"] == "Test Album"
    assert track_info["album_art_url"] == "large.jpg"


@patch("services.lastfm_api.requests.get")
def test_get_album_name(mock_get):
    """
    Test fetching album name from Last.fm API.
    """
    mock_response = Mock()
    mock_response.json.return_value = mock_track_info
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    album_name = get_album_name("Test Artist", "Test Track")
    assert album_name == "Test Album"


@patch("services.lastfm_api.requests.get")
def test_get_track_duration(mock_get):
    """
    Test fetching track duration from Last.fm API.
    """
    mock_response = Mock()
    mock_response.json.return_value = mock_track_info
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    duration = get_track_duration("Test Artist", "Test Track")
    assert duration == timedelta(milliseconds=300000)


@patch("services.lastfm_api.requests.get")
def test_get_genre(mock_get):
    """
    Test fetching genre(s) from Last.fm API.
    """
    mock_response = Mock()
    mock_response.json.return_value = mock_track_info
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    genres = get_genre("Test Artist", "Test Track")
    assert genres == ["Rock", "Alternative"]


@patch("services.lastfm_api.requests.get")
def test_fetch_and_cache_album_art(mock_get):
    """
    Test fetching a track's album art from Last.fm API.
    """
    mock_response = Mock()
    mock_response.content = b"fake_image_data"
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    cache_dir = "/tmp"
    album_art_url = "http://example.com/fake_image.jpg"
    album_name = "Test Album"

    with patch("builtins.open", mock_open()) as mock_file:
        album_art_path = fetch_and_cache_album_art(album_art_url, album_name, cache_dir)
        mock_file.assert_called_once_with(
            os.path.join(cache_dir, f"{album_name}.jpg"), "wb"
        )
        mock_file().write.assert_called_once_with(b"fake_image_data")
        assert album_art_path == os.path.join(cache_dir, f"{album_name}.jpg")
