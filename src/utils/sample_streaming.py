"""
Sample Streaming Manager for Memory-Efficient Audio Handling
Implements on-demand loading and intelligent caching for large sample libraries
"""

import os
import wave
import threading
from collections import OrderedDict
from typing import Optional, Tuple, Dict, Any
import weakref
from utils.error_handling import ErrorHandler, with_error_handling

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

class SampleMetadata:
    """Lightweight metadata for a sample without loading audio data"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.file_size = os.path.getsize(file_path)
        self.sample_rate = None
        self.channels = None
        self.duration = None
        self.format_info = None
        self.error_handler = ErrorHandler()
        self._load_metadata()
    
    def _load_metadata(self):
        """Load only metadata without audio data"""
        try:
            with wave.open(self.file_path, 'rb') as wav:
                self.sample_rate = wav.getframerate()
                self.channels = wav.getnchannels()
                self.frames = wav.getnframes()
                self.sample_width = wav.getsampwidth()
                self.duration = self.frames / self.sample_rate
                self.format_info = f"{self.sample_rate}Hz {self.sample_width*8}bit {self.channels}ch"
        except Exception as e:
            # Metadata errors are not critical - just log them
            self.error_handler.handle_error(
                e,
                f"loading metadata for {os.path.basename(self.file_path)}",
                show_dialog=False
            )

class StreamingSampleCache:
    """LRU cache for loaded sample data"""
    
    def __init__(self, max_memory_mb: int = 512):
        self.max_memory = max_memory_mb * 1024 * 1024  # Convert to bytes
        self.cache = OrderedDict()
        self.current_memory = 0
        self.lock = threading.Lock()
        self.access_count = {}
        
    def get(self, file_path: str) -> Optional[np.ndarray]:
        """Get sample from cache, updating LRU order"""
        with self.lock:
            if file_path in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(file_path)
                self.access_count[file_path] = self.access_count.get(file_path, 0) + 1
                return self.cache[file_path]
            return None
    
    def put(self, file_path: str, data: np.ndarray, size: int):
        """Add sample to cache, evicting old samples if necessary"""
        with self.lock:
            # Remove if already exists
            if file_path in self.cache:
                self.current_memory -= self._get_size(file_path)
                del self.cache[file_path]
            
            # Evict samples if necessary
            while self.current_memory + size > self.max_memory and self.cache:
                # Find least frequently used sample that hasn't been accessed recently
                evict_key = self._find_eviction_candidate()
                if evict_key:
                    evicted_size = self._get_size(evict_key)
                    self.current_memory -= evicted_size
                    del self.cache[evict_key]
                    if evict_key in self.access_count:
                        del self.access_count[evict_key]
            
            # Add new sample
            self.cache[file_path] = data
            self.current_memory += size
            self.access_count[file_path] = 1
    
    def _find_eviction_candidate(self) -> Optional[str]:
        """Find best candidate for eviction using frequency and recency"""
        if not self.cache:
            return None
            
        # Get samples ordered by recency (first = least recent)
        candidates = list(self.cache.keys())
        
        # Score each candidate (lower = better candidate for eviction)
        scores = {}
        for i, key in enumerate(candidates):
            recency_score = i / len(candidates)  # 0 = least recent, 1 = most recent
            frequency = self.access_count.get(key, 1)
            frequency_score = min(frequency / 10, 1.0)  # Cap at 10 accesses
            
            # Combined score (lower = better eviction candidate)
            scores[key] = recency_score * 0.7 + frequency_score * 0.3
        
        # Return candidate with lowest score
        return min(scores, key=scores.get)
    
    def _get_size(self, file_path: str) -> int:
        """Get size of cached sample"""
        if file_path in self.cache:
            return self.cache[file_path].nbytes if hasattr(self.cache[file_path], 'nbytes') else 0
        return 0
    
    def clear(self):
        """Clear entire cache"""
        with self.lock:
            self.cache.clear()
            self.current_memory = 0
            self.access_count.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            return {
                'cached_samples': len(self.cache),
                'memory_used_mb': self.current_memory / (1024 * 1024),
                'memory_limit_mb': self.max_memory / (1024 * 1024),
                'hit_rate': sum(self.access_count.values()) / max(len(self.access_count), 1)
            }

class SampleStreamingManager:
    """Manages sample streaming with metadata indexing and intelligent caching"""
    
    def __init__(self, cache_size_mb: int = 512):
        self.metadata_index = {}  # file_path -> SampleMetadata
        self.cache = StreamingSampleCache(cache_size_mb)
        self.loading_threads = {}  # file_path -> Thread
        self.load_callbacks = {}  # file_path -> [callbacks]
        self.preload_queue = []
        self.error_handler = ErrorHandler()
        self._init_preload_thread()
    
    def _init_preload_thread(self):
        """Initialize background preloading thread"""
        self.preload_thread = threading.Thread(target=self._preload_worker, daemon=True)
        self.preload_thread.start()
    
    def index_sample(self, file_path: str) -> SampleMetadata:
        """Index a sample file, loading only metadata"""
        if file_path not in self.metadata_index:
            self.metadata_index[file_path] = SampleMetadata(file_path)
        return self.metadata_index[file_path]
    
    def index_directory(self, directory: str, progress_callback=None):
        """Index all samples in a directory"""
        audio_extensions = {'.wav', '.aiff', '.aif', '.flac'}
        total_files = 0
        indexed_files = 0
        
        # Count total files first
        for root, dirs, files in os.walk(directory):
            for file in files:
                if os.path.splitext(file)[1].lower() in audio_extensions:
                    total_files += 1
        
        # Index files
        for root, dirs, files in os.walk(directory):
            for file in files:
                if os.path.splitext(file)[1].lower() in audio_extensions:
                    file_path = os.path.join(root, file)
                    self.index_sample(file_path)
                    indexed_files += 1
                    
                    if progress_callback:
                        progress = (indexed_files / total_files) * 100
                        progress_callback(progress, f"Indexing: {file}")
    
    def get_sample_async(self, file_path: str, callback, priority: int = 0):
        """Load sample asynchronously with callback"""
        # Check cache first
        cached_data = self.cache.get(file_path)
        if cached_data is not None:
            callback(file_path, cached_data)
            return
        
        # Add to callback list
        if file_path not in self.load_callbacks:
            self.load_callbacks[file_path] = []
        self.load_callbacks[file_path].append(callback)
        
        # Start loading if not already in progress
        if file_path not in self.loading_threads:
            thread = threading.Thread(
                target=self._load_sample_thread,
                args=(file_path, priority)
            )
            self.loading_threads[file_path] = thread
            thread.start()
    
    def get_sample_sync(self, file_path: str) -> Optional[np.ndarray]:
        """Load sample synchronously (blocks until loaded)"""
        # Check cache first
        cached_data = self.cache.get(file_path)
        if cached_data is not None:
            return cached_data
        
        # Load synchronously
        return self._load_sample_data(file_path)
    
    def _load_sample_thread(self, file_path: str, priority: int):
        """Background thread for loading sample"""
        try:
            # Load the sample
            data = self._load_sample_data(file_path)
            
            if data is not None:
                # Cache it
                size = data.nbytes if hasattr(data, 'nbytes') else 0
                self.cache.put(file_path, data, size)
                
                # Call all callbacks
                callbacks = self.load_callbacks.get(file_path, [])
                for callback in callbacks:
                    try:
                        callback(file_path, data)
                    except Exception as e:
                        self.error_handler.handle_error(
                            e,
                            "executing sample load callback",
                            show_dialog=False
                        )
            
            # Cleanup
            if file_path in self.load_callbacks:
                del self.load_callbacks[file_path]
            if file_path in self.loading_threads:
                del self.loading_threads[file_path]
                
        except Exception as e:
            self.error_handler.handle_error(
                e,
                f"loading sample {os.path.basename(file_path)}",
                show_dialog=False
            )
            # Call callbacks with None to indicate error
            callbacks = self.load_callbacks.get(file_path, [])
            for callback in callbacks:
                try:
                    callback(file_path, None)
                except:
                    pass
    
    def _load_sample_data(self, file_path: str) -> Optional[np.ndarray]:
        """Load actual sample data from file"""
        try:
            if not os.path.exists(file_path):
                return None
            
            with wave.open(file_path, 'rb') as wav:
                frames = wav.readframes(-1)
                
                if NUMPY_AVAILABLE:
                    # Convert to numpy array based on sample width
                    sample_width = wav.getsampwidth()
                    if sample_width == 2:
                        data = np.frombuffer(frames, dtype=np.int16)
                    elif sample_width == 3:
                        # 24-bit audio
                        data = np.frombuffer(frames, dtype=np.uint8)
                        data = data.reshape(-1, 3)
                        # Convert 24-bit to 32-bit
                        data = np.array([
                            s[0] | (s[1] << 8) | ((s[2] & 0x7F) << 16) - (0x800000 if s[2] & 0x80 else 0) 
                            for s in data
                        ], dtype=np.int32)
                    else:
                        data = np.frombuffer(frames, dtype=np.int8)
                    
                    # Handle multi-channel
                    channels = wav.getnchannels()
                    if channels > 1:
                        data = data.reshape(-1, channels)
                    
                    return data
                else:
                    # Return raw frames if numpy not available
                    # Log once that numpy would improve performance
                    if not hasattr(self, '_numpy_warning_shown'):
                        self._numpy_warning_shown = True
                        self.error_handler.handle_error(
                            ImportError("numpy not available"),
                            "processing audio data (install numpy for better performance)",
                            show_dialog=False
                        )
                    return frames
                    
        except Exception as e:
            self.error_handler.handle_error(
                e,
                f"loading sample data from {os.path.basename(file_path)}",
                show_dialog=False
            )
            return None
    
    def preload_samples(self, file_paths: list, priority: int = 1):
        """Queue samples for preloading in background"""
        for file_path in file_paths:
            if file_path not in self.preload_queue:
                self.preload_queue.append((priority, file_path))
        
        # Sort by priority (higher priority first)
        self.preload_queue.sort(key=lambda x: -x[0])
    
    def _preload_worker(self):
        """Background worker for preloading samples"""
        while True:
            if self.preload_queue:
                priority, file_path = self.preload_queue.pop(0)
                
                # Check if already cached
                if self.cache.get(file_path) is None:
                    # Load the sample
                    data = self._load_sample_data(file_path)
                    if data is not None:
                        size = data.nbytes if hasattr(data, 'nbytes') else 0
                        self.cache.put(file_path, data, size)
            else:
                # Sleep when queue is empty
                threading.Event().wait(0.1)
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics"""
        stats = self.cache.get_stats()
        stats['indexed_samples'] = len(self.metadata_index)
        stats['loading_queue'] = len(self.loading_threads)
        stats['preload_queue'] = len(self.preload_queue)
        return stats
    
    def optimize_cache_for_range(self, start_note: int, end_note: int, mappings: list):
        """Optimize cache for a specific note range"""
        # Find all samples that might be needed for this range
        relevant_samples = []
        
        for mapping in mappings:
            lo = getattr(mapping, 'lo', getattr(mapping, 'loNote', 0))
            hi = getattr(mapping, 'hi', getattr(mapping, 'hiNote', 127))
            path = getattr(mapping, 'path', '')
            
            # Check if mapping overlaps with range
            if lo <= end_note and hi >= start_note and path:
                relevant_samples.append(path)
        
        # Preload relevant samples
        self.preload_samples(relevant_samples, priority=5)
    
    def clear_cache(self):
        """Clear the sample cache"""
        self.cache.clear()
    
    def close(self):
        """Clean up resources"""
        self.clear_cache()
        self.metadata_index.clear()

# Global instance for the application
_streaming_manager = None

def get_streaming_manager(cache_size_mb: int = 512) -> SampleStreamingManager:
    """Get or create the global streaming manager instance"""
    global _streaming_manager
    if _streaming_manager is None:
        _streaming_manager = SampleStreamingManager(cache_size_mb)
    return _streaming_manager