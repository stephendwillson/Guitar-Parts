import os
import sys
import logging
import logging.handlers


def setup_logging():
    """Set up logging configuration with rotation"""
    log_dir = os.path.join(get_app_data_dir(), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "guitar_parts.log")

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.handlers.RotatingFileHandler(
                log_file,
                maxBytes=1024 * 1024,  # 1MB per file
                backupCount=3,  # Keep 3 backup files
                encoding='utf-8'
            ),
            logging.StreamHandler()
        ]
    )


def get_app_data_dir():
    """Get the application data directory following XDG spec"""
    if sys.platform == "win32":
        app_data = os.path.join(os.environ.get(
            "LOCALAPPDATA", os.path.expanduser("~")), "GuitarParts")
    else:
        app_data = os.path.join(
            os.path.expanduser("~"), ".local", "share", "guitar_parts")
    os.makedirs(app_data, exist_ok=True)
    return app_data


def get_settings_path():
    """Get the path to the settings file"""
    return os.path.join(get_app_data_dir(), "settings.env")


def get_default_db_path():
    """Get the default path for the database file"""
    return os.path.join(get_app_data_dir(), "songs.db")


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
    """Create the cache directory for album art"""
    cache_dir = os.path.join(get_app_data_dir(), "album_art_cache")
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


def save_settings(api_key, api_secret):
    """
    Save API settings to the settings file.

    Args:
        api_key (str): The Last.fm API key
        api_secret (str): The Last.fm API secret
    """
    settings_path = get_settings_path()
    with open(settings_path, 'w') as f:
        f.write(f"API_KEY={api_key}\n")
        f.write(f"API_SECRET={api_secret}\n")
