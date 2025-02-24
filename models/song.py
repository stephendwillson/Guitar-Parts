"""
Song module.
"""


class Song:
    """
    Class to represent a song.
    """

    PROGRESS_STATES = ["Not Started", "Learning", "Mastered"]

    def __init__(
        self,
        title,
        artist,
        tuning=None,
        notes=None,
        album=None,
        duration=None,
        genres="",
        progress="Not Started",
    ):
        """
        Initialize a Song object.

        Args:
            title (str): The title of the song.
            artist (str): The artist of the song.
            tuning (str, optional): The tuning of the song.
            notes (str, optional): Notes about the song.
            album (str, optional): The album of the song.
            duration (str, optional): The duration of the song.
            genres (list, optional): The genres of the song.
            progress (str, optional): Learning progress of the song.
                                    One of: "Not Started", "Learning", "Mastered"
        """
        self.title = title
        self.artist = artist
        self.tuning = tuning
        self.notes = notes
        self.album = album
        self.duration = duration
        self.genres = genres if genres is not None else []
        if progress not in self.PROGRESS_STATES:
            progress = "Not Started"
        self.progress = progress

    def __repr__(self):
        """
        Return a string representation of the Song object.

        Returns:
            str: String representation of the Song object.
        """
        return (
            f"Song(title={self.title}, artist={self.artist}, tuning={self.tuning}, "
            f"notes={self.notes}, album={self.album}, duration={self.duration}, "
            f"genres={self.genres}, progress={self.progress})"
        )
