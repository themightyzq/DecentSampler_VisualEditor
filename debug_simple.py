#!/usr/bin/env python3
"""
Simple focused test to identify waveform display issues
"""

import sys
import os
import tempfile
import wave
import struct
import time

# Add src to path
sys.path.insert(0, 'src')

def create_simple_wav(filename):
    """Create a minimal test WAV file"""
    import math
    
    sample_rate = 8000  # Lower sample rate for faster processing
    duration = 0.1  # Very short
    frames = []
    num_samples = int(duration * sample_rate)
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = 0.5 * math.sin(2 * math.pi * 440 * t)
        sample_int = int(sample * 16383)  # Lower amplitude
        frames.append(struct.pack('<h', sample_int))
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    return filename

def test_waveform_worker_sync():
    """Test WaveformWorker synchronously"""
    print("=== Testing WaveformWorker Synchronously ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from widgets.audio_preview import WaveformWorker
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create test file
        temp_dir = tempfile.gettempdir()
        test_file = os.path.join(temp_dir, "sync_test.wav")
        create_simple_wav(test_file)
        
        print(f"Created test file: {test_file}")
        print(f"File size: {os.path.getsize(test_file)} bytes")
        
        # Test the worker's run method directly (synchronous)
        worker = WaveformWorker(test_file, 200)
        
        # Collect results
        waveform_data = None
        error_message = None
        
        def capture_data(data):
            nonlocal waveform_data
            waveform_data = data
        
        def capture_error(error):
            nonlocal error_message
            error_message = error
        
        worker.waveform_loaded.connect(capture_data)
        worker.loading_error.connect(capture_error)
        
        print("Running worker synchronously...")
        worker.run()  # Call run() directly instead of start()
        
        # Check results
        if error_message:
            print(f"✗ Error: {error_message}")
            return False
        
        if waveform_data is None:
            print("✗ No data received")
            return False
        
        if len(waveform_data) == 0:
            print("✗ Empty waveform data")
            return False
        
        print(f"✓ Success: {len(waveform_data)} data points")
        print(f"   Sample data: {waveform_data[:5]}...")
        print(f"   Max value: {max(waveform_data) if waveform_data else 0}")
        
        return True
        
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'test_file' in locals() and os.path.exists(test_file):
            os.remove(test_file)

def test_audio_preview_direct():
    """Test AudioPreviewWidget load_file method step by step"""
    print("\n=== Testing AudioPreviewWidget Step by Step ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from widgets.audio_preview import AudioPreviewWidget
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create test file
        temp_dir = tempfile.gettempdir()
        test_file = os.path.join(temp_dir, "preview_test.wav")
        create_simple_wav(test_file)
        
        print(f"Created test file: {test_file}")
        
        # Create widget
        widget = AudioPreviewWidget()
        print("✓ AudioPreviewWidget created")
        
        # Check structure
        if not hasattr(widget, 'waveform'):
            print("✗ Widget missing 'waveform' attribute")
            return False
        
        print("✓ Widget has waveform sub-widget")
        
        # Check waveform widget structure
        waveform = widget.waveform
        if not hasattr(waveform, 'load_waveform'):
            print("✗ Waveform widget missing 'load_waveform' method")
            return False
        
        print("✓ Waveform widget has load_waveform method")
        
        # Test load_file method step by step
        print("\nCalling load_file...")
        widget.load_file(test_file)
        
        # Check if current_file was set
        if hasattr(widget, 'current_file'):
            if widget.current_file == test_file:
                print("✓ current_file set correctly")
            else:
                print(f"✗ current_file wrong: {widget.current_file}")
        else:
            print("? current_file attribute not found")
        
        # Check if waveform loading started
        if hasattr(waveform, 'is_loading'):
            print(f"Waveform loading state: {waveform.is_loading}")
        
        if hasattr(waveform, 'worker'):
            if waveform.worker:
                print(f"Worker exists: {type(waveform.worker)}")
                print(f"Worker running: {waveform.worker.isRunning()}")
            else:
                print("No worker created")
        
        # Wait a moment for async operations
        print("Waiting for async operations...")
        for i in range(30):  # 3 seconds max
            app.processEvents()
            time.sleep(0.1)
            
            if hasattr(waveform, 'waveform_data') and waveform.waveform_data:
                print(f"✓ Waveform data loaded after {i/10:.1f}s: {len(waveform.waveform_data)} points")
                return True
        
        # Final check
        if hasattr(waveform, 'waveform_data'):
            if waveform.waveform_data:
                print(f"✓ Final check - waveform data: {len(waveform.waveform_data)} points")
                return True
            else:
                print("✗ No waveform data after waiting")
                
                # Debug info
                if hasattr(waveform, 'is_loading'):
                    print(f"   is_loading: {waveform.is_loading}")
                if hasattr(waveform, 'worker') and waveform.worker:
                    print(f"   worker finished: {waveform.worker.isFinished()}")
                    print(f"   worker running: {waveform.worker.isRunning()}")
                
                return False
        else:
            print("✗ Waveform widget has no waveform_data attribute")
            return False
        
    except Exception as e:
        print(f"✗ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'test_file' in locals() and os.path.exists(test_file):
            os.remove(test_file)

def main():
    """Run simple debugging tests"""
    print("DecentSampler Waveform Simple Debug")
    print("=" * 40)
    
    # Test 1: Worker synchronously
    worker_success = test_waveform_worker_sync()
    
    # Test 2: AudioPreview step by step
    preview_success = test_audio_preview_direct()
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"WaveformWorker sync test: {'✓ PASS' if worker_success else '✗ FAIL'}")
    print(f"AudioPreview direct test: {'✓ PASS' if preview_success else '✗ FAIL'}")
    
    if worker_success and preview_success:
        print("\n🎉 Basic functionality working!")
    elif worker_success and not preview_success:
        print("\n⚠️  Worker OK, but async loading or widget integration issue.")
    elif not worker_success:
        print("\n⚠️  Core waveform processing issue.")

if __name__ == "__main__":
    main()