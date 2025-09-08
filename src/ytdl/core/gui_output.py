import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional
from .downloader import OutputHandler


class GUIOutputHandler(OutputHandler):
    def __init__(self, 
                 info_callback: Optional[Callable[[str], None]] = None,
                 error_callback: Optional[Callable[[str], None]] = None,
                 progress_callback: Optional[Callable[[str], None]] = None):
        self.info_callback = info_callback
        self.error_callback = error_callback  
        self.progress_callback = progress_callback
    
    def info(self, message: str):
        if self.info_callback:
            self.info_callback(message)
    
    def error(self, message: str):
        if self.error_callback:
            self.error_callback(message)
    
    def progress(self, message: str):
        """Handle progress updates from downloader"""
        if self.progress_callback:
            self.progress_callback(message)


class GUILogger:
    """Simple GUI logger that displays messages in a text widget"""
    
    def __init__(self, text_widget: tk.Text):
        self.text_widget = text_widget
    
    def log(self, level: str, message: str):
        """Add a log message to the text widget"""
        timestamp = self._get_timestamp()
        log_entry = f"[{timestamp}] {level}: {message}\n"
        
        # Insert at end and auto-scroll
        self.text_widget.insert(tk.END, log_entry)
        self.text_widget.see(tk.END)
        
        # Limit log size to prevent memory issues
        lines = self.text_widget.get("1.0", tk.END).count('\n')
        if lines > 1000:
            self.text_widget.delete("1.0", "100.0")
    
    def info(self, message: str):
        self.log("INFO", message)
    
    def error(self, message: str):
        self.log("ERROR", message)
    
    def clear(self):
        """Clear all log messages"""
        self.text_widget.delete("1.0", tk.END)
    
    def _get_timestamp(self) -> str:
        import datetime
        return datetime.datetime.now().strftime("%H:%M:%S")