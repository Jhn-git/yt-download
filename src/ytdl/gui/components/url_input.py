"""URL input component"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional

from ..utils.gui_utils import is_valid_url


class URLInputComponent:
    """Component for URL input with auto-fetch functionality"""
    
    def __init__(self, parent: tk.Widget,
                 add_callback: Optional[Callable[[str], None]] = None,
                 info_callback: Optional[Callable[[str], None]] = None):
        self.parent = parent
        self.add_callback = add_callback
        self.info_callback = info_callback
        
        self.frame = None
        self.url_var = None
        self.url_entry = None
        
        # Auto-fetch functionality
        self.auto_fetch_enabled = True
        self.auto_fetch_timer = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the URL input UI"""
        # URL input section
        self.frame = ttk.LabelFrame(self.parent, text="Download", padding="5")
        self.frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(self.frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.url_entry.bind('<Return>', lambda e: self._handle_add())
        
        # Add auto-fetch functionality with debouncing
        self.url_var.trace('w', self._on_url_change)
        
        ttk.Button(self.frame, text="Info", command=self._handle_info).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(self.frame, text="Add", command=self._handle_add).grid(row=0, column=3)
    
    def grid(self, **kwargs):
        """Grid the frame component"""
        if self.frame:
            self.frame.grid(**kwargs)
    
    def get_url(self) -> str:
        """Get the current URL value"""
        if self.url_var:
            return self.url_var.get().strip()
        return ""
    
    def clear_url(self):
        """Clear the URL input"""
        if self.url_var:
            self.url_var.set("")
    
    def set_auto_fetch_enabled(self, enabled: bool):
        """Enable or disable auto-fetch functionality"""
        self.auto_fetch_enabled = enabled
    
    def _on_url_change(self, *args):
        """Handle URL entry changes for auto-fetch functionality"""
        if not self.auto_fetch_enabled:
            return
        
        # Cancel any existing timer
        if self.auto_fetch_timer:
            self.parent.after_cancel(self.auto_fetch_timer)
        
        # Set up a new timer for debounced auto-fetch
        self.auto_fetch_timer = self.parent.after(1000, self._auto_fetch_info)  # 1 second delay
    
    def _auto_fetch_info(self):
        """Auto-fetch video information if URL appears valid"""
        url = self.get_url()
        
        if not url or not is_valid_url(url):
            return
        
        # Auto-add to queue if URL appears valid and complete
        if len(url) > 20:  # Reasonable minimum length for a complete URL
            self._handle_add()
    
    def _handle_add(self):
        """Handle add button click"""
        url = self.get_url()
        if not url:
            return
        
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Invalid URL", "Please enter a valid URL starting with http:// or https://")
            return
        
        if self.add_callback:
            self.add_callback(url)
        
        # Clear URL entry
        self.clear_url()
    
    def _handle_info(self):
        """Handle info button click"""
        url = self.get_url()
        if not url:
            return
        
        if self.info_callback:
            self.info_callback(url)