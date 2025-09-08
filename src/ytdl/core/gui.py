"""Backward compatibility wrapper for the refactored GUI"""

# Import utility functions and models (these don't depend on tkinter)
from ..gui.utils.gui_utils import format_file_size, is_valid_url
from ..gui.models.download_item import DownloadItem

# Import the refactored GUIService conditionally
try:
    from ..gui.main_window import GUIService
    __all__ = ['GUIService', 'DownloadItem', 'format_file_size', 'is_valid_url']
except ImportError:
    # Fallback if tkinter is not available
    GUIService = None
    __all__ = ['DownloadItem', 'format_file_size', 'is_valid_url']