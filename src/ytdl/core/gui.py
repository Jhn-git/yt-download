import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import re
import os
import tempfile
from typing import List, Dict, Optional
from .config import ConfigService
from .downloader import DownloaderService
from .logger import LoggerService
from .gui_output import GUIOutputHandler, GUILogger

try:
    from PIL import Image, ImageTk
    import urllib.request
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable string"""
    if not size_bytes:
        return "Unknown"
    
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def is_valid_url(url: str) -> bool:
    """Check if URL appears to be a valid video URL"""
    if not url or not url.strip():
        return False
    
    url = url.strip()
    
    # Basic URL validation
    if not url.startswith(('http://', 'https://')):
        return False
    
    # Check for common video platforms
    video_domains = [
        'youtube.com', 'youtu.be', 'vimeo.com', 'dailymotion.com', 
        'twitch.tv', 'tiktok.com', 'instagram.com', 'twitter.com', 'x.com'
    ]
    
    for domain in video_domains:
        if domain in url.lower():
            return True
    
    # If it looks like a URL but not a known video platform, still consider it valid
    # yt-dlp supports many platforms
    return '.' in url and len(url) > 10


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
        self.thumbnail_url = None
        self.thumbnail_image = None  # PIL Image for display
        self.tree_item_id = None  # Store reference to GUI tree item
    
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


class GUIService:
    """Main GUI service for the YouTube downloader"""
    
    def __init__(self, config: ConfigService, downloader: DownloaderService, logger: LoggerService):
        self.config = config
        self.downloader = downloader
        self.logger = logger
        self.download_queue: List[DownloadItem] = []
        self.current_download: Optional[DownloadItem] = None
        
        # Thumbnail cache management (for future implementation)
        self.thumbnail_cache: Dict[str, tk.PhotoImage] = {}
        self.thumbnail_temp_dir = tempfile.mkdtemp() if HAS_PILLOW else None
        self.placeholder_image = None
        
        # Auto-fetch functionality
        self.auto_fetch_enabled = True  # User preference
        self.auto_fetch_timer = None
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("YT-Download GUI")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        self._setup_gui()
        self._setup_gui_output_handler()
    
    def _setup_gui_output_handler(self):
        """Setup GUI output handler for downloader feedback"""
        self.gui_output = GUIOutputHandler(
            info_callback=self._handle_info_message,
            error_callback=self._handle_error_message,
            progress_callback=self._handle_progress_update
        )
        
        # Replace downloader's output handler
        self.downloader.output_handler = self.gui_output
    
    def _setup_gui(self):
        """Create and setup the GUI layout"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # URL input section
        url_frame = ttk.LabelFrame(main_frame, text="Download", padding="5")
        url_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        self.url_entry.bind('<Return>', lambda e: self._add_to_queue())
        
        # Add auto-fetch functionality with debouncing
        self.url_var.trace('w', self._on_url_change)
        
        ttk.Button(url_frame, text="Info", command=self._show_video_info).grid(row=0, column=2, padx=(0, 5))
        ttk.Button(url_frame, text="Add", command=self._add_to_queue).grid(row=0, column=3)
        
        # Quality and output selection
        options_frame = ttk.Frame(main_frame)
        options_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(2, weight=1)
        
        ttk.Label(options_frame, text="Quality:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.quality_var = tk.StringVar(value=self.config.quality)
        quality_combo = ttk.Combobox(options_frame, textvariable=self.quality_var, 
                                   values=["best", "720p", "1080p", "480p", "worst", "bestaudio/best"], 
                                   state="readonly", width=15)
        quality_combo.grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(options_frame, text="Output:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.output_var = tk.StringVar(value=self.config.download_dir)
        self.output_entry = ttk.Entry(options_frame, textvariable=self.output_var, width=30)
        self.output_entry.grid(row=0, column=3, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(options_frame, text="Browse", command=self._browse_output_dir).grid(row=0, column=4)
        
        # Download queue
        queue_frame = ttk.LabelFrame(main_frame, text="Download Queue", padding="5")
        queue_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        queue_frame.columnconfigure(0, weight=1)
        queue_frame.rowconfigure(0, weight=1)
        
        # Treeview for queue
        columns = ("URL", "Channel", "Size", "Quality", "Status", "Progress")
        self.queue_tree = ttk.Treeview(queue_frame, columns=columns, show="tree headings", height=8)
        
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
        
        # Bind selection change event to update button states
        self.queue_tree.bind('<<TreeviewSelect>>', lambda e: self._update_button_states())
        
        # Queue scrollbar
        queue_scrollbar = ttk.Scrollbar(queue_frame, orient="vertical", command=self.queue_tree.yview)
        queue_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.queue_tree.configure(yscrollcommand=queue_scrollbar.set)
        
        # Progress bar
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="Ready")
        self.progress_label.grid(row=0, column=1)
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        
        self.start_button = ttk.Button(button_frame, text="Start All", command=self._start_downloads)
        self.start_button.grid(row=0, column=0, padx=(0, 5))
        
        self.clear_button = ttk.Button(button_frame, text="Clear Queue", command=self._clear_queue)
        self.clear_button.grid(row=0, column=1, padx=(0, 5))
        
        self.remove_button = ttk.Button(button_frame, text="Remove Selected", command=self._remove_selected)
        self.remove_button.grid(row=0, column=2, padx=(0, 20))
        
        # Spacer
        button_frame.columnconfigure(3, weight=1)
        
        ttk.Button(button_frame, text="Settings", command=self._show_settings).grid(row=0, column=4, padx=(0, 5))
        ttk.Button(button_frame, text="Exit", command=self.root.quit).grid(row=0, column=5)
        
        # Configure main grid weights for resizing
        main_frame.rowconfigure(2, weight=1)
        
        # Initialize button states
        self._update_button_states()
    
    def _update_button_states(self):
        """Update button states based on current queue and download status"""
        has_queue = len(self.download_queue) > 0
        has_selection = len(self.queue_tree.selection()) > 0
        is_downloading = self.current_download is not None
        
        # Count pending items (not completed or failed)
        pending_items = sum(1 for item in self.download_queue if item.status == "Queued")
        
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
    
    def _on_url_change(self, *args):
        """Handle URL entry changes for auto-fetch functionality"""
        if not self.auto_fetch_enabled:
            return
        
        # Cancel any existing timer
        if self.auto_fetch_timer:
            self.root.after_cancel(self.auto_fetch_timer)
        
        # Set up a new timer for debounced auto-fetch
        self.auto_fetch_timer = self.root.after(1000, self._auto_fetch_info)  # 1 second delay
    
    def _auto_fetch_info(self):
        """Auto-fetch video information if URL appears valid"""
        url = self.url_var.get().strip()
        
        if not url or not is_valid_url(url):
            return
        
        # Only auto-fetch if not already in queue and URL looks complete
        if any(item.url == url for item in self.download_queue):
            return
        
        # Auto-add to queue if URL appears valid and complete
        if len(url) > 20:  # Reasonable minimum length for a complete URL
            self._add_to_queue()
    
    def _add_to_queue(self):
        """Add current URL to download queue with async title fetching"""
        url = self.url_var.get().strip()
        if not url:
            return
        
        if not url.startswith(('http://', 'https://')):
            messagebox.showerror("Invalid URL", "Please enter a valid URL starting with http:// or https://")
            return
        
        quality = self.quality_var.get()
        output_dir = self.output_var.get()
        
        # Create download item and add to queue immediately
        item = DownloadItem(url, quality, output_dir)
        self.download_queue.append(item)
        
        # Add to treeview with initial "Unknown" values
        item_id = self.queue_tree.insert("", "end", text="Fetching title...", 
                                       values=(url[:30] + "..." if len(url) > 30 else url,
                                              "Fetching...", "Fetching...", quality, item.status, "0%"))
        item.tree_item_id = item_id
        
        # Clear URL entry
        self.url_var.set("")
        self.status_var.set(f"Fetching video info... ({len(self.download_queue)} items in queue)")
        
        # Fetch title asynchronously with timeout handling
        def fetch_title():
            try:
                # Set a reasonable timeout for metadata fetching
                import signal
                
                def timeout_handler(signum, frame):
                    raise TimeoutError("Metadata fetch timeout")
                
                # Only use signal timeout on Unix systems
                if hasattr(signal, 'SIGALRM'):
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(10)  # 10 second timeout
                
                info = self.downloader.get_info(url)
                
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
                    
                    # Update the download item and GUI on main thread
                    self.root.after(0, lambda: self._update_item_metadata(item, title, channel, file_size))
                else:
                    # Fallback if no metadata found
                    self.root.after(0, lambda: self._update_item_metadata(item, "Unknown", "Unknown", "Unknown"))
            except (Exception, TimeoutError) as e:
                # Error or timeout fetching title - keep as "Unknown"
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)  # Cancel timeout
                self.root.after(0, lambda: self._update_item_metadata(item, "Unknown", "Unknown", "Unknown"))
        
        # Start title fetching in background thread
        threading.Thread(target=fetch_title, daemon=True).start()
        
        # Update button states
        self._update_button_states()
    
    def _update_item_metadata(self, item: DownloadItem, title: str, channel: str = None, file_size: str = None):
        """Update download item metadata in both data structure and GUI"""
        item.update_metadata(title, channel, file_size)
        
        # Update the treeview display
        if item.tree_item_id:
            self.queue_tree.item(item.tree_item_id, text=item.title)
            # Update the channel and size columns
            current_values = list(self.queue_tree.set(item.tree_item_id).values())
            if len(current_values) >= 6:
                current_values[1] = item.channel  # Channel column
                current_values[2] = item.file_size  # Size column
                self.queue_tree.item(item.tree_item_id, values=current_values)
        
        # Update status message
        self.status_var.set(f"Ready - {len(self.download_queue)} items in queue")
        
        # Update button states
        self._update_button_states()
    
    def _update_item_title(self, item: DownloadItem, title: str):
        """Backward compatibility method - delegates to _update_item_metadata"""
        self._update_item_metadata(item, title)
    
    def _show_video_info(self):
        """Show video information without downloading"""
        url = self.url_var.get().strip()
        if not url:
            return
        
        def fetch_info():
            info = self.downloader.get_info(url)
            if info:
                self.root.after(0, lambda: self._display_video_info(info))
            else:
                self.root.after(0, lambda: messagebox.showerror("Error", "Could not fetch video information"))
        
        self.status_var.set("Fetching video information...")
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def _display_video_info(self, info: dict):
        """Display video information in a popup"""
        info_window = tk.Toplevel(self.root)
        info_window.title("Video Information")
        info_window.geometry("500x300")
        
        frame = ttk.Frame(info_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        info_text = tk.Text(frame, wrap=tk.WORD, height=15)
        info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=info_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        info_text.configure(yscrollcommand=scrollbar.set)
        
        # Format info
        info_content = f"""Title: {info.get('title', 'Unknown')}
Duration: {info.get('duration', 'Unknown')} seconds
Uploader: {info.get('uploader', 'Unknown')}
View Count: {info.get('view_count', 'Unknown')}
Upload Date: {info.get('upload_date', 'Unknown')}
Description: {info.get('description', 'No description')[:500]}..."""
        
        info_text.insert("1.0", info_content)
        info_text.configure(state="disabled")
        
        info_window.columnconfigure(0, weight=1)
        info_window.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
        
        self.status_var.set("Ready")
    
    def _browse_output_dir(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(initialdir=self.output_var.get())
        if directory:
            self.output_var.set(directory)
    
    def _start_downloads(self):
        """Start downloading all queued items"""
        if not self.download_queue:
            return
        
        if self.current_download:
            messagebox.showinfo("Download in Progress", "A download is already in progress")
            return
        
        def download_worker():
            # Update button states at start of downloads
            self.root.after(0, self._update_button_states)
            
            for item in self.download_queue:
                if item.status == "Queued":
                    self.current_download = item
                    self.root.after(0, lambda: self.status_var.set(f"Downloading: {item.url}"))
                    self.root.after(0, self._update_button_states)
                    
                    item.status = "Downloading"
                    self._update_queue_display()
                    
                    success = self.downloader.download(item.url, item.output_dir or None, item.quality)
                    
                    if success:
                        item.status = "Complete"
                        item.progress = 100
                    else:
                        item.status = "Failed"
                    
                    self._update_queue_display()
                    self.root.after(0, self._update_button_states)
            
            self.current_download = None
            self.root.after(0, lambda: self.status_var.set("All downloads completed"))
            self.root.after(0, lambda: self.progress_var.set(0))
            self.root.after(0, self._update_button_states)
        
        threading.Thread(target=download_worker, daemon=True).start()
    
    def _clear_queue(self):
        """Clear the download queue"""
        self.download_queue.clear()
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
        self.status_var.set("Queue cleared")
        self._update_button_states()
    
    def _remove_selected(self):
        """Remove selected item from queue"""
        selection = self.queue_tree.selection()
        if not selection:
            return
        
        # Get index of selected item
        item_id = selection[0]
        index = self.queue_tree.index(item_id)
        
        # Remove from queue and treeview
        if 0 <= index < len(self.download_queue):
            del self.download_queue[index]
        self.queue_tree.delete(item_id)
        self._update_button_states()
    
    def _show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.grab_set()
        
        frame = ttk.Frame(settings_window, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Default quality
        ttk.Label(frame, text="Default Quality:").grid(row=0, column=0, sticky=tk.W, pady=5)
        quality_var = tk.StringVar(value=self.config.quality)
        quality_combo = ttk.Combobox(frame, textvariable=quality_var, 
                                   values=["best", "720p", "1080p", "480p", "worst"], 
                                   state="readonly")
        quality_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Default output directory
        ttk.Label(frame, text="Default Output:").grid(row=1, column=0, sticky=tk.W, pady=5)
        output_var = tk.StringVar(value=self.config.download_dir)
        output_entry = ttk.Entry(frame, textvariable=output_var)
        output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(5, 0))
        
        # Auto-fetch setting
        auto_fetch_var = tk.BooleanVar(value=self.auto_fetch_enabled)
        auto_fetch_check = ttk.Checkbutton(frame, text="Auto-fetch video info when URL is pasted", 
                                         variable=auto_fetch_var)
        auto_fetch_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        def save_settings():
            self.config.quality = quality_var.get()
            self.config.download_dir = output_var.get()
            self.auto_fetch_enabled = auto_fetch_var.get()
            self.quality_var.set(quality_var.get())
            self.output_var.set(output_var.get())
            settings_window.destroy()
        
        ttk.Button(button_frame, text="Save", command=save_settings).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).grid(row=0, column=1)
        
        frame.columnconfigure(1, weight=1)
    
    def _update_queue_display(self):
        """Update the queue display in the treeview"""
        def update():
            for i, (item_id, item) in enumerate(zip(self.queue_tree.get_children(), self.download_queue)):
                # Update title
                self.queue_tree.item(item_id, text=item.title)
                # Update all columns
                self.queue_tree.set(item_id, "Channel", item.channel)
                self.queue_tree.set(item_id, "Size", item.file_size)
                self.queue_tree.set(item_id, "Status", item.status)
                self.queue_tree.set(item_id, "Progress", f"{item.progress}%")
        
        self.root.after(0, update)
    
    def _handle_info_message(self, message: str):
        """Handle info messages from downloader"""
        self.status_var.set(message)
    
    def _handle_error_message(self, message: str):
        """Handle error messages from downloader"""
        messagebox.showerror("Download Error", message)
    
    def _handle_progress_update(self, message: str):
        """Handle progress updates from downloader"""
        # Parse progress from yt-dlp output
        percentage_match = re.search(r'(\d+(?:\.\d+)?)%', message)
        if percentage_match:
            progress = float(percentage_match.group(1))
            self.progress_var.set(progress)
            self.progress_label.config(text=f"{progress:.1f}%")
            
            if self.current_download:
                self.current_download.progress = progress
                self._update_queue_display()
        
        # Parse video title from yt-dlp output as fallback
        # Look for lines like "[download] Downloading video: Title" or "[download] Title"
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
                    # Filter out common non-title patterns
                    if (extracted_title and 
                        not extracted_title.startswith(('http', 'www.', 'Destination')) and
                        len(extracted_title) > 5 and
                        not extracted_title.endswith(('.m4a', '.mp4', '.mp3', '.webm'))):
                        self._update_item_title(self.current_download, extracted_title)
                        break
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()