import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt, QSettings
from views.windows.main_window import MainWindow
from utils.theme_manager import theme_manager
from utils.error_handling import DependencyChecker

def check_first_run_dependencies(app):
    """Check dependencies on first run and show message if needed"""
    settings = QSettings()
    first_run = settings.value("first_run", True, type=bool)
    
    if first_run:
        # Check dependencies
        status = DependencyChecker.get_all_dependencies_status()
        missing_deps = [dep for dep, (available, _) in status.items() if not available]
        
        if missing_deps:
            message = DependencyChecker.get_missing_dependencies_message()
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Optional Dependencies")
            msg_box.setText("Welcome to DecentSampler Frontend!\n\nSome optional features require additional packages:")
            msg_box.setDetailedText(message)
            msg_box.exec_()
        
        # Mark as not first run
        settings.setValue("first_run", False)

def main():
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("DecentSampler Frontend")
    app.setOrganizationName("DecentSamples")
    
    # Apply the centralized theme
    theme_manager.initialize(app)
    
    # Check dependencies on first run
    check_first_run_dependencies(app)
    
    window = MainWindow()
    window.showMaximized()  # Start maximized as per the UI analysis
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
