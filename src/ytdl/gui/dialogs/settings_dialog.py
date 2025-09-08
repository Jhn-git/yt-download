"""Settings dialog component"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional

from ...core.config import ConfigService


class SettingsDialog:
    """Settings configuration dialog"""
    
    def __init__(self, parent: tk.Widget, config: ConfigService, 
                 save_callback: Optional[Callable[[str, str, bool], None]] = None):
        self.parent = parent
        self.config = config
        self.save_callback = save_callback
        self.window = None
        self.auto_fetch_enabled = True  # Default value
    
    def show(self, auto_fetch_enabled: bool = True):
        """Show the settings dialog"""
        self.auto_fetch_enabled = auto_fetch_enabled
        
        self.window = tk.Toplevel(self.parent)
        self.window.title("Settings")
        self.window.geometry("400x300")
        self.window.grab_set()
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the settings dialog UI"""
        frame = ttk.Frame(self.window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Default quality
        ttk.Label(frame, text="Default Quality:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.quality_var = tk.StringVar(value=self.config.quality)
        quality_combo = ttk.Combobox(frame, textvariable=self.quality_var, 
                                   values=["best", "720p", "1080p", "480p", "worst"], 
                                   state="readonly")
        quality_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Default output directory
        ttk.Label(frame, text="Default Output:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.output_var = tk.StringVar(value=self.config.download_dir)
        output_entry = ttk.Entry(frame, textvariable=self.output_var)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Auto-fetch setting
        self.auto_fetch_var = tk.BooleanVar(value=self.auto_fetch_enabled)
        auto_fetch_check = ttk.Checkbutton(frame, text="Auto-fetch video info when URL is pasted", 
                                         variable=self.auto_fetch_var)
        auto_fetch_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self._save_settings).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=self._close).grid(row=0, column=1)
        
        frame.columnconfigure(1, weight=1)
    
    def _save_settings(self):
        """Save the settings and close dialog"""
        quality = self.quality_var.get()
        output_dir = self.output_var.get()
        auto_fetch = self.auto_fetch_var.get()
        
        # Update config
        self.config.quality = quality
        self.config.download_dir = output_dir
        
        # Notify parent via callback
        if self.save_callback:
            self.save_callback(quality, output_dir, auto_fetch)
        
        self._close()
    
    def _close(self):
        """Close the dialog"""
        if self.window:
            self.window.destroy()
            self.window = None