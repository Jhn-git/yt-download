"""Utility functions for the GUI"""

import os
import platform
import subprocess
from pathlib import Path

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


def open_folder(folder_path: str) -> bool:
    """
    Open a folder in the system's default file manager.
    
    Args:
        folder_path: Path to the folder to open
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Convert to Path object and resolve to absolute path
        path = Path(folder_path).resolve()
        
        # Check if path exists
        if not path.exists():
            return False
        
        # Ensure it's a directory
        if not path.is_dir():
            # If it's a file, open the parent directory
            path = path.parent
        
        # Cross-platform folder opening
        system = platform.system().lower()
        
        if system == "windows":
            # Use os.startfile for Windows (works in both native Windows and WSL)
            os.startfile(str(path))
        elif system == "linux":
            # Use xdg-open for Linux
            subprocess.run(["xdg-open", str(path)], check=True)
        elif system == "darwin":  # macOS
            # Use open command for macOS
            subprocess.run(["open", str(path)], check=True)
        else:
            # Fallback: try xdg-open for other Unix-like systems
            subprocess.run(["xdg-open", str(path)], check=True)
        
        return True
        
    except (OSError, subprocess.CalledProcessError, FileNotFoundError):
        return False