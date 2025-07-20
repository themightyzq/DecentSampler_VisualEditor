#!/usr/bin/env python3
"""
Debug why WaveformWorker sometimes returns 0 data points
"""

import sys
import os
import tempfile
import wave
import struct

# Add src to path
sys.path.insert(0, 'src')

def create_test_wav_detailed(filename, sample_rate=22050, duration=0.2):
    """Create a test WAV file with detailed logging"""
    import math
    
    frames = []
    num_samples = int(duration * sample_rate)
    
    print(f"Creating WAV: {filename}")
    print(f"  Sample rate: {sample_rate}")
    print(f"  Duration: {duration}s")
    print(f"  Total samples: {num_samples}")
    
    for i in range(num_samples):
        t = i / sample_rate
        sample = 0.7 * math.sin(2 * math.pi * 440 * t)
        sample_int = int(sample * 32767)
        frames.append(struct.pack('<h', sample_int))
    
    with wave.open(filename, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join(frames))
    
    # Verify the file
    file_size = os.path.getsize(filename)
    print(f"  File created, size: {file_size} bytes")
    
    # Read back and verify
    try:
        with wave.open(filename, 'rb') as wav_file:
            read_rate = wav_file.getframerate()
            read_channels = wav_file.getnchannels()
            read_width = wav_file.getsampwidth()
            read_frames = wav_file.getnframes()
            
            print(f"  Verification - Rate: {read_rate}, Channels: {read_channels}, Width: {read_width}, Frames: {read_frames}")
            
            if read_frames != num_samples:
                print(f"  ⚠️  Frame count mismatch: expected {num_samples}, got {read_frames}")
    except Exception as e:
        print(f"  ✗ Error verifying file: {e}")
        return None
    
    return filename

