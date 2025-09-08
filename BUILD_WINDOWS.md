# Building Windows Executable

This guide shows how to create a Windows `.exe` file for the YT-Download GUI.

## ⚠️ Important: Platform Requirements

- **Windows executable (.exe)**: Must be built on **native Windows**
- **Linux executable**: Must be built on **Linux**
- **Cross-compilation is NOT supported** by PyInstaller

## Quick Start (Windows)

### Option 1: Automated Script
```cmd
# Run the Windows build script
build_exe.bat
```

### Option 2: Manual Build
```cmd
# Install PyInstaller
pip install pyinstaller

# Build executable
python build_exe.py

# Or use PyInstaller directly
pyinstaller YT-Download-GUI.spec
```

## Detailed Windows Setup

### 1. Prerequisites
- **Windows 10/11** (native Windows, not WSL)
- **Python 3.8+** installed from [python.org](https://python.org)
- **Git** (to clone the repository)

### 2. Clone and Setup
```cmd
# Clone repository
git clone <repository-url>
cd yt-download

# Install build dependencies
pip install pyinstaller
```

### 3. Get yt-dlp Windows Binary
The project includes `yt-dlp_linux` but Windows needs `yt-dlp.exe`:

```cmd
# Download yt-dlp for Windows
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe -o yt-dlp.exe

# Or use PowerShell
Invoke-WebRequest -Uri "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe" -OutFile "yt-dlp.exe"
```

### 4. Build Executable
```cmd
# Option A: Use build script (recommended)
python build_exe.py

# Option B: Use batch script
build_exe.bat

# Option C: Manual PyInstaller
pyinstaller YT-Download-GUI.spec --clean
```

### 5. Test Executable
```cmd
# Run the created executable
dist\YT-Download-GUI.exe
```

## Troubleshooting

### Common Issues

**"This will create a LINUX executable, not a Windows .exe"**
- You're building on WSL/Linux
- Copy files to native Windows and build there

**"No yt-dlp binary found!"**
- Download `yt-dlp.exe` as shown above
- Place it in the project root directory

**"PyInstaller is not installed"**
```cmd
pip install pyinstaller
```

**"Python is not recognized"**
- Install Python from [python.org](https://python.org)
- Check "Add Python to PATH" during installation
- Restart command prompt

### Binary Size
- Expected size: ~45-50 MB
- Includes Python runtime + GUI + yt-dlp binary
- Single file, no dependencies required

## Distribution

The created `YT-Download-GUI.exe` file is completely standalone:
- ✅ No Python installation required
- ✅ No additional dependencies
- ✅ Can be copied to any Windows machine
- ✅ Includes all necessary components

## Advanced: GitHub Actions (Future)

For automated multi-platform builds, consider setting up GitHub Actions:
- Builds Windows .exe, Linux binary, and macOS app
- Automatically publishes releases
- Ensures all platforms are properly supported