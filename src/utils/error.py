from PyQt5.QtWidgets import QMessageBox
import traceback

def show_error(parent, title, msg):
    print(f"[ERROR] {title}: {msg}")
    traceback.print_exc()
    QMessageBox.critical(parent, title, msg)
