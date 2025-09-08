"""Download queue component"""

import tkinter as tk
from tkinter import ttk
from typing import List, Callable, Optional

from ..models.download_item import DownloadItem


class DownloadQueueComponent:
    """Component for displaying and managing the download queue"""
    
    def __init__(self, parent: tk.Widget, 
                 selection_callback: Optional[Callable[[], None]] = None):
        self.parent = parent
        self.selection_callback = selection_callback
        self.download_queue: List[DownloadItem] = []
        
        self.frame = None
        self.queue_tree = None
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the download queue UI"""
        # Download queue frame
        self.frame = ttk.LabelFrame(self.parent, text="Download Queue", padding="5")
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        
        # Treeview for queue
        columns = ("URL", "Channel", "Size", "Quality", "Status", "Progress")
        self.queue_tree = ttk.Treeview(self.frame, columns=columns, show="tree headings", height=8)
        
        # Configure columns
        self.queue_tree.heading("#0", text="Title")
        self.queue_tree.column("#0", width=250, minwidth=150)
        
        # Configure individual columns with appropriate sizing
        column_config = {
            "URL": {"width": 120, "minwidth": 100},
            "Channel": {"width": 120, "minwidth": 100},
            "Size": {"width": 80, "minwidth": 70},
            "Quality": {"width": 80, "minwidth": 70},
            "Status": {"width": 80, "minwidth": 70},
            "Progress": {"width": 70, "minwidth": 60}
        }
        
        for col in columns:
            self.queue_tree.heading(col, text=col)
            config = column_config.get(col, {"width": 100, "minwidth": 80})
            self.queue_tree.column(col, width=config["width"], minwidth=config["minwidth"])
        
        self.queue_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bind selection change event
        if self.selection_callback:
            self.queue_tree.bind('<<TreeviewSelect>>', lambda e: self.selection_callback())
        
        # Queue scrollbar
        queue_scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.queue_tree.yview)
        queue_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.queue_tree.configure(yscrollcommand=queue_scrollbar.set)
    
    def grid(self, **kwargs):
        """Grid the frame component"""
        if self.frame:
            self.frame.grid(**kwargs)
    
    def add_item(self, item: DownloadItem):
        """Add an item to the download queue"""
        self.download_queue.append(item)
        
        # Add to treeview with initial values
        url_display = item.url[:30] + "..." if len(item.url) > 30 else item.url
        item_id = self.queue_tree.insert("", "end", text="Fetching title...", 
                                       values=(url_display, "Fetching...", "Fetching...", 
                                              item.quality, item.status, "0%"))
        item.tree_item_id = item_id
    
    def update_item_metadata(self, item: DownloadItem):
        """Update download item metadata in the display"""
        if item.tree_item_id and self.queue_tree.exists(item.tree_item_id):
            self.queue_tree.item(item.tree_item_id, text=item.title)
            # Update the channel and size columns
            current_values = list(self.queue_tree.set(item.tree_item_id).values())
            if len(current_values) >= 6:
                current_values[1] = item.channel  # Channel column
                current_values[2] = item.file_size  # Size column
                self.queue_tree.item(item.tree_item_id, values=current_values)
    
    def update_item_progress(self, item: DownloadItem):
        """Update item progress and status in the display"""
        if item.tree_item_id and self.queue_tree.exists(item.tree_item_id):
            # Update all columns
            self.queue_tree.set(item.tree_item_id, "Status", item.status)
            self.queue_tree.set(item.tree_item_id, "Progress", f"{item.progress}%")
            
            # Update title if it was set
            if item.title != "Unknown":
                self.queue_tree.item(item.tree_item_id, text=item.title)
    
    def update_all_items(self):
        """Update all items in the display"""
        for item in self.download_queue:
            self.update_item_progress(item)
    
    def get_selected_item(self) -> Optional[DownloadItem]:
        """Get the currently selected download item"""
        selection = self.queue_tree.selection()
        if not selection:
            return None
        
        item_id = selection[0]
        index = self.queue_tree.index(item_id)
        
        if 0 <= index < len(self.download_queue):
            return self.download_queue[index]
        
        return None
    
    def remove_selected_item(self) -> bool:
        """Remove the selected item from the queue"""
        selection = self.queue_tree.selection()
        if not selection:
            return False
        
        item_id = selection[0]
        index = self.queue_tree.index(item_id)
        
        # Remove from queue and treeview
        if 0 <= index < len(self.download_queue):
            del self.download_queue[index]
        self.queue_tree.delete(item_id)
        return True
    
    def clear_queue(self):
        """Clear all items from the queue"""
        self.download_queue.clear()
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
    
    def has_selection(self) -> bool:
        """Check if there's a selected item"""
        return len(self.queue_tree.selection()) > 0
    
    def has_items(self) -> bool:
        """Check if there are items in the queue"""
        return len(self.download_queue) > 0
    
    def count_pending_items(self) -> int:
        """Count items that are still pending (not completed or failed)"""
        return sum(1 for item in self.download_queue if item.status == "Queued")