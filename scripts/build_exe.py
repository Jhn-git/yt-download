#!/usr/bin/env python3
"""
Build script for creating YT-Download GUI executable
Uses PyInstaller to create a standalone executable
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path


def clean_build():
    """Clean previous build artifacts"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"Cleaning {dir_name}/...")
            shutil.rmtree(dir_name)
    
    # Clean .pyc files
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.pyc'):
                os.remove(os.path.join(root, file))


def get_platform_info():
    """Get platform-specific information"""
    system = platform.system()
    is_windows = system == "Windows"
    is_linux = system == "Linux"
    is_wsl = ("Microsoft" in platform.release() or "microsoft" in platform.release()) if is_linux else False
    
    # Determine executable name and binary
    if is_windows:
        exe_name = "YT-Download-GUI.exe"
        binary_name = "yt-dlp.exe"
    else:
        exe_name = "YT-Download-GUI"
        binary_name = "yt-dlp_linux"
    
    return {
        "system": system,
        "is_windows": is_windows,
        "is_linux": is_linux,
        "is_wsl": is_wsl,
        "exe_name": exe_name,
        "binary_name": binary_name
    }


def show_platform_warning(platform_info):
    """Show platform-specific warnings and instructions"""
    if platform_info["is_wsl"]:
        print("⚠️  WARNING: Building on WSL (Windows Subsystem for Linux)")
        print("   This will create a LINUX executable, not a Windows .exe")
        print("   To create Windows .exe:")
        print("   1. Copy project to Windows (not WSL)")
        print("   2. Install Python + PyInstaller on Windows")
        print("   3. Run: python build_exe.py")
        print()
    elif platform_info["is_linux"]:
        print("ℹ️  Building for Linux platform")
        print("   Output: Linux executable (no .exe extension)")
        print()
    elif platform_info["is_windows"]:
        print("ℹ️  Building for Windows platform")
        print("   Output: Windows .exe executable")
        print()


def build_executable(platform_info):
    """Build the executable using PyInstaller"""
    print("Building YT-Download GUI executable...")
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller', 
            'YT-Download-GUI.spec',
            '--clean'
        ], check=True, capture_output=True, text=True)
        
        print("Build completed successfully!")
        
        # Check if executable was created
        exe_path = Path(f'dist/{platform_info["exe_name"]}')
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Executable created: {exe_path}")
            print(f"Size: {size_mb:.1f} MB")
            print(f"Platform: {platform_info['system']}")
            
            # Make it executable on Unix systems
            if not platform_info["is_windows"]:
                exe_path.chmod(0o755)
                print("Executable permissions set")
        else:
            print("ERROR: Executable was not created!")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        return False
    
    return True


def main():
    """Main build process"""
    print("YT-Download GUI - Executable Builder")
    print("=" * 40)
    
    # Get platform information
    platform_info = get_platform_info()
    show_platform_warning(platform_info)
    
    # Check if PyInstaller is available
    try:
        subprocess.run([sys.executable, '-m', 'PyInstaller', '--version'], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("ERROR: PyInstaller is not installed!")
        if platform_info["is_windows"]:
            print("Install with: pip install pyinstaller")
        else:
            print("Install with: pip install pyinstaller")
        return 1
    
    # Check required files (platform-specific)
    required_files = ['ytdl_gui.py', 'YT-Download-GUI.spec', 'config.json']
    
    # Add platform-specific binary
    if os.path.exists(platform_info["binary_name"]):
        required_files.append(platform_info["binary_name"])
    elif os.path.exists("yt-dlp_linux"):
        required_files.append("yt-dlp_linux")  # Fallback
        print(f"⚠️  Using yt-dlp_linux instead of {platform_info['binary_name']}")
    else:
        print(f"ERROR: No yt-dlp binary found!")
        print(f"Expected: {platform_info['binary_name']} or yt-dlp_linux")
        return 1
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("ERROR: Missing required files:")
        for file in missing_files:
            print(f"  - {file}")
        return 1
    
    # Clean previous builds
    clean_build()
    
    # Build executable
    if not build_executable(platform_info):
        return 1
    
    print("\n" + "=" * 40)
    print("Build completed successfully!")
    
    if platform_info["is_windows"]:
        print("Run with: dist\\YT-Download-GUI.exe")
    else:
        print("Run with: ./dist/YT-Download-GUI")
    
    if platform_info["is_wsl"]:
        print("\n⚠️  REMINDER: This is a Linux executable!")
        print("   It will NOT run on Windows outside WSL.")
        print("   For Windows users, build on native Windows.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())