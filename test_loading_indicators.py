#!/usr/bin/env python3
"""
Test script for loading indicators functionality
Tests all loading indicators integrated into the application
"""

import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt5.QtCore import QTimer

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from widgets.loading_indicators import LoadingOverlay, ProgressButton, CircularProgress, SkeletonLoader

class LoadingIndicatorTestWindow(QMainWindow):
    """Test window for all loading indicators"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Loading Indicators Test")
        self.setGeometry(100, 100, 600, 500)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Loading overlay (covers entire window)
        self.loading_overlay = LoadingOverlay(self)
        
        # Title
        title = QLabel("Loading Indicators Test Suite")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Test buttons
        overlay_btn = QPushButton("Test Loading Overlay")
        overlay_btn.clicked.connect(self.test_loading_overlay)
        layout.addWidget(overlay_btn)
        
        # Progress button
        self.progress_btn = ProgressButton("Test Progress Button")
        self.progress_btn.clicked.connect(self.test_progress_button)
        layout.addWidget(self.progress_btn)
        
        # Circular progress
        circular_layout = QVBoxLayout()
        circular_label = QLabel("Circular Progress Indicators:")
        circular_layout.addWidget(circular_label)
        
        # Determinate circular progress
        self.circular_progress = CircularProgress(64)
        circular_layout.addWidget(self.circular_progress)
        
        circular_btn = QPushButton("Test Circular Progress")
        circular_btn.clicked.connect(self.test_circular_progress)
        circular_layout.addWidget(circular_btn)
        
        layout.addLayout(circular_layout)
        
        # Skeleton loader
        skeleton_label = QLabel("Skeleton Loader:")
        layout.addWidget(skeleton_label)
        
        self.skeleton = SkeletonLoader(300, 20)
        layout.addWidget(self.skeleton)
        
        # Status
        self.status_label = QLabel("Ready to test loading indicators")
        self.status_label.setStyleSheet("margin: 10px; padding: 5px; background: #f0f0f0;")
        layout.addWidget(self.status_label)
        
        # Test integrated components button
        integrated_btn = QPushButton("Test Integrated Components")
        integrated_btn.clicked.connect(self.test_integrated_components)
        layout.addWidget(integrated_btn)
        
    def test_loading_overlay(self):
        """Test the loading overlay"""
        self.status_label.setText("Testing loading overlay...")
        self.loading_overlay.showWithText("Loading data, please wait...")
        
        # Simulate loading with timer
        QTimer.singleShot(3000, self._hide_overlay)
        
    def _hide_overlay(self):
        """Hide the loading overlay"""
        self.loading_overlay.hide()
        self.status_label.setText("Loading overlay test completed")
        
    def test_progress_button(self):
        """Test the progress button"""
        self.status_label.setText("Testing progress button...")
        self.progress_btn.setLoading(True)
        
        # Simulate progress with timer
        self.progress_value = 0
        self.progress_timer = QTimer()
        self.progress_timer.timeout.connect(self._update_progress)
        self.progress_timer.start(100)
        
    def _update_progress(self):
        """Update progress button progress"""
        self.progress_value += 5
        self.progress_btn.setProgress(self.progress_value)
        
        if self.progress_value >= 100:
            self.progress_timer.stop()
            self.status_label.setText("Progress button test completed")
            
    def test_circular_progress(self):
        """Test circular progress indicator"""
        self.status_label.setText("Testing circular progress...")
        
        # Test indeterminate mode first
        self.circular_progress.setIndeterminate(True)
        
        # Switch to determinate mode after 2 seconds
        QTimer.singleShot(2000, self._test_determinate_circular)
        
    def _test_determinate_circular(self):
        """Test determinate circular progress"""
        self.circular_progress.setIndeterminate(False)
        
        # Animate progress
        self.circular_value = 0
        self.circular_timer = QTimer()
        self.circular_timer.timeout.connect(self._update_circular)
        self.circular_timer.start(50)
        
    def _update_circular(self):
        """Update circular progress"""
        self.circular_value += 2
        self.circular_progress.setProgress(self.circular_value)
        
        if self.circular_value >= 100:
            self.circular_timer.stop()
            self.status_label.setText("Circular progress test completed")
            
    def test_integrated_components(self):
        """Test the actual integrated components"""
        self.status_label.setText("Testing integrated components...")
        
        try:
            # Import actual components to test
            from views.panels.sample_mapping_panel import SampleMappingPanel
            from widgets.audio_preview import AudioPreviewWidget
            
            self.status_label.setText("✓ All integrated components loaded successfully")
            
        except ImportError as e:
            self.status_label.setText(f"✗ Error importing components: {e}")

def main():
    """Run the loading indicators test"""
    app = QApplication(sys.argv)
    
    # Set up basic styling
    app.setStyleSheet("""
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QPushButton {
            background-color: #4a7c59;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-weight: bold;
            min-height: 32px;
        }
        QPushButton:hover {
            background-color: #5a8c69;
        }
        QPushButton:pressed {
            background-color: #3a6c49;
        }
        QLabel {
            color: #ffffff;
        }
    """)
    
    window = LoadingIndicatorTestWindow()
    window.show()
    
    print("Loading Indicators Test Suite")
    print("============================")
    print("Test each loading indicator using the buttons in the window.")
    print("Components tested:")
    print("- LoadingOverlay: Modal overlay with spinner")
    print("- ProgressButton: Button with integrated progress bar")
    print("- CircularProgress: Circular progress indicator")
    print("- SkeletonLoader: Shimmer loading placeholder")
    print("\nIntegrated into:")
    print("- Sample mapping panel (batch import, intelligent mapping)")
    print("- Audio preview widget (waveform generation)")
    print("- Main window (preset loading/saving)")
    print("- Sample browser (file operations)")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()