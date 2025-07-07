from PyQt5.QtWidgets import QDockWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QTextBrowser
from PyQt5.QtCore import Qt

class HelpPanel(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("Help", parent)
        widget = QWidget()
        layout = QVBoxLayout()

        help_text = """
        <h3>How to Use the DecentSampler Visual Editor</h3>
        <ol>
            <li><b>Import your WAV files:</b> Use the "Import Samples" or "Auto-Map Folder" buttons to add your samples.</li>
            <li><b>Map each sample's keyzone:</b> Select a sample and set its Low, High, and Root notes.</li>
            <li><b>Preview the UI:</b> The preview panel shows your UI layout and mapped keys in real time.</li>
            <li><b>Save as .dspreset:</b> Use the Save function to export your DecentSampler preset.</li>
        </ol>
        <p>
            <a href="https://www.decentsamples.com/manual/">Open DecentSampler Documentation</a>
        </p>
        """

        browser = QTextBrowser()
        browser.setHtml(help_text)
        browser.setOpenExternalLinks(True)
        browser.setToolTip("Click the link to open the DecentSampler manual in your browser.")

        layout.addWidget(browser)
        widget.setLayout(layout)
        self.setWidget(widget)
        self.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
