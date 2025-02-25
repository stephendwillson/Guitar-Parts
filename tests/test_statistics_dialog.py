import pytest
from PyQt6.QtWidgets import QDialog, QTabWidget, QHBoxLayout
from unittest.mock import MagicMock
from models.song import Song
from views.statistics_dialog import StatisticsDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt

pytest_plugins = ['pytest-qt']


@pytest.fixture
def stats_dialog(qtbot):
    """Create a StatisticsDialog instance for testing."""
    controller = MagicMock()

    # Create mock songs for testing
    mock_songs = [
        Song("Song 1", "Artist 1", tuning="Standard", genres=["Rock"],
             progress="Mastered"),
        Song("Song 2", "Artist 2", tuning="Drop D", genres=["Blues"],
             progress="Learning"),
        Song("Song 3", "Artist 3", tuning="Standard", genres=["Rock", "Metal"],
             progress="Not Started")
    ]

    # Set up mock return values with actual data
    controller.get_all_songs.return_value = mock_songs
    controller.get_progress_stats.return_value = {
        "Not Started": 1,
        "Learning": 1,
        "Mastered": 1
    }
    controller.get_progress_history.return_value = {
        "Not Started": 1,
        "Learning": 1,
        "Mastered": 1
    }
    controller.get_tuning_stats.return_value = {
        "Standard": 2,
        "Drop D": 1
    }
    controller.get_genre_stats.return_value = {
        "Rock": 2,
        "Blues": 1,
        "Metal": 1
    }

    dialog = StatisticsDialog(controller)
    qtbot.addWidget(dialog)
    return dialog


def test_dialog_creation(stats_dialog):
    """Test basic dialog creation and structure."""
    assert isinstance(stats_dialog, QDialog)

    # Verify tabs
    tab_widget = stats_dialog.findChild(QTabWidget)
    assert tab_widget is not None
    assert tab_widget.count() == 3
    assert tab_widget.tabText(0) == "Overview"
    assert tab_widget.tabText(1) == "Progress Over Time"
    assert tab_widget.tabText(2) == "Technical Analysis"


def test_progress_stats(stats_dialog):
    """Test progress statistics calculation and display."""
    mock_songs = [
        Song("Song 1", "Artist 1", progress="Mastered"),
        Song("Song 2", "Artist 2", progress="Learning"),
        Song("Song 3", "Artist 3", progress="Not Started"),
        Song("Song 4", "Artist 4", progress="Mastered")
    ]
    stats_dialog.controller.get_all_songs.return_value = mock_songs
    stats_dialog.controller.get_progress_stats.return_value = {
        "Mastered": 2,
        "Learning": 1,
        "Not Started": 1
    }

    stats = stats_dialog.controller.get_progress_stats()

    assert stats["Mastered"] == 2
    assert stats["Learning"] == 1
    assert stats["Not Started"] == 1


def test_tuning_stats(stats_dialog):
    """Test tuning statistics calculation and display."""
    mock_songs = [
        Song("Song 1", "Artist 1", tuning="Standard"),
        Song("Song 2", "Artist 2", tuning="Drop D"),
        Song("Song 3", "Artist 3", tuning="Standard")
    ]
    stats_dialog.controller.get_all_songs.return_value = mock_songs
    stats_dialog.controller.get_tuning_stats.return_value = {
        "Standard": 2,
        "Drop D": 1
    }

    stats = stats_dialog.controller.get_tuning_stats()

    assert stats["Standard"] == 2
    assert stats["Drop D"] == 1


def test_genre_stats(stats_dialog):
    """Test genre statistics calculation and display."""
    mock_songs = [
        Song("Song 1", "Artist 1", genres=["Rock", "Metal"]),
        Song("Song 2", "Artist 2", genres=["Blues"]),
        Song("Song 3", "Artist 3", genres=["Rock"])
    ]
    stats_dialog.controller.get_all_songs.return_value = mock_songs
    stats_dialog.controller.get_genre_stats.return_value = {
        "Rock": 2,
        "Metal": 1,
        "Blues": 1
    }

    stats = stats_dialog.controller.get_genre_stats()

    assert stats["Rock"] == 2
    assert stats["Metal"] == 1
    assert stats["Blues"] == 1


def test_chart_tooltips(stats_dialog):
    """Test that chart tooltips are properly configured."""
    technical_tab = stats_dialog.create_technical_tab()

    # Get the charts from the technical tab
    tuning_chart = None
    genre_chart = None
    for i in range(technical_tab.layout().count()):
        item = technical_tab.layout().itemAt(i)
        if isinstance(item, QHBoxLayout):
            for j in range(item.count()):
                widget = item.itemAt(j).widget()
                if isinstance(widget, FigureCanvasQTAgg):
                    if 'Tunings' in widget.figure.axes[0].get_title():
                        tuning_chart = widget
                    elif 'Genres' in widget.figure.axes[0].get_title():
                        genre_chart = widget

    assert tuning_chart is not None, "Tuning chart not found"
    assert genre_chart is not None, "Genre chart not found"

    # Verify tooltip annotations are properly configured
    for chart in [tuning_chart, genre_chart]:
        ax = chart.figure.axes[0]
        annotations = [child for child in ax.get_children()
                       if isinstance(child, plt.Annotation)]
        assert len(annotations) == 1, "Chart should have exactly one tooltip annotation"

        annotation = annotations[0]
        assert not annotation.get_visible(), "Tooltip should be hidden by default"
        assert annotation.get_bbox_patch().get_alpha() == 0.9, (
            "Tooltip should have proper opacity"
        )


@pytest.fixture(autouse=True)
def close_figures():
    """Automatically close matplotlib figures after each test."""
    yield
    plt.close('all')
