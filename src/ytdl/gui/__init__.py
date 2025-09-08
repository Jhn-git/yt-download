"""GUI package for YT-Download"""

try:
    from .main_window import GUIService
    __all__ = ['GUIService']
except ImportError:
    # Fallback if tkinter is not available
    GUIService = None
    __all__ = []