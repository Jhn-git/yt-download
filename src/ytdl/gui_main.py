#!/usr/bin/env python3
"""
GUI entry point for YT-Download
Launches the tkinter-based graphical user interface
"""
import sys
import os
import tkinter as tk
from tkinter import messagebox

from ytdl.core.config import ConfigService
from ytdl.core.downloader import DownloaderService
from ytdl.core.logger import LoggerService
from ytdl.gui import GUIService


def show_error_dialog(title: str, message: str):
    """Show error dialog for GUI applications, fallback to console for CLI"""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller executable - use GUI dialog
        try:
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror(title, message)
            root.destroy()
            return
        except Exception:
            # Fallback to console if GUI fails
            pass
    
    # Running in development or GUI dialog failed - use console
    print(f"{title}: {message}")
    if not getattr(sys, 'frozen', False):
        input("Press Enter to exit...")


def validate_binary(config: ConfigService, logger: LoggerService) -> bool:
    """Validate that the required yt-dlp binary exists and is executable"""
    binary_path = config.get("ytdlp_binary", "./binaries/yt-dlp.exe")
    
    
    if not os.path.exists(binary_path):
        error_msg = f"Required binary not found: {binary_path}"
        logger.error(f"ERROR: {error_msg}")
        
        if binary_path.endswith(".exe"):
            detailed_msg = f"{error_msg}\n\nPlease download yt-dlp.exe from https://github.com/yt-dlp/yt-dlp and place it in the same directory as this executable."
        else:
            detailed_msg = error_msg
            
        show_error_dialog("Binary Not Found", detailed_msg)
        return False
    
    # Check if file is executable (on Windows, .exe files are inherently executable)
    if not os.access(binary_path, os.X_OK):
        error_msg = f"Binary is not executable: {binary_path}"
        logger.error(f"ERROR: {error_msg}")
        show_error_dialog("Binary Not Executable", error_msg)
        return False
    
    logger.info(f"Binary validation successful: {binary_path}")
    return True


def main():
    """Initialize services and launch GUI"""
    try:
        # Initialize services with dependency injection
        config = ConfigService()
        logger = LoggerService(
            level=config.get("log_level", "INFO"),
            log_file=config.get("log_file")
        )
        
        # Validate required binary before proceeding
        if not validate_binary(config, logger):
            # Error dialog already shown in validate_binary function
            return 1
        
        downloader = DownloaderService(config, logger)
        
        # Create and run GUI
        gui = GUIService(config, downloader, logger)
        gui.run()
        
        return 0
    
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 130
    
    except Exception as e:
        error_msg = f"Failed to start GUI application: {e}"
        
        # If running as executable, also write to log
        if getattr(sys, 'frozen', False):
            try:
                with open("ytdl_error.log", "w") as f:
                    import traceback
                    f.write(f"Error starting YT-Download GUI:\n{error_msg}\n\n")
                    f.write("Full traceback:\n")
                    traceback.print_exc(file=f)
                detailed_error = f"{error_msg}\n\nError details written to: ytdl_error.log"
            except:
                detailed_error = error_msg
        else:
            detailed_error = error_msg
            
        show_error_dialog("Application Error", detailed_error)
        return 1


if __name__ == "__main__":
    sys.exit(main())