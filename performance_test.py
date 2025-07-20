#!/usr/bin/env python3
"""
Performance test script for the optimized piano keyboard widget.
This demonstrates the performance improvements made to reduce full repaints on hover events.
"""

import sys
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer, pyqtSignal
from PyQt5.QtGui import QPaintEvent, QResizeEvent

# Import the optimized piano keyboard
sys.path.append('src')
try:
    from panels.piano_keyboard import PianoKeyboardWidget
    from utils.accessibility import accessibility_settings
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running this from the DecentSampler_FrontEnd directory")
    sys.exit(1)

class PerformanceTestWindow(QMainWindow):
    """Test window to measure piano keyboard performance"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Piano Keyboard Performance Test")
        self.setGeometry(100, 100, 1200, 300)
        
        # Performance counters
        self.paint_count = 0
        self.last_paint_time = time.time()
        self.paint_times = []
        
        self.init_ui()
        self.setup_test_timer()
    
    def init_ui(self):
        """Initialize the UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Performance info label
        self.perf_label = QLabel("Performance Monitor: Starting test...")
        layout.addWidget(self.perf_label)
        
        # Create piano keyboard with some test mappings
        self.piano_keyboard = TestPianoKeyboard()
        layout.addWidget(self.piano_keyboard)
        
        # Instructions
        instructions = QLabel(
            "Instructions:\n"
            "• Move your mouse over the piano keys to test hover performance\n"
            "• The optimizations should result in minimal full repaints\n"
            "• Only the hovered key regions should update\n"
            "• Background elements are cached and not redrawn on hover"
        )
        layout.addWidget(instructions)
    
    def setup_test_timer(self):
        """Setup timer to update performance stats"""
        self.perf_timer = QTimer()
        self.perf_timer.timeout.connect(self.update_performance_stats)
        self.perf_timer.start(1000)  # Update every second
    
    def update_performance_stats(self):
        """Update performance statistics"""
        current_time = time.time()
        elapsed = current_time - self.last_paint_time
        
        if elapsed > 0:
            fps = len(self.paint_times) / max(elapsed, 1)
            avg_paint_time = sum(self.paint_times) / max(len(self.paint_times), 1) if self.paint_times else 0
            
            self.perf_label.setText(
                f"Performance Stats - "
                f"Paints: {self.paint_count} | "
                f"FPS: {fps:.1f} | "
                f"Avg Paint Time: {avg_paint_time*1000:.2f}ms | "
                f"Cache Valid: {self.piano_keyboard.cached_background_valid}"
            )
        
        # Reset counters
        self.paint_times.clear()

class TestPianoKeyboard(PianoKeyboardWidget):
    """Enhanced piano keyboard for performance testing"""
    
    def __init__(self):
        super().__init__()
        self.setup_test_mappings()
        
        # Performance tracking
        self.parent_window = None
    
    def setup_test_mappings(self):
        """Setup some test sample mappings"""
        # Create mock mappings for testing
        self.test_mappings = [
            {'lo': 36, 'hi': 48, 'root': 42, 'path': 'test_sample1.wav'},
            {'lo': 49, 'hi': 60, 'root': 54, 'path': 'test_sample2.wav'},
            {'lo': 61, 'hi': 72, 'root': 66, 'path': 'test_sample3.wav'},
            {'lo': 73, 'hi': 84, 'root': 78, 'path': 'test_sample4.wav'},
        ]
    
    def _get_sample_mappings(self):
        """Override to return test mappings"""
        return self.test_mappings
    
    def paintEvent(self, event):
        """Override to track paint performance"""
        start_time = time.time()
        
        # Call the optimized paint event
        super().paintEvent(event)
        
        # Track performance
        paint_time = time.time() - start_time
        
        # Find parent window and update stats
        parent = self.parent()
        while parent and not isinstance(parent, PerformanceTestWindow):
            parent = parent.parent()
        
        if parent:
            parent.paint_count += 1
            parent.paint_times.append(paint_time)
            
            # Print detailed info for region updates
            update_rect = event.rect()
            if update_rect.width() < self.width() or update_rect.height() < self.height():
                print(f"Partial update: {update_rect.width()}x{update_rect.height()} "
                      f"at ({update_rect.x()}, {update_rect.y()}) - "
                      f"Paint time: {paint_time*1000:.2f}ms")

def main():
    """Main function to run the performance test"""
    app = QApplication(sys.argv)
    
    # Setup accessibility for testing
    accessibility_settings.colorblind_mode = False
    
    window = PerformanceTestWindow()
    window.show()
    
    print("Piano Keyboard Performance Test")
    print("=" * 50)
    print("Optimizations implemented:")
    print("• Dirty region tracking - only repaints changed areas")
    print("• Static background caching - background elements cached")
    print("• Hover event throttling - reduces update frequency")
    print("• Regional updates - only affected key regions updated")
    print("• Optimized paint operations - expensive operations cached")
    print()
    print("Move your mouse over the piano keys and observe the performance stats.")
    print("Regional updates should be much smaller than full widget size.")
    print()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()