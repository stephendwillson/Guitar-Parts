from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTabWidget, QWidget, QGroupBox,
    QGridLayout, QLabel, QHBoxLayout
)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import logging


class StatisticsDialog(QDialog):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        logging.debug("Initializing StatisticsDialog")
        self.setWindowTitle("Practice Statistics")
        self.setMinimumSize(1200, 600)
        self.controller = controller

        # Create main layout
        layout = QVBoxLayout()

        # Create tabs
        tabs = QTabWidget()

        # Add Overview tab
        overview_tab = self.create_overview_tab()
        tabs.addTab(overview_tab, "Overview")

        # Add Progress tab
        progress_tab = self.create_progress_tab()
        tabs.addTab(progress_tab, "Progress Over Time")

        # Add Technical tab
        technical_tab = self.create_technical_tab()
        tabs.addTab(technical_tab, "Technical Analysis")

        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_overview_tab(self):
        """Create the overview tab with current statistics"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Create stats group
        stats_group = QGroupBox("Current Progress")
        stats_layout = QGridLayout()

        # Get statistics from controller
        total_songs = len(self.controller.get_all_songs())
        progress_stats = self.controller.get_progress_stats()

        # Add stats to layout
        stats_layout.addWidget(QLabel("Total Songs:"), 0, 0)
        stats_layout.addWidget(QLabel(str(total_songs)), 0, 1)

        row = 1
        for state in ["Not Started", "Learning", "Mastered"]:
            count = progress_stats.get(state, 0)
            percentage = (count / total_songs * 100) if total_songs > 0 else 0

            stats_layout.addWidget(QLabel(f"{state}:"), row, 0)
            stats_layout.addWidget(
                QLabel(f"{count} ({percentage:.1f}%)"), row, 1
            )
            row += 1

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        layout.addStretch()

        tab.setLayout(layout)
        return tab

    def create_progress_tab(self):
        """Create the progress over time tab with charts"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Get progress data
        progress_data = self.controller.get_progress_history()

        # Create figure with progress distribution pie chart
        fig, ax = plt.subplots(figsize=(8, 6))

        # Data for pie chart
        labels = list(progress_data.keys())
        sizes = list(progress_data.values())
        colors = ['#808080', '#FFA500', '#32CD32']  # Match main window colors

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90
        )

        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        plt.title('Song Progress Distribution')

        # Create canvas and add to layout
        canvas = FigureCanvasQTAgg(fig)
        layout.addWidget(canvas)

        tab.setLayout(layout)
        return tab

    def create_technical_tab(self):
        """Create the technical analysis tab with tuning and genre charts"""
        logging.debug("Creating technical analysis tab")
        tab = QWidget()
        layout = QVBoxLayout()
        charts_layout = QHBoxLayout()

        # Get statistics
        try:
            tuning_stats = self.controller.get_tuning_stats()
            genre_stats = self.controller.get_genre_stats()
            total_songs = len(self.controller.get_all_songs())
            logging.info(f"Statistics loaded: {total_songs} total songs, "
                         f"{len(tuning_stats)} tunings, {len(genre_stats)} genres")
        except Exception as e:
            logging.error(f"Failed to load statistics: {str(e)}")
            return tab

        if not tuning_stats and not genre_stats:
            logging.warning("No statistics available to display in technical tab")

        if len(genre_stats) > 10:
            logging.info(
                f"Truncating genres display from {len(genre_stats)} to 10 most common"
            )

        def create_chart(ax, labels, values, title):
            """Helper function to create a bar chart with tooltips"""
            bars = ax.bar(range(len(labels)), values)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, rotation=45, ha='right')
            ax.set_title(title)

            # Create annotation for tooltip
            annot = ax.annotate(
                "",
                xy=(0, 0),
                xytext=(0, 5),
                textcoords='offset points',
                bbox=dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9),
                visible=False,
                ha='center',
                va='bottom'
            )

            def hover(event):
                if event.inaxes == ax:
                    for i, bar in enumerate(bars):
                        cont, _ = bar.contains(event)
                        if cont:
                            percentage = (values[i] / total_songs * 100)
                            text = f"{labels[i]}\n{values[i]} songs ({percentage:.1f}%)"
                            annot.set_text(text)
                            annot.xy = (i, values[i])
                            annot.set_visible(True)
                            ax.figure.canvas.draw_idle()
                            return
                    annot.set_visible(False)
                    ax.figure.canvas.draw_idle()

            return bars, hover

        if tuning_stats:
            tuning_fig, tuning_ax = plt.subplots(figsize=(6, 4))
            tuning_labels = list(tuning_stats.keys())
            tuning_values = list(tuning_stats.values())

            _, hover_func = create_chart(tuning_ax, tuning_labels, tuning_values,
                                         'Tunings Distribution')
            tuning_fig.canvas.mpl_connect("motion_notify_event", hover_func)
            tuning_fig.tight_layout()
            tuning_canvas = FigureCanvasQTAgg(tuning_fig)
            charts_layout.addWidget(tuning_canvas)

        if genre_stats:
            genre_fig, genre_ax = plt.subplots(figsize=(6, 4))
            genre_labels = list(genre_stats.keys())[:10]
            genre_values = list(genre_stats.values())[:10]

            _, hover_func = create_chart(genre_ax, genre_labels, genre_values,
                                         'Top 10 Genres')
            genre_fig.canvas.mpl_connect("motion_notify_event", hover_func)
            genre_fig.tight_layout()
            genre_canvas = FigureCanvasQTAgg(genre_fig)
            charts_layout.addWidget(genre_canvas)

        layout.addLayout(charts_layout)

        # Add summary statistics
        stats_group = QGroupBox("Summary")
        stats_layout = QVBoxLayout()

        stats_layout.addWidget(QLabel(f"Total Songs: {total_songs}"))
        stats_layout.addWidget(QLabel(f"Unique Tunings: {len(tuning_stats)}"))
        stats_layout.addWidget(QLabel(f"Unique Genres: {len(genre_stats)}"))

        if tuning_stats:
            most_used_tuning = max(tuning_stats.items(), key=lambda x: x[1])
            stats_layout.addWidget(QLabel(
                f"Most Used Tuning: {most_used_tuning[0]} ({most_used_tuning[1]} songs)"
            ))

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        tab.setLayout(layout)
        return tab
