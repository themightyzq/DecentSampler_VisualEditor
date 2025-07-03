global_style = """
QWidget { font-family: Sans-Serif; font-size: 11pt; }
QDockWidget { titlebar-close-icon: url(); titlebar-normal-icon: url(); }
"""

from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QSettings
import traceback

def show_error(parent, title, msg):
    print(f"[ERROR] {title}: {msg}")
    traceback.print_exc()
    QMessageBox.critical(parent, title, msg)

def load_recent_files(settings):
    files = settings.value("recentFiles", [], type=list)
    if not isinstance(files, list):
        files = [files] if files else []
    return files

def save_recent_files(settings, files):
    settings.setValue("recentFiles", files)

def restore_window_geometry(settings, window):
    geometry = settings.value("windowGeometry")
    if geometry:
        window.restoreGeometry(geometry)
