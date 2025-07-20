#!/usr/bin/env python3
"""
Test to isolate threading issues in waveform loading
"""

import sys
import os
import tempfile
import wave
import struct
import time

# Add src to path
sys.path.insert(0, 'src')

def create_test_wav(filename):
    """Create a minimal test WAV file"""
    import math
    
    sample_rate = 8000
    duration = 0.1
    frames = []
    num_samples = int(duration * sample_rate)
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = 0.5 * math.sin(2 * math.pi * 440 * t)
        sample_int = int(sample * 16383)
        frames.append(struct.pack('<h', sample_int))
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    return filename

def test_threading_safety():
    """Test thread safety and termination"""
    print("=== Testing Threading Safety ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from widgets.audio_preview import WaveformWidget
        import threading
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create test files
        temp_dir = tempfile.gettempdir()
        test_files = []
        for i in range(3):
            filename = os.path.join(temp_dir, f"thread_test_{i}.wav")
            create_test_wav(filename)
            test_files.append(filename)
            print(f"Created: {os.path.basename(filename)}")
        
        # Test rapid loading/cancellation
        widget = WaveformWidget()
        print("WaveformWidget created")
        
        print("\nTesting rapid load/cancel cycles...")
        
        for cycle in range(5):
            print(f"\nCycle {cycle + 1}:")
            
            # Load first file
            file1 = test_files[0]
            print(f"  Loading {os.path.basename(file1)}...")
            widget.load_waveform(file1)
            
            # Check worker state
            if hasattr(widget, 'worker') and widget.worker:
                print(f"  Worker created, running: {widget.worker.isRunning()}")
            
            # Immediately load second file (should cancel first)
            time.sleep(0.05)  # Very short delay
            file2 = test_files[1]
            print(f"  Loading {os.path.basename(file2)} (should cancel previous)...")
            
            start_time = time.time()
            widget.load_waveform(file2)
            load_time = time.time() - start_time
            
            print(f"  Load call completed in {load_time:.3f}s")
            
            if load_time > 1.0:  # If it takes more than 1 second, there's likely a blocking issue
                print(f"  ⚠️  Load call took too long! Possible blocking.")
                return False
            
            # Check final worker state
            if hasattr(widget, 'worker') and widget.worker:
                print(f"  Final worker running: {widget.worker.isRunning()}")
            
            # Process events briefly
            for _ in range(10):
                app.processEvents()
                time.sleep(0.01)
        
        print("\n✓ Threading safety test completed")
        return True
        
    except Exception as e:
        print(f"✗ Threading test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)

def test_worker_termination():
    """Test worker termination specifically"""
    print("\n=== Testing Worker Termination ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from widgets.audio_preview import WaveformWorker
        from PyQt5.QtCore import QThread
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create test file
        temp_dir = tempfile.gettempdir()
        test_file = os.path.join(temp_dir, "termination_test.wav")
        create_test_wav(test_file)
        
        print(f"Created test file: {os.path.basename(test_file)}")
        
        # Test 1: Normal worker lifecycle
        print("\n1. Testing normal worker lifecycle...")
        worker1 = WaveformWorker(test_file, 200)
        
        results = []
        def capture_result(data):
            results.append(data)
        
        worker1.waveform_loaded.connect(capture_result)
        worker1.start()
        
        # Wait for completion
        worker1.wait(5000)  # 5 second timeout
        
        if worker1.isFinished():
            print("   ✓ Worker completed normally")
            print(f"   Result: {len(results[0]) if results else 0} data points")
        else:
            print("   ✗ Worker did not complete")
            return False
        
        # Test 2: Worker termination
        print("\n2. Testing worker termination...")
        worker2 = WaveformWorker(test_file, 200)
        worker2.start()
        
        # Let it start, then terminate
        time.sleep(0.1)
        
        if worker2.isRunning():
            print("   Worker is running, attempting termination...")
            
            start_time = time.time()
            worker2.terminate()
            terminate_time = time.time() - start_time
            
            print(f"   Terminate call completed in {terminate_time:.3f}s")
            
            if terminate_time > 1.0:
                print("   ⚠️  Terminate took too long!")
                return False
            
            # Wait for termination
            start_time = time.time()
            wait_result = worker2.wait(2000)  # 2 second timeout
            wait_time = time.time() - start_time
            
            print(f"   Wait call completed in {wait_time:.3f}s, result: {wait_result}")
            
            if wait_time > 2.1:  # Slightly more than timeout
                print("   ⚠️  Wait took longer than timeout!")
                return False
            
            if wait_result:
                print("   ✓ Worker terminated successfully")
            else:
                print("   ⚠️  Worker wait timeout (but not necessarily an error)")
        else:
            print("   Worker finished too quickly to test termination")
        
        print("\n✓ Worker termination test completed")
        return True
        
    except Exception as e:
        print(f"✗ Worker termination test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'test_file' in locals() and os.path.exists(test_file):
            os.remove(test_file)

def main():
    """Run threading tests"""
    print("DecentSampler Threading Debug")
    print("=" * 35)
    
    # Test 1: Threading safety
    safety_success = test_threading_safety()
    
    # Test 2: Worker termination
    termination_success = test_worker_termination()
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Threading safety: {'✓ PASS' if safety_success else '✗ FAIL'}")
    print(f"Worker termination: {'✓ PASS' if termination_success else '✗ FAIL'}")
    
    if safety_success and termination_success:
        print("\n🎉 Threading tests passed!")
        print("The timeout issue is likely elsewhere.")
    elif not safety_success:
        print("\n⚠️  Threading safety issue detected.")
        print("The terminate()/wait() pattern may be causing blocking.")
    elif not termination_success:
        print("\n⚠️  Worker termination issue detected.")
        print("Thread cleanup may be problematic.")

if __name__ == "__main__":
    main()