"""Main GUI window coordinator"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import re
import tempfile
import signal
from typing import Optional

from ..core.config import ConfigService
from ..core.downloader import DownloaderService
from ..core.logger import LoggerService
from ..core.gui_output import GUIOutputHandler

from .components.url_input import URLInputComponent
from .components.options_panel import OptionsPanelComponent
from .components.download_queue import DownloadQueueComponent
from .components.progress_display import ProgressDisplayComponent
from .components.control_buttons import ControlButtonsComponent
from .dialogs.settings_dialog import SettingsDialog
from .dialogs.video_info_dialog import VideoInfoDialog
from .models.download_item import DownloadItem
from .utils.gui_utils import format_file_size, is_valid_url

try:
    from PIL import Image, ImageTk
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


class GUIService:
    """Main GUI service coordinator for the YouTube downloader"""
    
    def __init__(self, config: ConfigService, downloader: DownloaderService, logger: LoggerService):
        self.config = config
        self.downloader = downloader
        self.logger = logger
        self.current_download: Optional[DownloadItem] = None
        
        # Thumbnail cache management
        self.thumbnail_cache = {}
        self.thumbnail_temp_dir = tempfile.mkdtemp() if HAS_PILLOW else None
        self.placeholder_image = None
        
        # Auto-fetch functionality
        self.auto_fetch_enabled = True
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("YT-Download GUI")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # Initialize components
        self._create_components()
        self._setup_layout()
        self._setup_gui_output_handler()
    
    def _create_components(self):
        """Create all GUI components"""
        # Main container
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)
        
        # URL input component
        self.url_input = URLInputComponent(
            self.main_frame,
            add_callback=self._handle_add_url,
            info_callback=self._handle_show_info
        )
        
        # Options panel component
        self.options_panel = OptionsPanelComponent(
            self.main_frame,
            default_quality=self.config.quality,
            default_output=self.config.download_dir
        )
        
        # Download queue component
        self.download_queue = DownloadQueueComponent(
            self.main_frame,
            selection_callback=self._update_button_states
        )
        
        # Progress display component
        self.progress_display = ProgressDisplayComponent(self.main_frame)
        self.status_label = self.progress_display.create_status_label(self.main_frame)
        
        # Control buttons component
        self.control_buttons = ControlButtonsComponent(
            self.main_frame,
            start_callback=self._start_downloads,
            clear_callback=self._clear_queue,
            remove_callback=self._remove_selected,
            settings_callback=self._show_settings,
            exit_callback=self.root.quit
        )
        
        # Dialog components (created on demand)
        self.settings_dialog = None
        self.video_info_dialog = None
    
    def _setup_layout(self):
        """Setup the layout of components"""
        # URL input section
        self.url_input.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Options panel
        self.options_panel.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Download queue
        self.download_queue.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Progress bar
        self.progress_display.grid_progress(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status label
        self.status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Control buttons
        self.control_buttons.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        # Configure main grid weights for resizing
        self.main_frame.rowconfigure(2, weight=1)
        
        # Initialize button states
        self._update_button_states()
    
    def _setup_gui_output_handler(self):
        """Setup GUI output handler for downloader feedback"""
        self.gui_output = GUIOutputHandler(
            info_callback=self._handle_info_message,
            error_callback=self._handle_error_message,
            progress_callback=self._handle_progress_update
        )
        
        # Replace downloader's output handler
        self.downloader.output_handler = self.gui_output
    
    def _handle_add_url(self, url: str):
        """Handle URL addition to queue"""
        # Check if URL is already in queue
        if any(item.url == url for item in self.download_queue.download_queue):
            return
        
        quality = self.options_panel.get_quality()
        output_dir = self.options_panel.get_output_dir()
        
        # Create download item and add to queue
        item = DownloadItem(url, quality, output_dir)
        self.download_queue.add_item(item)
        
        self.progress_display.set_status(f"Fetching video info... ({self.download_queue.count_pending_items()} items in queue)")
        
        # Fetch title asynchronously with timeout handling
        threading.Thread(target=self._fetch_metadata, args=(item,), daemon=True).start()
        
        # Update button states
        self._update_button_states()
    
    def _fetch_metadata(self, item: DownloadItem):
        """Fetch video metadata in background thread"""
        try:
            # Set timeout for metadata fetching (Unix systems only)
            if hasattr(signal, 'SIGALRM'):
                def timeout_handler(signum, frame):
                    raise TimeoutError("Metadata fetch timeout")
                
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(10)  # 10 second timeout
            
            info = self.downloader.get_info(item.url)
            
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)  # Cancel timeout
            
            if info and 'title' in info:
                title = info['title']
                channel = info.get('uploader', info.get('channel', 'Unknown'))
                
                # Extract file size information
                file_size = "Unknown"
                if 'filesize' in info and info['filesize']:
                    file_size = format_file_size(info['filesize'])
                elif 'filesize_approx' in info and info['filesize_approx']:
                    file_size = format_file_size(info['filesize_approx'])
                
                # Update on main thread
                self.root.after(0, lambda: self._update_item_metadata(item, title, channel, file_size))
            else:
                # Fallback
                self.root.after(0, lambda: self._update_item_metadata(item, "Unknown", "Unknown", "Unknown"))
        except (Exception, TimeoutError):
            # Error or timeout
            if hasattr(signal, 'SIGALRM'):
                signal.alarm(0)
            self.root.after(0, lambda: self._update_item_metadata(item, "Unknown", "Unknown", "Unknown"))
    
    def _update_item_metadata(self, item: DownloadItem, title: str, channel: str = None, file_size: str = None):
        """Update download item metadata"""
        item.update_metadata(title, channel, file_size)
        self.download_queue.update_item_metadata(item)
        
        self.progress_display.set_status(f"Ready - {len(self.download_queue.download_queue)} items in queue")
        self._update_button_states()
    
    def _handle_show_info(self, url: str):
        """Handle video info request"""
        def fetch_info():
            info = self.downloader.get_info(url)
            if info:
                self.root.after(0, lambda: self._display_video_info(info))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Could not fetch video information"))
        
        self.progress_display.set_status("Fetching video information...")
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def _display_video_info(self, info: dict):
        """Display video information dialog"""
        self.video_info_dialog = VideoInfoDialog(self.root)
        self.video_info_dialog.show(info)
        self.progress_display.set_status("Ready")
    
    def _start_downloads(self):
        """Start downloading all queued items"""
        if not self.download_queue.has_items():
            return
        
        if self.current_download:
            messagebox.showinfo("Download in Progress", "A download is already in progress")
            return
        
        def download_worker():
            self.root.after(0, self._update_button_states)
            
            for item in self.download_queue.download_queue:
                if item.status == "Queued":
                    self.current_download = item
                    self.root.after(0, lambda: self.progress_display.set_status(f"Downloading: {item.url}"))
                    self.root.after(0, self._update_button_states)
                    
                    item.status = "Downloading"
                    self.root.after(0, self.download_queue.update_all_items)
                    
                    success = self.downloader.download(item.url, item.output_dir or None, item.quality)
                    
                    if success:
                        item.status = "Complete"
                        item.progress = 100
                    else:
                        item.status = "Failed"
                    
                    self.root.after(0, self.download_queue.update_all_items)
                    self.root.after(0, self._update_button_states)
            
            self.current_download = None
            self.root.after(0, lambda: self.progress_display.set_status("All downloads completed"))
            self.root.after(0, lambda: self.progress_display.reset_progress())
            self.root.after(0, self._update_button_states)
        
        threading.Thread(target=download_worker, daemon=True).start()
    
    def _clear_queue(self):
        """Clear the download queue"""
        self.download_queue.clear_queue()
        self.progress_display.set_status("Queue cleared")
        self._update_button_states()
    
    def _remove_selected(self):
        """Remove selected item from queue"""
        if self.download_queue.remove_selected_item():
            self._update_button_states()
    
    def _show_settings(self):
        """Show settings dialog"""
        self.settings_dialog = SettingsDialog(
            self.root, 
            self.config,
            save_callback=self._handle_settings_save
        )
        self.settings_dialog.show(self.auto_fetch_enabled)
    
    def _handle_settings_save(self, quality: str, output_dir: str, auto_fetch: bool):
        """Handle settings save"""
        self.auto_fetch_enabled = auto_fetch
        self.options_panel.set_quality(quality)
        self.options_panel.set_output_dir(output_dir)
        self.url_input.set_auto_fetch_enabled(auto_fetch)
    
    def _update_button_states(self):
        """Update button states based on current state"""
        has_queue = self.download_queue.has_items()
        has_selection = self.download_queue.has_selection()
        is_downloading = self.current_download is not None
        pending_items = self.download_queue.count_pending_items()
        
        self.control_buttons.update_button_states(has_queue, has_selection, is_downloading, pending_items)
    
    def _handle_info_message(self, message: str):
        """Handle info messages from downloader"""
        self.progress_display.set_status(message)
    
    def _handle_error_message(self, message: str):
        """Handle error messages from downloader"""
        messagebox.showerror("Download Error", message)
    
    def _handle_progress_update(self, message: str):
        """Handle progress updates from downloader"""
        # Parse progress from yt-dlp output
        percentage_match = re.search(r'(\d+(?:\.\d+)?)%', message)
        if percentage_match:
            progress = float(percentage_match.group(1))
            self.progress_display.set_progress(progress)
            
            if self.current_download:
                self.current_download.progress = progress
                self.download_queue.update_all_items()
        
        # Parse video title from yt-dlp output as fallback
        if self.current_download and self.current_download.title == "Unknown":
            title_patterns = [
                r'\[download\] Downloading video: (.+)',
                r'\[download\] (.+?)(?:\s+\[|$)',
                r'Downloading: (.+?)(?:\s+\[|$)',
                r'\[info\] (.+?):',
            ]
            
            for pattern in title_patterns:
                title_match = re.search(pattern, message)
                if title_match:
                    extracted_title = title_match.group(1).strip()
                    if (extracted_title and 
                        not extracted_title.startswith(('http', 'www.', 'Destination')) and
                        len(extracted_title) > 5 and
                        not extracted_title.endswith(('.m4a', '.mp4', '.mp3', '.webm'))):
                        self._update_item_metadata(self.current_download, extracted_title)
                        break
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()