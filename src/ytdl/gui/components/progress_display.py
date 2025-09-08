"""Progress display component"""

import tkinter as tk
from tkinter import ttk


class ProgressDisplayComponent:
    """Component for displaying download progress"""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        
        self.progress_frame = None
        self.progress_var = None
        self.progress_bar = None
        self.progress_label = None
        self.status_var = None
        self.status_label = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the progress display UI"""
        # Progress bar frame
        self.progress_frame = ttk.Frame(self.parent)
        self.progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.progress_label = ttk.Label(self.progress_frame, text="Ready")
        self.progress_label.grid(row=0, column=1)
    
    def grid_progress(self, **kwargs):
        """Grid the progress frame"""
        if self.progress_frame:
            self.progress_frame.grid(**kwargs)
    
    def grid_status(self, **kwargs):
        """Grid the status label"""
        if self.status_label:
            self.status_label.grid(**kwargs)
    
    def create_status_label(self, parent: tk.Widget):
        """Create and return a status label (for placement outside this component)"""
        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = ttk.Label(parent, textvariable=self.status_var)
        return self.status_label
    
    def set_progress(self, percentage: float):
        """Set the progress percentage"""
        if self.progress_var:
            self.progress_var.set(percentage)
        if self.progress_label:
            self.progress_label.config(text=f"{percentage:.1f}%")
    
    def reset_progress(self):
        """Reset progress to 0"""
        self.set_progress(0)
        if self.progress_label:
            self.progress_label.config(text="Ready")
    
    def set_status(self, message: str):
        """Set the status message"""
        if self.status_var:
            self.status_var.set(message)
    
    def get_status(self) -> str:
        """Get the current status message"""
        if self.status_var:
            return self.status_var.get()
        return ""