from PyQt5.QtCore import QSettings

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
