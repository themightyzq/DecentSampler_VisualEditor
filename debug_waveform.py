#!/usr/bin/env python3
"""
Debug script to analyze waveform display issues
This script tests the complete waveform pipeline from file selection to visual display
"""

import sys
import os
import tempfile
import wave
import struct

# Add src to path
sys.path.insert(0, 'src')

def create_test_wav_file(filename, duration=1.0, sample_rate=44100):
    """Create a test WAV file with a simple waveform"""
    import math
    
    # Generate a sine wave
    frames = []
    num_samples = int(duration * sample_rate)
    
    for i in range(num_samples):
        # Create a sine wave with some variation
        t = i / sample_rate
        # Mix of sine waves for interesting waveform
        sample = (
            0.5 * math.sin(2 * math.pi * 440 * t) +  # A4 note
            0.3 * math.sin(2 * math.pi * 880 * t) +  # A5 note
            0.2 * math.sin(2 * math.pi * 220 * t)    # A3 note
        )
        
        # Convert to 16-bit integer
        sample_int = int(sample * 32767)
        frames.append(struct.pack('<h', sample_int))
    
    # Write WAV file
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    print(f"Created test WAV file: {filename}")
    print(f"Duration: {duration}s, Sample rate: {sample_rate}Hz")

def test_waveform_loading(test_file):
    """Test the complete waveform loading pipeline"""
    print(f"\n=== Testing Waveform Loading Pipeline ===")
    print(f"Test file: {test_file}")
    
    try:
        # Test 1: Basic file validation
        print("\n1. File validation...")
        if not os.path.exists(test_file):
            print(f"✗ File does not exist: {test_file}")
            return False
        
        file_size = os.path.getsize(test_file)
        print(f"✓ File exists, size: {file_size} bytes")
        
        # Test 2: Wave file reading
        print("\n2. Wave file metadata...")
        try:
            with wave.open(test_file, 'rb') as wav_file:
                sample_rate = wav_file.getframerate()
                channels = wav_file.getnchannels()
                frames = wav_file.getnframes()
                sample_width = wav_file.getsampwidth()
                duration = frames / sample_rate
                
                print(f"✓ Sample rate: {sample_rate}Hz")
                print(f"✓ Channels: {channels}")
                print(f"✓ Sample width: {sample_width} bytes")
                print(f"✓ Total frames: {frames}")
                print(f"✓ Duration: {duration:.2f}s")
        except Exception as e:
            print(f"✗ Error reading WAV metadata: {e}")
            return False
        
        # Test 3: WaveformWorker processing
        print("\n3. WaveformWorker processing...")
        from widgets.audio_preview import WaveformWorker
        from PyQt5.QtCore import QEventLoop
        from PyQt5.QtWidgets import QApplication
        
        # Create Qt application if needed
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create worker and capture results
        worker = WaveformWorker(test_file, 400)  # 400px widget width
        waveform_data = None
        error_message = None
        
        def on_waveform_loaded(data):
            nonlocal waveform_data
            waveform_data = data
            print(f"✓ Waveform loaded, {len(data)} data points")
        
        def on_loading_error(error):
            nonlocal error_message
            error_message = error
            print(f"✗ Loading error: {error}")
        
        # Connect signals
        worker.waveform_loaded.connect(on_waveform_loaded)
        worker.loading_error.connect(on_loading_error)
        
        # Run worker
        worker.start()
        
        # Wait for completion
        loop = QEventLoop()
        worker.finished.connect(loop.quit)
        loop.exec_()
        
        if error_message:
            print(f"✗ WaveformWorker failed: {error_message}")
            return False
        
        if not waveform_data:
            print("✗ No waveform data received")
            return False
        
        print(f"✓ WaveformWorker completed successfully")
        print(f"  Data points: {len(waveform_data)}")
        print(f"  Max amplitude: {max(waveform_data) if waveform_data else 0}")
        print(f"  Sample values: {waveform_data[:10]}...")
        
        # Test 4: WaveformWidget integration
        print("\n4. WaveformWidget integration...")
        from widgets.audio_preview import WaveformWidget
        
        widget = WaveformWidget()
        print("✓ WaveformWidget created")
        
        # Simulate loading
        widget.load_waveform(test_file)
        print("✓ load_waveform() called")
        
        # Check if data gets set
        loop2 = QEventLoop()
        
        def check_widget_data():
            if hasattr(widget, 'waveform_data') and widget.waveform_data:
                print(f"✓ Widget has waveform data: {len(widget.waveform_data)} points")
                return True
            else:
                print("? Widget waveform data not yet available")
                return False
        
        # Wait a bit for async loading
        from PyQt5.QtCore import QTimer
        timer = QTimer()
        timer.timeout.connect(loop2.quit)
        timer.start(2000)  # 2 second timeout
        loop2.exec_()
        
        final_result = check_widget_data()
        
        # Test 5: AudioPreviewWidget integration
        print("\n5. AudioPreviewWidget integration...")
        from widgets.audio_preview import AudioPreviewWidget
        
        preview_widget = AudioPreviewWidget()
        print("✓ AudioPreviewWidget created")
        
        preview_widget.load_file(test_file)
        print("✓ load_file() called")
        
        # Check waveform widget
        if hasattr(preview_widget, 'waveform'):
            print("✓ AudioPreviewWidget has waveform sub-widget")
            
            # Wait for loading
            timer2 = QTimer()
            timer2.timeout.connect(loop2.quit)
            timer2.start(2000)
            loop2.exec_()
            
            if hasattr(preview_widget.waveform, 'waveform_data') and preview_widget.waveform.waveform_data:
                print(f"✓ AudioPreviewWidget waveform loaded: {len(preview_widget.waveform.waveform_data)} points")
            else:
                print("✗ AudioPreviewWidget waveform data not loaded")
        else:
            print("✗ AudioPreviewWidget missing waveform sub-widget")
        
        return final_result
        
    except Exception as e:
        print(f"✗ Unexpected error in pipeline test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_file_path_handling():
    """Test file path handling in sample mapping"""
    print(f"\n=== Testing File Path Handling ===")
    
    try:
        from views.panels.sample_mapping_panel import SampleMappingPanel
        from PyQt5.QtWidgets import QApplication
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Mock main window
        class MockMainWindow:
            def __init__(self):
                self.preset = None
                self.statusBar = lambda: MockStatusBar()
        
        class MockStatusBar:
            def showMessage(self, msg, timeout=0):
                print(f"Status: {msg}")
        
        main_window = MockMainWindow()
        panel = SampleMappingPanel(main_window)
        
        print("✓ SampleMappingPanel created")
        
        # Test audio preview widget
        if hasattr(panel, 'audio_preview'):
            print("✓ Panel has audio_preview widget")
            
            # Check if it has the right methods
            if hasattr(panel.audio_preview, 'load_file'):
                print("✓ audio_preview has load_file method")
            else:
                print("✗ audio_preview missing load_file method")
            
            if hasattr(panel.audio_preview, 'waveform'):
                print("✓ audio_preview has waveform sub-widget")
                
                if hasattr(panel.audio_preview.waveform, 'load_waveform'):
                    print("✓ waveform has load_waveform method")
                else:
                    print("✗ waveform missing load_waveform method")
            else:
                print("✗ audio_preview missing waveform sub-widget")
        else:
            print("✗ Panel missing audio_preview widget")
        
        return True
        
    except Exception as e:
        print(f"✗ Error in file path handling test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the complete waveform debugging suite"""
    print("DecentSampler Waveform Debug Tool")
    print("=" * 50)
    
    # Create a temporary test file
    temp_dir = tempfile.gettempdir()
    test_file = os.path.join(temp_dir, "waveform_test.wav")
    
    try:
        # Create test WAV file
        create_test_wav_file(test_file)
        
        # Run tests
        pipeline_success = test_waveform_loading(test_file)
        path_handling_success = test_file_path_handling()
        
        # Summary
        print(f"\n=== Summary ===")
        print(f"Waveform pipeline test: {'✓ PASS' if pipeline_success else '✗ FAIL'}")
        print(f"File path handling test: {'✓ PASS' if path_handling_success else '✗ FAIL'}")
        
        if pipeline_success and path_handling_success:
            print("\n🎉 All tests passed! Waveform display should be working.")
        else:
            print("\n⚠️  Some tests failed. Check the issues above.")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"\nCleaned up test file: {test_file}")

if __name__ == "__main__":
    main()