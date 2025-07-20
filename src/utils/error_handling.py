"""
Centralized Error Handling for DecentSampler Frontend
Provides user-friendly error messages and dependency checking
"""

from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtCore import QObject, pyqtSignal
import traceback
import sys
from typing import Optional, Callable, Any

class DependencyChecker:
    """Check for optional dependencies and provide helpful messages"""
    
    @staticmethod
    def check_pygame() -> tuple[bool, str]:
        """Check if pygame is available"""
        try:
            import pygame
            return True, "pygame is available"
        except ImportError:
            return False, "pygame is not installed. Audio preview features will be limited.\n\nTo enable full audio preview:\npip install pygame"
    
    @staticmethod
    def check_numpy() -> tuple[bool, str]:
        """Check if numpy is available"""
        try:
            import numpy
            return True, "numpy is available"
        except ImportError:
            return False, "numpy is not installed. Waveform visualization will be limited.\n\nTo enable enhanced waveform display:\npip install numpy"
    
    @staticmethod
    def check_librosa() -> tuple[bool, str]:
        """Check if librosa is available"""
        try:
            import librosa
            return True, "librosa is available"
        except ImportError:
            return False, "librosa is not installed. High-quality pitch shifting will be unavailable.\n\nTo enable professional audio transposition:\npip install librosa"
    
    @staticmethod
    def check_pydub() -> tuple[bool, str]:
        """Check if pydub is available"""
        try:
            import pydub
            return True, "pydub is available"
        except ImportError:
            return False, "pydub is not installed. Basic audio transposition will be unavailable.\n\nTo enable basic audio transposition:\npip install pydub"
    
    @staticmethod
    def check_soundfile() -> tuple[bool, str]:
        """Check if soundfile is available"""
        try:
            import soundfile
            return True, "soundfile is available"
        except ImportError:
            return False, "soundfile is not installed. Some audio file operations may be limited.\n\nTo enable full audio support:\npip install soundfile"
    
    @staticmethod
    def get_all_dependencies_status() -> dict:
        """Get status of all optional dependencies"""
        return {
            'pygame': DependencyChecker.check_pygame(),
            'numpy': DependencyChecker.check_numpy(),
            'librosa': DependencyChecker.check_librosa(),
            'pydub': DependencyChecker.check_pydub(),
            'soundfile': DependencyChecker.check_soundfile()
        }
    
    @staticmethod
    def get_missing_dependencies_message() -> str:
        """Get a comprehensive message about missing dependencies"""
        status = DependencyChecker.get_all_dependencies_status()
        missing = []
        messages = []
        
        for dep, (available, message) in status.items():
            if not available:
                missing.append(dep)
                messages.append(message)
        
        if not missing:
            return "All optional dependencies are installed!"
        
        header = "Some optional features are unavailable due to missing dependencies:\n\n"
        install_all = f"\n\nTo install all optional dependencies at once:\npip install {' '.join(missing)}"
        
        return header + "\n\n".join(messages) + install_all

