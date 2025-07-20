#!/usr/bin/env python3
"""
Test that mimics the real application workflow:
1. Create a main window mock
2. Create sample mappings
3. Select samples in the table
4. Verify waveform updates
"""

import sys
import os
import tempfile
import wave
import struct

# Add src to path
sys.path.insert(0, 'src')

def create_test_wav(filename, frequency=440, duration=0.2):
    """Create a test WAV file"""
    import math
    
    sample_rate = 22050  # Lower sample rate for faster processing
    frames = []
    num_samples = int(duration * sample_rate)
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = 0.6 * math.sin(2 * math.pi * frequency * t)
        sample_int = int(sample * 32767)
        frames.append(struct.pack('<h', sample_int))
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    return filename

def test_real_workflow():
    """Test the exact workflow that happens in the real application"""
    print("=== Testing Real Application Workflow ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import QTimer, QEventLoop
        from views.panels.sample_mapping_panel import SampleMappingPanel
        from model import SampleMapping
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create test files
        temp_dir = tempfile.gettempdir()
        test_files = []
        frequencies = [220, 440, 880]  # Different frequencies for testing
        
        for i, freq in enumerate(frequencies):
            filename = os.path.join(temp_dir, f"sample_{freq}hz.wav")
            create_test_wav(filename, frequency=freq, duration=0.15)
            test_files.append(filename)
            print(f"Created: {os.path.basename(filename)} ({freq}Hz)")
        
        # Create realistic main window mock
        class MockMainWindow:
            def __init__(self):
                self.preset = MockPreset()
                self.piano_keyboard = MockPianoKeyboard()
                self._status_messages = []
                
            def statusBar(self):
                return MockStatusBar(self)
        
        class MockPreset:
            def __init__(self):
                self.mappings = []
        
        class MockPianoKeyboard:
            def set_highlight_range(self, lo, hi):
                print(f"   → Piano keyboard highlight: notes {lo}-{hi}")
        
        class MockStatusBar:
            def __init__(self, main_window):
                self.main_window = main_window
            
            def showMessage(self, msg, timeout=0):
                self.main_window._status_messages.append(msg)
                print(f"   → Status: {msg}")
        
        # Create the panel exactly as the real app does
        main_window = MockMainWindow()
        panel = SampleMappingPanel(main_window)
        
        print(f"\n1. Created SampleMappingPanel")
        print(f"   Audio preview widget: {hasattr(panel, 'audio_preview')}")
        print(f"   Table widget: {hasattr(panel, 'table_widget')}")
        
        # Create sample mappings
        mappings = []
        for i, file_path in enumerate(test_files):
            # Use different MIDI ranges for each sample
            lo_note = 60 + i * 5  # C4, F4, A4
            hi_note = lo_note + 4
            root_note = lo_note + 2
            
            mapping = SampleMapping(file_path, lo_note, hi_note, root_note)
            mappings.append(mapping)
            print(f"   Mapping {i}: {os.path.basename(file_path)} → notes {lo_note}-{hi_note}")
        
        # Add samples to panel (this is what happens when user imports files)
        print(f"\n2. Setting samples in panel...")
        panel.set_samples(mappings)
        
        table_rows = panel.table_widget.rowCount()
        print(f"   Table populated with {table_rows} rows")
        
        if table_rows != len(mappings):
            print(f"   ✗ Row count mismatch!")
            return False
        
        # Test each sample selection (this is what happens when user clicks table row)
        print(f"\n3. Testing sample selection...")
        
        for i in range(len(mappings)):
            print(f"\n   === Testing Sample {i+1} ===")
            expected_file = test_files[i]
            print(f"   Expected file: {os.path.basename(expected_file)}")
            
            # Simulate user clicking table row
            panel.table_widget.selectRow(i)
            print(f"   ✓ Row {i} selected")
            
            # Get current selection
            indexes = panel.table_widget.selectionModel().selectedRows()
            if not indexes:
                print(f"   ✗ No selection detected")
                continue
            
            idx = indexes[0].row()
            print(f"   ✓ Selection index: {idx}")
            
            # This is the exact code from on_table_selection_changed
            if idx < 0 or idx >= len(panel.samples):
                print(f"   ✗ Invalid index range")
                continue
            
            mapping = panel.samples[idx]
            print(f"   ✓ Got mapping object")
            
            # Set mapping (this updates the zone panel)
            panel.set_mapping(mapping)
            print(f"   ✓ Mapping set in panel")
            
            # Get file path (exact code from the method)
            if isinstance(mapping, dict):
                file_path = mapping.get("path", "")
            else:
                file_path = getattr(mapping, "path", "")
            
            print(f"   File path from mapping: {os.path.basename(file_path) if file_path else 'None'}")
            
            # Check file existence (exact code from the method)
            if file_path and os.path.exists(file_path):
                print(f"   ✓ File exists and is accessible")
                
                # This is the critical call that should load the waveform
                print(f"   → Calling audio_preview.load_file()...")
                panel.audio_preview.load_file(file_path)
                
                # Check immediate state
                if hasattr(panel.audio_preview, 'current_file'):
                    current = panel.audio_preview.current_file
                    if current == file_path:
                        print(f"   ✓ AudioPreview current_file set correctly")
                    else:
                        print(f"   ✗ AudioPreview current_file mismatch: {os.path.basename(current) if current else 'None'}")
                
                # Check waveform widget
                if hasattr(panel.audio_preview, 'waveform'):
                    waveform_widget = panel.audio_preview.waveform
                    print(f"   ✓ Waveform widget accessible")
                    
                    # Check immediate loading state
                    if hasattr(waveform_widget, 'is_loading'):
                        print(f"   Loading state: {waveform_widget.is_loading}")
                    
                    # Wait for async loading to complete
                    print(f"   Waiting for waveform loading...")
                    
                    max_wait_time = 3.0  # 3 seconds
                    wait_interval = 0.1
                    wait_cycles = int(max_wait_time / wait_interval)
                    
                    for cycle in range(wait_cycles):
                        app.processEvents()  # Process Qt events
                        
                        if hasattr(waveform_widget, 'waveform_data') and waveform_widget.waveform_data:
                            wait_time = cycle * wait_interval
                            data_points = len(waveform_widget.waveform_data)
                            print(f"   ✓ Waveform loaded after {wait_time:.1f}s: {data_points} points")
                            
                            # Verify data quality
                            if data_points > 0:
                                max_val = max(waveform_widget.waveform_data)
                                print(f"   ✓ Waveform data quality: max={max_val:.1f}")
                                break
                            else:
                                print(f"   ✗ Empty waveform data")
                                break
                        
                        if cycle % 10 == 0:  # Every second
                            print(f"   ... waiting {cycle * wait_interval:.1f}s")
                        
                        import time
                        time.sleep(wait_interval)
                    else:
                        # Timeout reached
                        print(f"   ✗ Waveform loading timeout after {max_wait_time}s")
                        
                        # Debug info
                        if hasattr(waveform_widget, 'is_loading'):
                            print(f"   Debug: is_loading = {waveform_widget.is_loading}")
                        if hasattr(waveform_widget, 'worker') and waveform_widget.worker:
                            print(f"   Debug: worker running = {waveform_widget.worker.isRunning()}")
                            print(f"   Debug: worker finished = {waveform_widget.worker.isFinished()}")
                        if hasattr(waveform_widget, 'waveform_data'):
                            data_len = len(waveform_widget.waveform_data) if waveform_widget.waveform_data else 0
                            print(f"   Debug: waveform_data length = {data_len}")
                else:
                    print(f"   ✗ AudioPreview missing waveform widget")
            else:
                print(f"   ✗ File does not exist: {file_path}")
                panel.audio_preview._clear()
        
        print(f"\n4. Workflow test completed")
        return True
        
    except Exception as e:
        print(f"✗ Error in workflow test: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)

def main():
    """Run the real workflow test"""
    print("DecentSampler Real Workflow Test")
    print("=" * 40)
    
    success = test_real_workflow()
    
    print(f"\n=== Final Result ===")
    if success:
        print("🎉 Workflow test completed!")
        print("If waveforms aren't displaying in the real app, the issue may be:")
        print("- File path problems")
        print("- UI update/repaint issues") 
        print("- Real sample files vs test files")
        print("- Threading synchronization in complex UI")
    else:
        print("⚠️  Workflow test found issues.")
        print("Check the error messages above.")

if __name__ == "__main__":
    main()