from unittest.mock import patch, Mock
from datetime import timedelta
import os
import sys


# I don't know why this is required here but not in test_db.py.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../api")))

from api.lastfm_api import (  # noqa: E402 - Import not at top of file
    get_track_info,
    get_album_name,
    get_track_duration,
    get_genre,
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


@patch("lastfm_api.requests.get")
def test_get_track_info(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = mock_track_info
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    track_info = get_track_info("Test Artist", "Test Track")
    assert track_info["track"]["name"] == "Test Track"
    assert track_info["album_art_url"] == "large.jpg"


@patch("lastfm_api.requests.get")
def test_get_album_name(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = mock_track_info
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    album_name = get_album_name("Test Artist", "Test Track")
    assert album_name == "Test Album"


@patch("lastfm_api.requests.get")
def test_get_track_duration(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = mock_track_info
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    duration = get_track_duration("Test Artist", "Test Track")
    assert duration == timedelta(milliseconds=300000)


@patch("lastfm_api.requests.get")
def test_get_genre(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = mock_track_info
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    genres = get_genre("Test Artist", "Test Track")
    assert genres == ["Rock", "Alternative"]