def debug_waveform_worker_detailed():
    """Debug WaveformWorker with detailed logging"""
    print("=== Detailed WaveformWorker Debug ===")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from widgets.audio_preview import WaveformWorker
        import numpy as np
        
        app = QApplication.instance()
        if not app:
            app = QApplication([])
        
        # Create test file
        temp_dir = tempfile.gettempdir()
        test_file = os.path.join(temp_dir, "detailed_test.wav")
        create_test_wav_detailed(test_file)
        
        if not test_file:
            print("Failed to create test file")
            return False
        
        # Test with different widget widths
        test_widths = [100, 200, 400, 800]
        
        for width in test_widths:
            print(f"\n--- Testing with widget width: {width} ---")
            
            # Create worker with detailed signal tracking
            worker = WaveformWorker(test_file, width)
            
            results = {
                'waveform_data': None,
                'error': None,
                'progress_updates': []
            }
            
            def capture_waveform(data):
                results['waveform_data'] = data
                print(f"  📊 Waveform data received: {len(data) if data else 0} points")
                if data and len(data) > 0:
                    print(f"     Sample data: {data[:5]}...")
                    print(f"     Max value: {max(data)}")
            
            def capture_error(error):
                results['error'] = error
                print(f"  ❌ Error received: {error}")
            
            def capture_progress(progress):
                results['progress_updates'].append(progress)
                print(f"  📈 Progress: {progress}%")
            
            # Connect signals
            worker.waveform_loaded.connect(capture_waveform)
            worker.loading_error.connect(capture_error)
            worker.loading_progress.connect(capture_progress)
            
            # Run the worker's run method directly for detailed debugging
            print(f"  🔧 Running worker.run() directly...")
            try:
                worker.run()
                print(f"  ✓ Worker.run() completed")
            except Exception as e:
                print(f"  ✗ Worker.run() failed: {e}")
                import traceback
                traceback.print_exc()
                continue
            
            # Check results
            print(f"  📋 Results summary:")
            print(f"     Progress updates: {len(results['progress_updates'])}")
            print(f"     Error: {results['error']}")
            print(f"     Waveform data: {len(results['waveform_data']) if results['waveform_data'] else 0} points")
            
            if results['error']:
                print(f"  ❌ Test failed due to error")
                return False
            
            if not results['waveform_data'] or len(results['waveform_data']) == 0:
                print(f"  ❌ Test failed - no waveform data")
                
                # Let's debug the worker's run method step by step
                print(f"  🔍 Debugging worker internals...")
                debug_worker_internals(test_file, width)
                return False
            
            print(f"  ✅ Test passed for width {width}")
        
        print(f"\n✓ All width tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Debug test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'test_file' in locals() and os.path.exists(test_file):
            os.remove(test_file)

def debug_worker_internals(file_path, widget_width):
    """Debug the worker's internal processing step by step"""
    print(f"    🔬 Internal debugging for {os.path.basename(file_path)}, width={widget_width}")
    
    try:
        import wave
        import numpy as np
        import math
        
        # Step 1: File existence
        if not os.path.exists(file_path):
            print(f"    ❌ File does not exist")
            return
        print(f"    ✓ File exists")
        
        # Step 2: File extension check
        if not file_path.lower().endswith('.wav'):
            print(f"    ⚠️  Not a WAV file")
            return
        print(f"    ✓ WAV file extension")
        
        # Step 3: Wave file opening
        try:
            with wave.open(file_path, 'rb') as wav_file:
                frames = wav_file.readframes(-1)
                sample_width = wav_file.getsampwidth()
                channels = wav_file.getnchannels()
                frame_rate = wav_file.getframerate()
                
                print(f"    ✓ WAV file opened successfully")
                print(f"      Frames length: {len(frames)} bytes")
                print(f"      Sample width: {sample_width}")
                print(f"      Channels: {channels}")
                print(f"      Frame rate: {frame_rate}")
                
        except Exception as e:
            print(f"    ❌ Error opening WAV file: {e}")
            return
        
        # Step 4: NumPy processing
        try:
            NUMPY_AVAILABLE = True
            import numpy as np
            print(f"    ✓ NumPy available")
        except ImportError:
            NUMPY_AVAILABLE = False
            print(f"    ⚠️  NumPy not available")
        
        if NUMPY_AVAILABLE:
            # Step 5: Sample conversion
            if sample_width == 2:
                samples = np.frombuffer(frames, dtype=np.int16)
                print(f"    ✓ Converted to int16 samples: {len(samples)} samples")
            elif sample_width == 3:
                print(f"    ⚠️  24-bit samples (complex conversion)")
                samples = np.frombuffer(frames, dtype=np.uint8)
                samples = samples.reshape(-1, 3)
                samples = np.array([s[0] | (s[1] << 8) | ((s[2] & 0x7F) << 16) - (0x800000 if s[2] & 0x80 else 0) for s in samples], dtype=np.int32)
                print(f"    ✓ Converted 24-bit samples: {len(samples)} samples")
            else:
                samples = np.frombuffer(frames, dtype=np.int8)
                print(f"    ✓ Converted to int8 samples: {len(samples)} samples")
            
            # Step 6: Channel processing
            if channels > 1:
                original_len = len(samples)
                samples = samples.reshape(-1, channels).mean(axis=1).astype(samples.dtype)
                print(f"    ✓ Converted to mono: {original_len} → {len(samples)} samples")
            
            # Step 7: Target points calculation
            target_points = widget_width // 4
            target_points = max(40, min(target_points, 200))
            print(f"    ✓ Target points: {target_points}")
            
            # Step 8: Chunk size calculation
            if len(samples) < target_points * 10:
                target_points = len(samples) // 10
                print(f"    ⚠️  Adjusted target points due to short sample: {target_points}")
            
            chunk_size = max(1, len(samples) // target_points)
            print(f"    ✓ Chunk size: {chunk_size}")
            
            # Step 9: Waveform generation
            waveform_data = []
            print(f"    🔄 Processing chunks...")
            
            for i in range(0, len(samples) - chunk_size, chunk_size):
                chunk = samples[i:i + chunk_size]
                if len(chunk) > 0:
                    peak = max(abs(chunk.min()), abs(chunk.max()))
                    waveform_data.append(float(peak))
            
            print(f"    ✓ Generated {len(waveform_data)} waveform points")
            
            # Step 10: Normalization
            if len(waveform_data) > 0:
                max_val = max(waveform_data) if max(waveform_data) > 0 else 1
                waveform_data = [val / max_val * 32768 for val in waveform_data]
                print(f"    ✓ Normalized waveform, max_val={max_val}")
                print(f"    ✓ Final waveform: {len(waveform_data)} points, sample: {waveform_data[:3]}...")
            else:
                print(f"    ❌ No waveform data generated!")
                
                # Debug why no data was generated
                print(f"    🔍 Debug info:")
                print(f"      len(samples): {len(samples)}")
                print(f"      target_points: {target_points}")
                print(f"      chunk_size: {chunk_size}")
                print(f"      range(0, len(samples) - chunk_size, chunk_size): {list(range(0, len(samples) - chunk_size, chunk_size))[:10]}...")
        
    except Exception as e:
        print(f"    ❌ Internal debug error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Run waveform data debugging"""
    print("DecentSampler Waveform Data Debug")
    print("=" * 40)
    
    success = debug_waveform_worker_detailed()
    
    print(f"\n=== Final Result ===")
    if success:
        print("🎉 Waveform data processing working correctly!")
    else:
        print("⚠️  Waveform data processing has issues.")

if __name__ == "__main__":
    main()