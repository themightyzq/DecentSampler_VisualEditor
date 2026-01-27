"""
Welcome Overlay Widget for DecentSampler Editor
Shows on first launch with drag-drop zone and quick-start actions.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont, QPainter, QColor, QPen
from utils.theme_manager import ThemeColors, ThemeSpacing
import os


class WelcomeOverlay(QWidget):
    """Full-page welcome overlay shown when no preset is loaded."""

    importFolderClicked = pyqtSignal()
    openPresetClicked = pyqtSignal()
    filesDropped = pyqtSignal(list)  # list of file paths

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(ThemeSpacing.SPACING_XLARGE)
        layout.setContentsMargins(60, 40, 60, 40)

        # Title
        title = QLabel("DecentSampler Preset Editor")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {ThemeColors.TEXT_PRIMARY};
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }}
        """)
        layout.addWidget(title)

        subtitle = QLabel("Create sample instruments in under 2 minutes")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"""
            QLabel {{
                color: {ThemeColors.TEXT_SECONDARY};
                font-size: 14px;
                background: transparent;
            }}
        """)
        layout.addWidget(subtitle)

        layout.addSpacing(16)

        # Drag-drop zone
        self.drop_zone = DropZoneWidget()
        self.drop_zone.filesDropped.connect(self.filesDropped.emit)
        layout.addWidget(self.drop_zone, 1)

        layout.addSpacing(8)

        # Action buttons row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(ThemeSpacing.SPACING_LARGE)
        btn_layout.setAlignment(Qt.AlignCenter)

        import_btn = QPushButton("Import Sample Folder")
        import_btn.setProperty("primary", True)
        import_btn.setCursor(Qt.PointingHandCursor)
        import_btn.setMinimumSize(200, 40)
        import_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.ACCENT};
                color: {ThemeColors.TEXT_PRIMARY};
                border: none;
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {ThemeColors.ACCENT_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {ThemeColors.ACCENT_PRESSED};
            }}
        """)
        import_btn.clicked.connect(self.importFolderClicked.emit)
        btn_layout.addWidget(import_btn)

        open_btn = QPushButton("Open Existing Preset")
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setMinimumSize(200, 40)
        open_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {ThemeColors.PANEL_BG};
                color: {ThemeColors.TEXT_PRIMARY};
                border: 1px solid {ThemeColors.BORDER};
                border-radius: 6px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background-color: {ThemeColors.HOVER_BG};
                border-color: {ThemeColors.ACCENT};
            }}
        """)
        open_btn.clicked.connect(self.openPresetClicked.emit)
        btn_layout.addWidget(open_btn)

        layout.addLayout(btn_layout)

        layout.addSpacing(16)

        # 3-step workflow visual
        steps_layout = QHBoxLayout()
        steps_layout.setAlignment(Qt.AlignCenter)
        steps_layout.setSpacing(8)

        steps = [
            ("1", "Import", "Drop or select sample files"),
            ("2", "Map", "Assign samples to keyboard keys"),
            ("3", "Export", "Save as .dspreset file"),
        ]

        for i, (num, label, desc) in enumerate(steps):
            step_widget = self._create_step_widget(num, label, desc)
            steps_layout.addWidget(step_widget)
            if i < len(steps) - 1:
                arrow = QLabel("\u2192")  # right arrow
                arrow.setAlignment(Qt.AlignCenter)
                arrow.setStyleSheet(f"""
                    QLabel {{
                        color: {ThemeColors.TEXT_DISABLED};
                        font-size: 20px;
                        background: transparent;
                        padding: 0 8px;
                    }}
                """)
                steps_layout.addWidget(arrow)

        layout.addLayout(steps_layout)

    def _create_step_widget(self, number, label, description):
        widget = QWidget()
        widget.setFixedWidth(200)
        widget.setStyleSheet("background: transparent;")
        v = QVBoxLayout(widget)
        v.setAlignment(Qt.AlignCenter)
        v.setSpacing(4)
        v.setContentsMargins(0, 0, 0, 0)

        num_label = QLabel(number)
        num_label.setAlignment(Qt.AlignCenter)
        num_label.setFixedSize(32, 32)
        num_label.setStyleSheet(f"""
            QLabel {{
                background-color: {ThemeColors.ACCENT};
                color: {ThemeColors.TEXT_PRIMARY};
                border-radius: 16px;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        v.addWidget(num_label, 0, Qt.AlignCenter)

        title = QLabel(label)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"""
            QLabel {{
                color: {ThemeColors.TEXT_PRIMARY};
                font-size: 13px;
                font-weight: 600;
                background: transparent;
            }}
        """)
        v.addWidget(title)

        desc = QLabel(description)
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet(f"""
            QLabel {{
                color: {ThemeColors.TEXT_SECONDARY};
                font-size: 11px;
                background: transparent;
            }}
        """)
        v.addWidget(desc)

        return widget

    # Forward drag-drop events to drop zone
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.drop_zone.setHighlighted(True)

    def dragLeaveEvent(self, event):
        self.drop_zone.setHighlighted(False)

    def dropEvent(self, event: QDropEvent):
        self.drop_zone.setHighlighted(False)
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.exists(path):
                    paths.append(path)
            if paths:
                self.filesDropped.emit(paths)
                event.acceptProposedAction()


class DropZoneWidget(QFrame):
    """Dashed-border drop zone with visual feedback."""

    filesDropped = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._highlighted = False
        self.setMinimumHeight(140)
        self.setMaximumHeight(200)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._update_style()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(8)

        icon_label = QLabel("\U0001F4C2")  # folder emoji
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 36px; background: transparent;")
        layout.addWidget(icon_label)

        text = QLabel("Drop a folder of samples here")
        text.setAlignment(Qt.AlignCenter)
        text.setStyleSheet(f"""
            QLabel {{
                color: {ThemeColors.TEXT_SECONDARY};
                font-size: 15px;
                font-weight: 500;
                background: transparent;
            }}
        """)
        layout.addWidget(text)

        hint = QLabel("WAV, AIFF, FLAC, OGG supported")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"""
            QLabel {{
                color: {ThemeColors.TEXT_DISABLED};
                font-size: 11px;
                background: transparent;
            }}
        """)
        layout.addWidget(hint)

    def setHighlighted(self, highlighted):
        self._highlighted = highlighted
        self._update_style()

    def _update_style(self):
        if self._highlighted:
            border_color = ThemeColors.ACCENT
            bg = ThemeColors.SECONDARY_BG
        else:
            border_color = ThemeColors.BORDER_HOVER
            bg = ThemeColors.PANEL_BG
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                border: 2px dashed {border_color};
                border-radius: 12px;
            }}
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setHighlighted(True)

    def dragLeaveEvent(self, event):
        self.setHighlighted(False)

    def dropEvent(self, event):
        self.setHighlighted(False)
        if event.mimeData().hasUrls():
            paths = []
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.exists(path):
                    paths.append(path)
            if paths:
                self.filesDropped.emit(paths)
                event.acceptProposedAction()
