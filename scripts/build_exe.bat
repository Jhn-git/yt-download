@echo off
REM Windows batch script for building YT-Download GUI executable
REM Run this on native Windows (not WSL)

echo YT-Download GUI - Windows Executable Builder
echo ============================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

REM Check if PyInstaller is available
python -m PyInstaller --version >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller!
        pause
        exit /b 1
    )
)

REM Check required files
echo Checking required files...
if not exist "ytdl_gui.py" (
    echo ERROR: ytdl_gui.py not found!
    pause
    exit /b 1
)

if not exist "YT-Download-GUI.spec" (
    echo ERROR: YT-Download-GUI.spec not found!
    pause
    exit /b 1
)

if not exist "config.json" (
    echo ERROR: config.json not found!
    pause
    exit /b 1
)

REM Check for yt-dlp binary (Windows version)
if exist "yt-dlp.exe" (
    echo Found yt-dlp.exe
) else if exist "yt-dlp_linux" (
    echo WARNING: Found yt-dlp_linux instead of yt-dlp.exe
    echo This may cause issues on Windows
) else (
    echo ERROR: No yt-dlp binary found!
    echo Please download yt-dlp.exe from https://github.com/yt-dlp/yt-dlp
    pause
    exit /b 1
)

echo.
echo Building Windows executable...
echo.

REM Clean previous builds
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"

REM Build executable
python -m PyInstaller YT-Download-GUI.spec --clean

if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Check if executable was created
if exist "dist\YT-Download-GUI.exe" (
    echo.
    echo ============================================
    echo Build completed successfully!
    echo Executable: dist\YT-Download-GUI.exe
    
    REM Get file size
    for %%A in ("dist\YT-Download-GUI.exe") do (
        set /a size_mb=%%~zA/1024/1024
        echo Size: !size_mb! MB
    )
    
    echo.
    echo To run: dist\YT-Download-GUI.exe
    echo.
) else (
    echo ERROR: Executable was not created!
    pause
    exit /b 1
)

pause