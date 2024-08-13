import os
import sys
import logging


def setup_logging():
    """
    Setup logging configuration.
    """
    return logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)-4s [%(filename)s:%(lineno)d %(funcName)s] "
        "%(message)s",
        datefmt="%Y-%m-%d:%H:%M:%S",
    )


def get_default_db_path():
    """
    Get the default path for the database file.

    Returns:
        str: The default path to the database file.
    """
    home_dir = os.path.expanduser("~")
    db_dir = os.path.join(home_dir, ".guitar_parts")
    os.makedirs(db_dir, exist_ok=True)
    return os.path.join(db_dir, "songs.db")


def get_resource_path(relative_path):
    """
    Get the absolute path to a resource file.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def create_cache_directory():
    """
    Create the cache directory for album art.

    Returns:
        str: The path to the cache directory.
    """
    db_path = get_default_db_path()
    cache_dir = os.path.join(os.path.dirname(db_path), "album_art_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir


def get_cached_album_art(album_name, cache_dir):
    """
    Get the path to the cached album art if it exists.

    Args:
        album_name (str): The name of the album.
        cache_dir (str): The directory where album art is cached.

    Returns:
        str or None: The path to the cached album art if it exists, otherwise None.
    """
    if not album_name:
        logging.info("No album name provided, skipping album art fetch.")
        return None

    album_art_path = os.path.join(cache_dir, f"{album_name}.jpg")
    return album_art_path if os.path.exists(album_art_path) else None