class ErrorHandler(QObject):
    """Centralized error handler with user-friendly messages"""
    
    # Signal emitted when an error should be shown to the user
    errorOccurred = pyqtSignal(str, str)  # title, message
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.parent_widget = parent
        self.error_log = []
        
    def handle_error(self, error: Exception, context: str = "", 
                    show_dialog: bool = True, suggest_solution: bool = True) -> str:
        """
        Handle an error with appropriate user messaging
        
        Args:
            error: The exception that occurred
            context: Context about what was happening when error occurred
            show_dialog: Whether to show error dialog to user
            suggest_solution: Whether to suggest solutions for common errors
            
        Returns:
            Formatted error message
        """
        # Get error details
        error_type = type(error).__name__
        error_msg = str(error)
        
        # Build user-friendly message
        if context:
            message = f"An error occurred while {context}:\n\n"
        else:
            message = "An unexpected error occurred:\n\n"
        
        message += f"{error_type}: {error_msg}"
        
        # Add solution suggestions
        if suggest_solution:
            solution = self._get_solution_suggestion(error, error_type, error_msg)
            if solution:
                message += f"\n\n{solution}"
        
        # Log the error
        self.error_log.append({
            'context': context,
            'error_type': error_type,
            'error_msg': error_msg,
            'traceback': traceback.format_exc()
        })
        
        # Show dialog if requested
        if show_dialog and self.parent_widget:
            self.show_error_dialog("Error", message)
        
        # Emit signal for other components to handle
        self.errorOccurred.emit("Error", message)
        
        return message
    
    def _get_solution_suggestion(self, error: Exception, error_type: str, error_msg: str) -> Optional[str]:
        """Get solution suggestion based on error type and message"""
        
        # Import errors for optional dependencies
        if isinstance(error, ImportError):
            module_name = str(error.name) if hasattr(error, 'name') else ""
            
            if 'pygame' in error_msg or module_name == 'pygame':
                return "To enable audio preview:\npip install pygame"
            elif 'numpy' in error_msg or module_name == 'numpy':
                return "To enable waveform visualization:\npip install numpy"
            elif 'librosa' in error_msg or module_name == 'librosa':
                return "To enable high-quality pitch shifting:\npip install librosa"
            elif 'pydub' in error_msg or module_name == 'pydub':
                return "To enable audio transposition:\npip install pydub"
            elif 'soundfile' in error_msg or module_name == 'soundfile':
                return "To enable full audio support:\npip install soundfile"
        
        # File errors
        elif isinstance(error, FileNotFoundError):
            return "Make sure the file path is correct and the file exists."
        
        # Permission errors
        elif isinstance(error, PermissionError):
            return "Check that you have permission to access this file or directory."
        
        # Audio format errors
        elif "unsupported" in error_msg.lower() and "format" in error_msg.lower():
            return "This audio format may not be supported. Try converting to WAV format."
        
        # Memory errors
        elif isinstance(error, MemoryError):
            return "Try closing other applications or working with smaller files."
        
        return None
    
    def show_error_dialog(self, title: str, message: str, detail: Optional[str] = None):
        """Show error dialog to user"""
        if not self.parent_widget:
            return
            
        msg_box = QMessageBox(self.parent_widget)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if detail:
            msg_box.setDetailedText(detail)
        
        msg_box.exec_()
    
    def show_dependency_status(self):
        """Show dialog with dependency status"""
        message = DependencyChecker.get_missing_dependencies_message()
        
        if "All optional dependencies are installed!" in message:
            icon = QMessageBox.Information
            title = "Dependencies OK"
        else:
            icon = QMessageBox.Warning  
            title = "Missing Optional Dependencies"
        
        if self.parent_widget:
            msg_box = QMessageBox(self.parent_widget)
            msg_box.setIcon(icon)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.exec_()
    
    def get_error_log(self) -> list:
        """Get the error log"""
        return self.error_log
    
    def clear_error_log(self):
        """Clear the error log"""
        self.error_log.clear()

def safe_import(module_name: str, feature_name: str = "") -> tuple[Any, bool]:
    """
    Safely import an optional module
    
    Args:
        module_name: Name of module to import
        feature_name: Name of feature that requires this module
        
    Returns:
        Tuple of (module or None, success boolean)
    """
    try:
        module = __import__(module_name)
        return module, True
    except ImportError:
        if feature_name:
            print(f"Note: {module_name} not available. {feature_name} features will be limited.")
        return None, False

def with_error_handling(context: str = "", show_dialog: bool = True):
    """
    Decorator for methods that need error handling
    
    Usage:
        @with_error_handling("loading audio file")
        def load_audio(self, path):
            # method implementation
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                # Look for error handler in self or create temporary one
                if hasattr(self, 'error_handler'):
                    handler = self.error_handler
                else:
                    handler = ErrorHandler(getattr(self, 'parent', None))
                
                handler.handle_error(e, context=context, show_dialog=show_dialog)
                return None
        return wrapper
    return decorator

# Global error handler instance
_global_error_handler = None

def get_global_error_handler(parent: Optional[QWidget] = None) -> ErrorHandler:
    """Get or create global error handler"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler(parent)
    elif parent and _global_error_handler.parent_widget is None:
        _global_error_handler.parent_widget = parent
    return _global_error_handler