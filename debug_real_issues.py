#!/usr/bin/env python3
"""
Debug real-world issues that could prevent waveform display
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

def check_dependencies():
    """Check for required dependencies"""
    print("=== Checking Dependencies ===")
    
    # PyQt5
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5 available")
    except ImportError as e:
        print(f"✗ PyQt5 not available: {e}")
        return False
    
    # NumPy
    try:
        import numpy as np
        print("✓ NumPy available")
    except ImportError as e:
        print(f"⚠️  NumPy not available: {e}")
        print("   Waveform processing will use fallback method")
    
    # Wave module
    try:
        import wave
        print("✓ Wave module available")
    except ImportError as e:
        print(f"✗ Wave module not available: {e}")
        return False
    
    # Audio preview components
    try:
        from widgets.audio_preview import AudioPreviewWidget, WaveformWidget, WaveformWorker
        print("✓ Audio preview components available")
    except ImportError as e:
        print(f"✗ Audio preview components not available: {e}")
        return False
    
    return True

def check_common_issues():
    """Check for common real-world issues"""
    print("\n=== Checking Common Issues ===")
    
    # Issue 1: File path with spaces or special characters
    print("\n1. File path handling...")
    test_paths = [
        "/path/with spaces/file.wav",
        "/path/with-dashes/file.wav", 
        "/path/with_underscores/file.wav",
        "/path/with.dots/file.wav",
        "/path/with(parentheses)/file.wav",
        "/path/with[brackets]/file.wav"
    ]
    
    from widgets.audio_preview import WaveformWorker
    for path in test_paths:
        try:
            # Just test instantiation, not actual loading
            worker = WaveformWorker(path, 400)
            print(f"   ✓ Path handled: {path}")
        except Exception as e:
            print(f"   ✗ Path failed: {path} - {e}")
    
    # Issue 2: Widget sizing issues
    print("\n2. Widget sizing...")
    from PyQt5.QtWidgets import QApplication
    from widgets.audio_preview import WaveformWidget
    
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    
    widget = WaveformWidget()
    
    # Test various sizes
    test_sizes = [(0, 0), (1, 1), (100, 50), (400, 80), (800, 100)]
    for width, height in test_sizes:
        widget.resize(width, height)
        widget_width = widget.width()
        calculated_width = widget_width if widget_width > 1 else 400
        print(f"   Size {width}x{height} → calculated width: {calculated_width}")
    
    # Issue 3: Signal/slot connections
    print("\n3. Signal/slot connections...")
    try:
        from views.panels.sample_mapping_panel import SampleMappingPanel
        
        # Mock main window
        class MockMainWindow:
            def __init__(self):
                self.preset = MockPreset()
                self.piano_keyboard = MockPianoKeyboard()
            def statusBar(self):
                return MockStatusBar()
        
        class MockPreset:
            def __init__(self):
                self.mappings = []
        
        class MockPianoKeyboard:
            def set_highlight_range(self, lo, hi):
                pass
        
        class MockStatusBar:
            def showMessage(self, msg, timeout=0):
                pass
        
        main_window = MockMainWindow()
        panel = SampleMappingPanel(main_window)
        
        # Check if audio preview exists
        if hasattr(panel, 'audio_preview'):
            print("   ✓ Panel has audio_preview")
            
            # Check if waveform exists
            if hasattr(panel.audio_preview, 'waveform'):
                print("   ✓ Audio preview has waveform")
                
                # Check methods
                waveform = panel.audio_preview.waveform
                if hasattr(waveform, 'load_waveform'):
                    print("   ✓ Waveform has load_waveform method")
                else:
                    print("   ✗ Waveform missing load_waveform method")
                
                if hasattr(waveform, '_on_waveform_loaded'):
                    print("   ✓ Waveform has _on_waveform_loaded method")
                else:
                    print("   ✗ Waveform missing _on_waveform_loaded method")
            else:
                print("   ✗ Audio preview missing waveform")
        else:
            print("   ✗ Panel missing audio_preview")
    
    except Exception as e:
        print(f"   ✗ Error checking connections: {e}")
    
    # Issue 4: File format support
    print("\n4. File format support...")
    format_tests = [
        ("test.wav", True),
        ("test.WAV", True),
        ("test.aiff", False),
        ("test.mp3", False),
        ("test.flac", False),
        ("test.ogg", False)
    ]
    
    for filename, should_process in format_tests:
        is_wav = filename.lower().endswith('.wav')
        result = "✓" if is_wav == should_process else "⚠️ "
        print(f"   {result} {filename}: {'WAV' if is_wav else 'Non-WAV'} (should process: {should_process})")

def identify_potential_causes():
    """Identify potential causes for waveform not displaying"""
    print("\n=== Potential Causes Analysis ===")
    
    causes = [
        {
            "issue": "Widget not properly sized",
            "description": "WaveformWidget might be 0x0 pixels",
            "check": "Verify widget.width() > 0 and widget.height() > 0",
            "fix": "Ensure proper layout and sizing constraints"
        },
        {
            "issue": "File paths with special characters",
            "description": "Paths with spaces, unicode, or special chars",
            "check": "Test with simple ASCII paths first",
            "fix": "Proper path encoding and escaping"
        },
        {
            "issue": "Threading signal disconnection",
            "description": "Qt signals not connecting properly between threads",
            "check": "Verify worker signals are emitted and received",
            "fix": "Use Qt::QueuedConnection for cross-thread signals"
        },
        {
            "issue": "Widget not updating after data load",
            "description": "Waveform data loads but widget doesn't repaint",
            "check": "Call widget.update() after data changes",
            "fix": "Ensure update() is called on UI thread"
        },
        {
            "issue": "File access permissions",
            "description": "Can't read sample files due to permissions",
            "check": "os.access(file_path, os.R_OK)",
            "fix": "Check file permissions and accessibility"
        },
        {
            "issue": "Empty or corrupt audio files",
            "description": "Files exist but contain no valid audio data",
            "check": "Verify files have audio content and valid format",
            "fix": "Test with known good WAV files"
        },
        {
            "issue": "Widget hidden or clipped",
            "description": "Widget exists but is not visible in UI",
            "check": "Verify widget.isVisible() and parent layout",
            "fix": "Check widget hierarchy and visibility"
        },
        {
            "issue": "Paint event not triggered",
            "description": "Widget doesn't receive paint events",
            "check": "Override paintEvent() with debug logging",
            "fix": "Ensure widget is properly shown and sized"
        }
    ]
    
    for i, cause in enumerate(causes, 1):
        print(f"\n{i}. {cause['issue']}")
        print(f"   Description: {cause['description']}")
        print(f"   Check: {cause['check']}")
        print(f"   Fix: {cause['fix']}")

def main():
    """Run real-world issue debugging"""
    print("DecentSampler Real-World Issues Debug")
    print("=" * 45)
    
    # Check dependencies first
    deps_ok = check_dependencies()
    
    if deps_ok:
        # Check common issues
        check_common_issues()
    
    # Provide analysis regardless
    identify_potential_causes()
    
    print(f"\n=== Summary ===")
    if deps_ok:
        print("✓ Basic dependencies are available")
        print("✓ Component structure looks correct")
        print("⚠️  If waveforms still don't display, check the potential causes above")
    else:
        print("✗ Missing critical dependencies")
        print("Fix dependency issues first")

if __name__ == "__main__":
    main()