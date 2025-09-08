"""Options panel component"""

import tkinter as tk
from tkinter import ttk, filedialog
from typing import Optional, Callable
from ..utils.gui_utils import open_folder


class OptionsPanelComponent:
    """Component for quality and output directory selection"""
    
    def __init__(self, parent: tk.Widget, default_quality: str = "best", default_output: str = "", 
                 open_folder_callback: Optional[Callable[[str], None]] = None):
        self.parent = parent
        self.open_folder_callback = open_folder_callback
        
        self.frame = None
        self.quality_var = None
        self.output_var = None
        self.output_entry = None
        
        self._setup_ui(default_quality, default_output)
    
    def _setup_ui(self, default_quality: str, default_output: str):
        """Setup the options panel UI"""
        self.frame = ttk.Frame(self.parent)
        self.frame.columnconfigure(2, weight=1)
        
        # Quality selection
        ttk.Label(self.frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.quality_var = tk.StringVar(value=default_quality)
        quality_combo = ttk.Combobox(self.frame, textvariable=self.quality_var, 
                                   values=["best", "720p", "1080p", "480p", "worst", "bestaudio/best"], 
                                   state="readonly", width=15)
        quality_combo.grid(row=0, column=1, padx=(0, 20))
        
        # Output directory selection
        ttk.Label(self.frame, text="Output:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.output_var = tk.StringVar(value=default_output)
        self.output_entry = ttk.Entry(self.frame, textvariable=self.output_var, width=30)
        self.output_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(self.frame, text="Browse", command=self._browse_output_dir).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(self.frame, text="Open Folder", command=self._open_folder).grid(row=0, column=5)
    
    def grid(self, **kwargs):
        """Grid the frame component"""
        if self.frame:
            self.frame.grid(**kwargs)
    
    def get_quality(self) -> str:
        """Get the selected quality"""
        if self.quality_var:
            return self.quality_var.get()
        return "best"
    
    def get_output_dir(self) -> str:
        """Get the selected output directory"""
        if self.output_var:
            return self.output_var.get()
        return ""
    
    def set_quality(self, quality: str):
        """Set the quality selection"""
        if self.quality_var:
            self.quality_var.set(quality)
    
    def set_output_dir(self, output_dir: str):
        """Set the output directory"""
        if self.output_var:
            self.output_var.set(output_dir)
    
    def _browse_output_dir(self):
        """Browse for output directory"""
        current_dir = self.get_output_dir()
        directory = filedialog.askdirectory(initialdir=current_dir)
        if directory:
            self.set_output_dir(directory)
    
    def _open_folder(self):
        """Open the current output directory"""
        current_dir = self.get_output_dir()
        if not current_dir:
            return
        
        success = open_folder(current_dir)
        if self.open_folder_callback:
            self.open_folder_callback(current_dir if success else None)