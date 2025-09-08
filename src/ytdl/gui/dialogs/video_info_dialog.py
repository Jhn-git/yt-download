"""Video info dialog component"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any


class VideoInfoDialog:
    """Video information display dialog"""
    
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.window = None
    
    def show(self, info: Dict[str, Any]):
        """Show the video info dialog with the provided information"""
        self.window = tk.Toplevel(self.parent)
        self.window.title("Video Information")
        self.window.geometry("500x300")
        
        self._setup_ui(info)
    
    def _setup_ui(self, info: Dict[str, Any]):
        """Setup the video info dialog UI"""
        frame = ttk.Frame(self.window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        info_text = tk.Text(frame, wrap=tk.WORD, height=15)
        info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=info_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        info_text.configure(yscrollcommand=scrollbar.set)
        
        # Format info
        info_content = self._format_info(info)
        info_text.insert("1.0", info_content)
        info_text.configure(state="disabled")
        
        # Configure grid weights
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
    
    def _format_info(self, info: Dict[str, Any]) -> str:
        """Format video information for display"""
        lines = []
        
        # Basic info
        lines.append(f"Title: {info.get('title', 'Unknown')}")
        lines.append(f"Duration: {info.get('duration', 'Unknown')} seconds")
        lines.append(f"Uploader: {info.get('uploader', 'Unknown')}")
        lines.append(f"View Count: {info.get('view_count', 'Unknown')}")
        lines.append(f"Upload Date: {info.get('upload_date', 'Unknown')}")
        
        # Description (truncated)
        description = info.get('description', 'No description')
        if description and len(description) > 500:
            description = description[:500] + "..."
        lines.append(f"Description: {description}")
        
        return "\n".join(lines)