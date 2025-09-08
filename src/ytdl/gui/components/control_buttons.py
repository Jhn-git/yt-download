"""Control buttons component"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class ControlButtonsComponent:
    """Component for download control buttons"""
    
    def __init__(self, parent: tk.Widget,
                 start_callback: Optional[Callable[[], None]] = None,
                 clear_callback: Optional[Callable[[], None]] = None,
                 remove_callback: Optional[Callable[[], None]] = None,
                 settings_callback: Optional[Callable[[], None]] = None,
                 exit_callback: Optional[Callable[[], None]] = None):
        self.parent = parent
        self.start_callback = start_callback
        self.clear_callback = clear_callback
        self.remove_callback = remove_callback
        self.settings_callback = settings_callback
        self.exit_callback = exit_callback
        
        self.frame = None
        self.start_button = None
        self.clear_button = None
        self.remove_button = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the control buttons UI"""
        self.frame = ttk.Frame(self.parent)
        
        self.start_button = ttk.Button(self.frame, text="Start All", command=self._handle_start)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.clear_button = ttk.Button(self.frame, text="Clear Queue", command=self._handle_clear)
        self.clear_button.grid(row=0, column=1, padx=(0, 5))
        
        self.remove_button = ttk.Button(self.frame, text="Remove Selected", command=self._handle_remove)
        self.remove_button.grid(row=0, column=2, padx=(0, 20))
        
        # Spacer
        self.frame.columnconfigure(3, weight=1)
        
        ttk.Button(self.frame, text="Settings", command=self._handle_settings).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(self.frame, text="Exit", command=self._handle_exit).grid(row=0, column=5)
    
    def grid(self, **kwargs):
        """Grid the frame component"""
        if self.frame:
            self.frame.grid(**kwargs)
    
    def update_button_states(self, has_queue: bool, has_selection: bool, 
                           is_downloading: bool, pending_items: int):
        """Update button states based on current state"""
        # Start button: enabled if there are pending items and not currently downloading
        if pending_items > 0 and not is_downloading:
            self.start_button.config(state="normal", text="Start All")
        elif is_downloading:
            self.start_button.config(state="disabled", text="Downloading...")
        elif has_queue and pending_items == 0:
            self.start_button.config(state="disabled", text="All Complete")
        else:
            self.start_button.config(state="disabled", text="Start All")
        
        # Clear button: enabled if there's a queue
        self.clear_button.config(state="normal" if has_queue else "disabled")
        
        # Remove button: enabled if there's a selection
        self.remove_button.config(state="normal" if has_selection else "disabled")
    
    def _handle_start(self):
        """Handle start button click"""
        if self.start_callback:
            self.start_callback()
    
    def _handle_clear(self):
        """Handle clear button click"""
        if self.clear_callback:
            self.clear_callback()
    
    def _handle_remove(self):
        """Handle remove button click"""
        if self.remove_callback:
            self.remove_callback()
    
    def _handle_settings(self):
        """Handle settings button click"""
        if self.settings_callback:
            self.settings_callback()
    
    def _handle_exit(self):
        """Handle exit button click"""
        if self.exit_callback:
            self.exit_callback()