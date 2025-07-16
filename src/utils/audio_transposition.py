"""
Audio Transposition System for DecentSampler Frontend
Handles pitch shifting and sample playback with proper transposition
"""

import math
import os
import tempfile
from typing import Optional, Tuple
from PyQt5.QtMultimedia import QSound, QMediaPlayer, QMediaContent
from PyQt5.QtCore import QUrl, QTimer, QObject, pyqtSignal

try:
    import librosa
    import soundfile as sf
    import numpy as np
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.playback import play
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False

class TranspositionEngine(QObject):
    """
    Handles sample transposition and playback for the piano keyboard
    Supports multiple methods depending on available libraries
    """
    
    playbackFinished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.temp_files = []  # Track temporary files for cleanup
        self.current_player = None
        self.method = self._detect_best_method()
        
    def _detect_best_method(self):
        """Detect the best available transposition method"""
        if LIBROSA_AVAILABLE:
            return "librosa"
        elif PYDUB_AVAILABLE:
            return "pydub"
        else:
            return "basic"  # Simple pitch calculation without actual transposition
            
    def calculate_pitch_ratio(self, played_note: int, root_note: int, tune_cents: float = 0.0) -> float:
        """
        Calculate the pitch ratio for transposition
        
        Args:
            played_note: MIDI note being played
            root_note: Original root note of the sample
            tune_cents: Additional tuning in cents
            
        Returns:
            Pitch ratio (1.0 = no change, 2.0 = octave up, 0.5 = octave down)
        """
        # Calculate semitone difference
        semitone_diff = played_note - root_note
        
        # Add cents adjustment (100 cents = 1 semitone)
        total_cents = (semitone_diff * 100) + tune_cents
        
        # Convert to pitch ratio using equal temperament
        # Each semitone is 2^(1/12), so pitch_ratio = 2^(semitones/12)
        pitch_ratio = 2 ** (total_cents / 1200)
        
        return pitch_ratio
    
    def calculate_semitone_difference(self, played_note: int, root_note: int) -> int:
        """Calculate semitone difference between played note and root note"""
        return played_note - root_note
    
    def play_transposed_sample(self, sample_path: str, played_note: int, root_note: int, 
                             tune_cents: float = 0.0, volume: float = 1.0) -> bool:
        """
        Play a sample with proper transposition
        
        Args:
            sample_path: Path to the sample file
            played_note: MIDI note being played
            root_note: Root note of the sample
            tune_cents: Additional tuning in cents
            volume: Volume multiplier (0.0 to 1.0+)
            
        Returns:
            True if playback started successfully
        """
        if not os.path.exists(sample_path):
            return False
            
        pitch_ratio = self.calculate_pitch_ratio(played_note, root_note, tune_cents)
        
        # If no transposition needed, play directly
        if abs(pitch_ratio - 1.0) < 0.001:  # Very close to 1.0
            return self._play_direct(sample_path, volume)
        
        # Use the best available method for transposition
        if self.method == "librosa":
            return self._play_with_librosa(sample_path, pitch_ratio, volume)
        elif self.method == "pydub":
            return self._play_with_pydub(sample_path, pitch_ratio, volume)
        else:
            # Fallback: play without transposition but show info
            print(f"Transposition needed: {self.calculate_semitone_difference(played_note, root_note)} semitones")
            return self._play_direct(sample_path, volume)
    
    def _play_direct(self, sample_path: str, volume: float = 1.0) -> bool:
        """Play sample directly without transposition"""
        try:
            QSound.play(sample_path)
            return True
        except Exception as e:
            print(f"Error playing sample: {e}")
            return False
    
    def _play_with_librosa(self, sample_path: str, pitch_ratio: float, volume: float = 1.0) -> bool:
        """Play sample with librosa transposition (highest quality)"""
        try:
            # Load audio file
            y, sr = librosa.load(sample_path, sr=None)
            
            # Apply pitch shifting
            if pitch_ratio != 1.0:
                # Convert pitch ratio to semitones for librosa
                semitones = 12 * math.log2(pitch_ratio)
                y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones)
            else:
                y_shifted = y
            
            # Apply volume
            if volume != 1.0:
                y_shifted = y_shifted * volume
            
            # Save to temporary file and play
            temp_file = self._create_temp_file(y_shifted, sr)
            if temp_file:
                QSound.play(temp_file)
                return True
                
        except Exception as e:
            print(f"Error with librosa transposition: {e}")
            
        return False
    
    def _play_with_pydub(self, sample_path: str, pitch_ratio: float, volume: float = 1.0) -> bool:
        """Play sample with pydub transposition (medium quality)"""
        try:
            # Load audio with pydub
            audio = AudioSegment.from_file(sample_path)
            
            # Apply pitch shifting (approximate)
            if pitch_ratio != 1.0:
                # Pydub doesn't have built-in pitch shifting, so we simulate it
                # by changing playback speed and then adjusting duration
                new_sample_rate = int(audio.frame_rate * pitch_ratio)
                
                # Speed up/slow down (this changes both pitch and duration)
                audio_pitched = audio._spawn(audio.raw_data, overrides={
                    "frame_rate": new_sample_rate
                }).set_frame_rate(audio.frame_rate)
            else:
                audio_pitched = audio
            
            # Apply volume
            if volume != 1.0:
                volume_db = 20 * math.log10(max(volume, 0.001))  # Convert to dB
                audio_pitched = audio_pitched + volume_db
            
            # Save to temporary file and play
            temp_file = self._create_temp_file_pydub(audio_pitched)
            if temp_file:
                QSound.play(temp_file)
                return True
                
        except Exception as e:
            print(f"Error with pydub transposition: {e}")
            
        return False
    
    def _create_temp_file(self, audio_data: np.ndarray, sample_rate: int) -> Optional[str]:
        """Create temporary audio file from numpy array"""
        try:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_fd)
            
            # Write audio data
            sf.write(temp_path, audio_data, sample_rate)
            
            # Track for cleanup
            self.temp_files.append(temp_path)
            
            return temp_path
            
        except Exception as e:
            print(f"Error creating temp file: {e}")
            return None
    
    def _create_temp_file_pydub(self, audio: AudioSegment) -> Optional[str]:
        """Create temporary audio file from pydub AudioSegment"""
        try:
            # Create temporary file
            temp_fd, temp_path = tempfile.mkstemp(suffix='.wav')
            os.close(temp_fd)
            
            # Export audio
            audio.export(temp_path, format="wav")
            
            # Track for cleanup
            self.temp_files.append(temp_path)
            
            return temp_path
            
        except Exception as e:
            print(f"Error creating temp file: {e}")
            return None
    
    def cleanup_temp_files(self):
        """Clean up temporary audio files"""
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                print(f"Error cleaning up temp file {temp_file}: {e}")
        
        self.temp_files.clear()
    
    def get_transposition_info(self, played_note: int, root_note: int, tune_cents: float = 0.0) -> dict:
        """Get detailed transposition information for display"""
        semitone_diff = self.calculate_semitone_difference(played_note, root_note)
        pitch_ratio = self.calculate_pitch_ratio(played_note, root_note, tune_cents)
        
        # Calculate frequency ratio
        freq_ratio = pitch_ratio
        
        # Determine direction
        if semitone_diff > 0:
            direction = "up"
        elif semitone_diff < 0:
            direction = "down"
        else:
            direction = "none"
        
        return {
            'semitones': abs(semitone_diff),
            'direction': direction,
            'pitch_ratio': pitch_ratio,
            'frequency_ratio': freq_ratio,
            'cents_total': (semitone_diff * 100) + tune_cents,
            'method': self.method,
            'quality': self._get_quality_description()
        }
    
    def _get_quality_description(self) -> str:
        """Get description of transposition quality"""
        if self.method == "librosa":
            return "High Quality (Librosa PSOLA)"
        elif self.method == "pydub":
            return "Medium Quality (Speed Change)"
        else:
            return "Basic (No Transposition)"
    
    def get_capabilities(self) -> dict:
        """Get information about available transposition capabilities"""
        return {
            'method': self.method,
            'librosa_available': LIBROSA_AVAILABLE,
            'pydub_available': PYDUB_AVAILABLE,
            'can_transpose': self.method in ["librosa", "pydub"],
            'quality': self._get_quality_description(),
            'recommendations': self._get_recommendations()
        }
    
    def _get_recommendations(self) -> list:
        """Get recommendations for improving transposition quality"""
        recommendations = []
        
        if not LIBROSA_AVAILABLE:
            recommendations.append("Install librosa for high-quality pitch shifting: pip install librosa")
        
        if not PYDUB_AVAILABLE:
            recommendations.append("Install pydub for basic transposition: pip install pydub")
        
        if not LIBROSA_AVAILABLE and not PYDUB_AVAILABLE:
            recommendations.append("Currently only direct playback available - no transposition")
        
        return recommendations

