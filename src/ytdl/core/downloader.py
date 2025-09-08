import subprocess
import os
import sys
import re
from typing import List, Optional, Protocol
from .config import ConfigService


class OutputHandler(Protocol):
    """Protocol for output handling.
    
    Defines interface for outputting info and error messages.
    """
    def info(self, message: str): ...
    def error(self, message: str): ...


class ConsoleOutputHandler:
    """Console-based output handler implementation."""
    
    def info(self, message: str):
        print(f"INFO: {message}")
    
    def error(self, message: str):
        print(f"ERROR: {message}")


class DownloaderService:
    """Service for downloading videos using yt-dlp.
    
    Handles video downloads with real-time progress display, quality selection,
    and configurable output directories. Integrates with yt-dlp binary via subprocess.
    """
    
    def __init__(self, config: ConfigService, output_handler: OutputHandler = None):
        """Initialize downloader service.
        
        Args:
            config: Configuration service instance
            output_handler: Output handler for messages (default: ConsoleOutputHandler)
        """
        self.config = config
        self.output_handler = output_handler or ConsoleOutputHandler()
    
    def download(self, url: str, output_dir: Optional[str] = None, quality: Optional[str] = None) -> bool:
        """Download video from URL.
        
        Args:
            url: Video URL to download
            output_dir: Output directory (uses config default if None)
            quality: Video quality (uses config default if None)
            
        Returns:
            True if download succeeded, False otherwise
        """
        try:
            cmd = self._build_command(url, output_dir, quality)
            self.output_handler.info(f"Downloading: {url}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=os.getcwd()
            )
            
            # Stream output in real-time with smart progress handling
            last_progress_line = None
            for line in process.stdout:
                line = line.rstrip()
                if self._is_progress_line(line):
                    # Store progress line, only show the latest one
                    last_progress_line = line
                    print(f"\r{line}", end="", flush=True)
                else:
                    # Non-progress lines: print normally
                    # If we had a progress line, add newline first
                    if last_progress_line:
                        print()  # Add newline after the last progress line
                        last_progress_line = None
                    print(line)
            
            # Ensure we end with a newline after the final progress line
            if last_progress_line:
                print()  # Final newline after progress
            
            # Wait for process to complete and get return code
            return_code = process.wait()
            
            if return_code == 0:
                self.output_handler.info("Download completed successfully")
                return True
            else:
                self.output_handler.error("Download failed")
                return False
                
        except Exception as e:
            self.output_handler.error(f"Error during download: {str(e)}")
            return False
    
    def _build_command(self, url: str, output_dir: Optional[str] = None, quality: Optional[str] = None) -> List[str]:
        cmd = [self.config.ytdlp_binary]
        
        download_dir = output_dir or self.config.download_dir
        os.makedirs(download_dir, exist_ok=True)
        cmd.extend(["-o", f"{download_dir}/%(title)s.%(ext)s"])
        
        # Build format selector to prefer MP4 but ensure we get the requested quality
        format_quality = quality or self.config.quality
        target_format = self.config.format.lower()
        
        if target_format == "mp4":
            if format_quality == "best":
                # Prefer MP4 containers, but fallback to any format
                cmd.extend(["-f", "bv[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv+ba/b"])
            else:
                # Parse height from quality like "720p", "1080p" etc.
                if format_quality.endswith('p') and format_quality[:-1].isdigit():
                    height = format_quality[:-1]
                    cmd.extend(["-f", f"bv[height<={height}][ext=mp4]+ba[ext=m4a]/bv[height<={height}]+ba/b[height<={height}]"])
                else:
                    # For non-standard quality formats, use as-is
                    cmd.extend(["-f", format_quality])
            
            # Always remux/convert to MP4 if we didn't get MP4 initially
            cmd.extend(["--remux-video", "mp4"])
        else:
            # Use original behavior for non-MP4 formats
            if format_quality != "best":
                cmd.extend(["-f", format_quality])
        
        cmd.append(url)
        return cmd
    
    def _is_progress_line(self, line: str) -> bool:
        """
        Detect if a line is a progress update from yt-dlp.
        Progress lines typically start with [download] and contain percentage.
        """
        if not line.startswith('[download]'):
            return False
        
        # Look for percentage pattern (e.g., "23.6%", "100%")
        # Allow optional whitespace before percentage
        percentage_pattern = r'\s*\d+(?:\.\d+)?%'
        return bool(re.search(percentage_pattern, line))
    
    def get_info(self, url: str) -> Optional[dict]:
        """Get video information without downloading.
        
        Args:
            url: Video URL to get information for
            
        Returns:
            Dictionary with video information or None if failed
        """
        try:
            cmd = [self.config.ytdlp_binary, "--dump-json", url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout.strip())
            return None
        except Exception:
            return None