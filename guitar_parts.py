"""
Entry point for application
"""

import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import SongApp

__version__ = "1.2.0"


def main():
    """Run the thing"""

    # Create app instance
    app = QApplication(sys.argv)

    # Create and show the main window
    window = SongApp()
    window.show()

    # Run the app
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
