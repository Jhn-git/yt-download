"""Download item model for GUI"""

from typing import Optional

try:
    from PIL import Image
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class DownloadItem:
    """Represents a single download item in the queue"""
    
    def __init__(self, url: str, quality: str = "best", output_dir: str = ""):
        self.url = url
        self.quality = quality
        self.output_dir = output_dir
        self.status = "Queued"
        self.progress = 0
        self.title = "Unknown"
        self.channel = "Unknown"
        self.file_size = "Unknown"
        self.error_message = ""
        self.thumbnail_url: Optional[str] = None
        self.thumbnail_image = None  # PIL Image for display
        self.tree_item_id: Optional[str] = None  # Store reference to GUI tree item
    
    def update_title(self, title: str):
        """Update the title of this download item"""
        if title and title.strip():
            self.title = title.strip()
    
    def update_metadata(self, title: str = None, channel: str = None, file_size: str = None):
        """Update multiple metadata fields"""
        if title and title.strip():
            self.title = title.strip()
        if channel and channel.strip():
            self.channel = channel.strip()
        if file_size and file_size.strip():
            self.file_size = file_size.strip()
    
    def __str__(self):
        return f"{self.title} ({self.status})"