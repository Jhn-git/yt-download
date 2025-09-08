"""Utility functions for the GUI"""

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