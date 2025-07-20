#!/usr/bin/env python3
"""
Integration test for sample selection -> waveform display pipeline
This specifically tests the data flow when selecting samples in the mapping panel
"""

import sys
import os
import tempfile
import wave
import struct

# Add src to path
sys.path.insert(0, 'src')

def create_test_wav_file(filename, frequency=440, duration=0.5):
    """Create a test WAV file with a specific frequency"""
    import math
    
    sample_rate = 44100
    frames = []
    num_samples = int(duration * sample_rate)
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = 0.7 * math.sin(2 * math.pi * frequency * t)
        sample_int = int(sample * 32767)
        frames.append(struct.pack('<h', sample_int))
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    return filename

def test_sample_selection_waveform_integration():
    """Test the complete integration from sample selection to waveform display"""
    print("=== Testing Sample Selection -> Waveform Integration ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from views.panels.sample_mapping_panel import SampleMappingPanel
        from model import SampleMapping
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create test files
        temp_dir = tempfile.gettempdir()
        test_files = []
        for i, freq in enumerate([440, 880, 220]):  # A4, A5, A3
            filename = os.path.join(temp_dir, f"test_sample_{i}_{freq}hz.wav")
            create_test_wav_file(filename, frequency=freq, duration=0.3)
            test_files.append(filename)
            print(f"Created test file: {os.path.basename(filename)}")
        
        # Mock main window with proper attributes
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
                print(f"Piano keyboard highlight set: {lo}-{hi}")
        
        class MockStatusBar:
            def showMessage(self, msg, timeout=0):
                print(f"Status: {msg}")
        
        main_window = MockMainWindow()
        panel = SampleMappingPanel(main_window)
        
        print("\n1. SampleMappingPanel created")
        
        # Create sample mappings
        mappings = []
        for i, file_path in enumerate(test_files):
            mapping = SampleMapping(file_path, 60 + i * 12, 70 + i * 12, 65 + i * 12)
            mappings.append(mapping)
        
        print(f"2. Created {len(mappings)} sample mappings")
        
        # Set samples in panel
        panel.set_samples(mappings)
        print("3. Set samples in panel")
        
        # Verify table population
        table_rows = panel.table_widget.rowCount()
        print(f"4. Table has {table_rows} rows")
        
        if table_rows != len(mappings):
            print(f"✗ Row count mismatch: expected {len(mappings)}, got {table_rows}")
            return False
        
        # Test sample selection
        print("\n5. Testing sample selection...")
        
        for i in range(len(mappings)):
            print(f"\n   Testing selection of sample {i}...")
            
            # Select row
            panel.table_widget.selectRow(i)
            
            # Trigger selection change manually
            selection_model = panel.table_widget.selectionModel()
            selected = selection_model.selection()
            deselected = selection_model.selection()  # Empty for this test
            panel.on_table_selection_changed(selected, deselected)
            
            # Check if mapping is set
            if panel.current_mapping is not None:
                print(f"   ✓ Current mapping set")
                
                # Check file path
                if isinstance(panel.current_mapping, dict):
                    current_path = panel.current_mapping.get("path", "")
                else:
                    current_path = getattr(panel.current_mapping, "path", "")
                
                expected_path = test_files[i]
                if current_path == expected_path:
                    print(f"   ✓ Correct file path: {os.path.basename(current_path)}")
                else:
                    print(f"   ✗ Wrong file path: expected {os.path.basename(expected_path)}, got {os.path.basename(current_path)}")
                
                # Check if audio preview received the file
                if hasattr(panel, 'audio_preview'):
                    if hasattr(panel.audio_preview, 'current_file'):
                        preview_file = panel.audio_preview.current_file
                        if preview_file == expected_path:
                            print(f"   ✓ Audio preview file set correctly")
                        else:
                            print(f"   ✗ Audio preview file wrong: expected {os.path.basename(expected_path)}, got {os.path.basename(preview_file) if preview_file else 'None'}")
                    else:
                        print(f"   ? Audio preview doesn't have current_file attribute")
                    
                    # Check waveform data
                    if hasattr(panel.audio_preview, 'waveform'):
                        waveform_widget = panel.audio_preview.waveform
                        
                        # Give some time for async loading
                        from PyQt5.QtCore import QEventLoop, QTimer
                        loop = QEventLoop()
                        timer = QTimer()
                        timer.timeout.connect(loop.quit)
                        timer.start(1000)  # 1 second
                        loop.exec_()
                        
                        if hasattr(waveform_widget, 'waveform_data') and waveform_widget.waveform_data:
                            data_points = len(waveform_widget.waveform_data)
                            print(f"   ✓ Waveform data loaded: {data_points} points")
                        else:
                            print(f"   ✗ No waveform data loaded")
                            
                            # Debug: Check if loading is in progress
                            if hasattr(waveform_widget, 'is_loading'):
                                print(f"   Debug: is_loading = {waveform_widget.is_loading}")
                            if hasattr(waveform_widget, 'worker'):
                                print(f"   Debug: worker exists = {waveform_widget.worker is not None}")
                                if waveform_widget.worker:
                                    print(f"   Debug: worker running = {waveform_widget.worker.isRunning()}")
                    else:
                        print(f"   ✗ Audio preview missing waveform widget")
                else:
                    print(f"   ✗ Panel missing audio_preview widget")
            else:
                print(f"   ✗ No current mapping set")
        
        print("\n6. Integration test completed")
        return True
        
    except Exception as e:
        print(f"✗ Error in integration test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test files
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)

def test_direct_waveform_loading():
    """Test direct waveform loading to isolate issues"""
    print("\n=== Testing Direct Waveform Loading ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from widgets.audio_preview import AudioPreviewWidget
        from PyQt5.QtCore import QEventLoop, QTimer
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create test file
        temp_dir = tempfile.gettempdir()
        test_file = os.path.join(temp_dir, "direct_test.wav")
        create_test_wav_file(test_file, frequency=1000, duration=0.2)
        
        print(f"Created test file: {test_file}")
        
        # Test direct loading
        widget = AudioPreviewWidget()
        print("AudioPreviewWidget created")
        
        # Monitor waveform loading
        waveform_loaded = False
        error_occurred = False
        
        def on_waveform_loaded(data):
            nonlocal waveform_loaded
            waveform_loaded = True
            print(f"Waveform loaded callback: {len(data) if data else 0} points")
        
        def on_loading_error(error):
            nonlocal error_occurred
            error_occurred = True
            print(f"Waveform error callback: {error}")
        
        # Connect to the waveform widget's signals
        if hasattr(widget, 'waveform'):
            widget.waveform.waveform_loaded = on_waveform_loaded
            # Note: The WaveformWorker signals aren't directly accessible, 
            # so we'll check the final state
        
        # Load the file
        widget.load_file(test_file)
        print("load_file() called")
        
        # Wait for loading to complete
        loop = QEventLoop()
        timer = QTimer()
        timer.timeout.connect(loop.quit)
        timer.start(3000)  # 3 second timeout
        loop.exec_()
        
        # Check final state
        if hasattr(widget, 'waveform') and hasattr(widget.waveform, 'waveform_data'):
            data = widget.waveform.waveform_data
            if data and len(data) > 0:
                print(f"✓ Direct waveform loading successful: {len(data)} points")
                print(f"   Max amplitude: {max(data)}")
                print(f"   Sample values: {data[:5]}...")
                return True
            else:
                print(f"✗ Direct waveform loading failed: no data")
                
                # Debug information
                print(f"   is_loading: {getattr(widget.waveform, 'is_loading', 'N/A')}")
                if hasattr(widget.waveform, 'worker') and widget.waveform.worker:
                    print(f"   worker finished: {widget.waveform.worker.isFinished()}")
                    print(f"   worker running: {widget.waveform.worker.isRunning()}")
                
                return False
        else:
            print("✗ Widget structure incorrect")
            return False
            
    except Exception as e:
        print(f"✗ Error in direct loading test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'test_file' in locals() and os.path.exists(test_file):
            os.remove(test_file)

def main():
    """Run integration debugging"""
    print("DecentSampler Waveform Integration Debug")
    print("=" * 50)
    
    # Test 1: Direct waveform loading
    direct_success = test_direct_waveform_loading()
    
    # Test 2: Full integration
    integration_success = test_sample_selection_waveform_integration()
    
    # Summary
    print(f"\n=== Summary ===")
    print(f"Direct waveform loading: {'✓ PASS' if direct_success else '✗ FAIL'}")
    print(f"Sample selection integration: {'✓ PASS' if integration_success else '✗ FAIL'}")
    
    if direct_success and integration_success:
        print("\n🎉 Integration working correctly!")
    elif direct_success and not integration_success:
        print("\n⚠️  Waveform loading works, but integration has issues.")
        print("Check the sample selection -> waveform display pipeline.")
    elif not direct_success:
        print("\n⚠️  Basic waveform loading has issues.")
        print("Check file loading and WaveformWorker implementation.")
    else:
        print("\n⚠️  Multiple issues detected.")

if __name__ == "__main__":
    main()