class SampleTranspositionWidget:
    """
    UI helper for showing transposition information and controls
    """
    
    @staticmethod
    def get_transposition_tooltip(played_note: int, root_note: int, tune_cents: float = 0.0) -> str:
        """Generate tooltip text showing transposition info"""
        engine = TranspositionEngine()
        info = engine.get_transposition_info(played_note, root_note, tune_cents)
        
        tooltip_lines = []
        
        if info['direction'] == 'none':
            tooltip_lines.append("🎵 Playing at original pitch")
        else:
            direction_arrow = "↑" if info['direction'] == 'up' else "↓"
            tooltip_lines.append(f"🎵 Transposed {direction_arrow} {info['semitones']} semitones")
        
        tooltip_lines.append(f"Pitch Ratio: {info['pitch_ratio']:.3f}")
        tooltip_lines.append(f"Method: {info['quality']}")
        
        if abs(info['cents_total']) > 50:  # Show cents if significant
            tooltip_lines.append(f"Total Cents: {info['cents_total']:+.0f}")
        
        return "\\n".join(tooltip_lines)
    
    @staticmethod
    def get_note_name(midi_note: int) -> str:
        """Convert MIDI note to name"""
        note_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        octave = (midi_note // 12) - 1
        name = note_names[midi_note % 12]
        return f"{name}{octave}"

# Global transposition engine instance
_global_engine = None

def get_transposition_engine() -> TranspositionEngine:
    """Get the global transposition engine instance"""
    global _global_engine
    if _global_engine is None:
        _global_engine = TranspositionEngine()
    return _global_engine

def cleanup_transposition():
    """Clean up global transposition engine"""
    global _global_engine
    if _global_engine is not None:
        _global_engine.cleanup_temp_files()
        _global_engine = None