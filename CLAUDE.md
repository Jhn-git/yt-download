# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a modular YouTube downloader CLI built with dependency injection for testability and extensibility.

### Core Services
- **ConfigService** (`src/ytdl/core/config.py`): JSON-based configuration management with defaults
- **DownloaderService** (`src/ytdl/core/downloader.py`): Wraps yt-dlp_linux binary calls via subprocess
- **CLIService** (`src/ytdl/core/cli.py`): Argument parsing and user interaction
- **GUIService** (`src/ytdl/core/gui.py`): Tkinter-based graphical user interface
- **LoggerService** (`src/ytdl/core/logger.py`): Structured logging with console/file output

### Dependency Flow
```
main() → ConfigService → LoggerService → DownloaderService → CLIService
```

All services use constructor injection. OutputHandler protocol enables mocking for tests.

## Environment
- **Platform**: WSL2 on Windows 11
- **Python**: 3.10.18 (default)
- **Binary**: `./binaries/yt-dlp_linux` (included, executable)
- **Dependencies**: ffmpeg (system-installed)

## Common Commands

### Running the Tool

**GUI Application** (Recommended):
```bash
# Convenience script (easiest)
python run_gui.py

# Or directly from source
python src/ytdl/gui_main.py

# Or using setup.py entry points (after pip install -e .)
ytdl-gui

# Or using backward-compatible wrapper
python wrappers/ytdl_gui.py
```

**Command Line**:
```bash
# Convenience script (easiest)
python run_cli.py "https://youtube.com/watch?v=VIDEO_ID"

# Or directly from source
python src/ytdl/main.py "https://youtube.com/watch?v=VIDEO_ID"

# Or using setup.py entry points (after pip install -e .)
ytdl "https://youtube.com/watch?v=VIDEO_ID"

# Or using backward-compatible wrapper
python wrappers/ytdl.py "https://youtube.com/watch?v=VIDEO_ID"

# With quality and output directory
ytdl -q 720p -o ~/Videos "URL"

# Audio only
ytdl --audio-only "URL"

# Show info without downloading
ytdl --info "URL"

# Interactive mode for multiple downloads
ytdl -i
ytdl -i -q 720p -o ~/Videos  # with preset settings
```

### Development

**First-Time Setup:**
```bash
# Install build dependencies (if needed)
pip install setuptools wheel

# Install package in development mode
pip install -e .
```

**Usage Options:**
```bash
# Option 1: Use installed console scripts (recommended)
ytdl --help
ytdl-gui  # Launch GUI for testing
ytdl --info "https://youtube.com/watch?v=dQw4w9WgXcQ"

# Option 2: Use root-level convenience scripts (development)
python run_cli.py --help
python run_gui.py

# Option 3: Use backward-compatible wrapper scripts
python wrappers/ytdl.py --help
python wrappers/ytdl_gui.py

# Option 4: Run directly from source
python src/ytdl/main.py --help
python src/ytdl/gui_main.py
```

**Windows-Specific Notes:**
- Ensure `binaries/yt-dlp.exe` exists (download from https://github.com/yt-dlp/yt-dlp)
- Use `python -m pip` if `pip` command is not available
- On Windows, the config defaults to `./binaries/yt-dlp.exe`

### Building Executable

**⚠️ Platform-Specific Building Required:**
- **Windows .exe**: Must build on native Windows (see [BUILD_WINDOWS.md](BUILD_WINDOWS.md))
- **Linux executable**: Must build on Linux
- **Cross-compilation NOT supported**

**Linux Build:**
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable (with platform detection)
python scripts/build_exe.py

# Or build manually
pyinstaller YT-Download-GUI.spec

# Run Linux executable
./dist/YT-Download-GUI
```

**Windows Build:**
```cmd
REM On native Windows (not WSL):
REM 1. Download yt-dlp.exe to binaries/ directory
REM 2. Run build script
scripts\build_exe.bat

REM Or use Python script
python scripts/build_exe.py

REM Run Windows executable
dist\YT-Download-GUI.exe
```

**Executable Features:**
- **Single file**: ~45MB standalone executable  
- **No dependencies**: Includes Python runtime + yt-dlp binary
- **Platform-specific**: Optimized for target OS
- **All functionality**: Complete GUI with download queue, progress, settings

**Current Build:** Linux executable (ELF format) - runs on Linux/WSL only

### Testing

**Framework**: Python unittest with comprehensive test suite (86 tests)
**Coverage**: Unit tests for all services + integration tests
**Location**: `tests/` directory with dedicated test runner

```bash
# Run all tests
python tools/run_tests.py

# Run specific test module
python tools/run_tests.py config
python tools/run_tests.py downloader

# Run with verbose output
python tools/run_tests.py -v

# List available tests
python tools/run_tests.py --list
```

**Test Structure**: Services accept dependencies via constructor, making them easily mockable:
```python
# Example test setup
mock_config = Mock()
mock_output = Mock(spec=OutputHandler)
service = DownloaderService(mock_config, mock_output)
```

## Configuration
- **File**: `config/config.json` (JSON format)
- **Local overrides**: `config/config_local.json` (gitignored)
- **Key settings**: download_dir, quality, ytdlp_binary path, log_level

## Important Files

### Package Structure
- `src/ytdl/main.py`: CLI entry point with dependency wiring
- `src/ytdl/gui_main.py`: GUI entry point (tkinter-based interface)
- `src/ytdl/core/downloader.py`: Core download logic and yt-dlp integration
- `src/ytdl/core/gui.py`: GUI service with tkinter interface
- `src/ytdl/core/gui_output.py`: GUI output handlers for progress/status updates
- `setup.py`: Package configuration with console script entry points

### Configuration & Build
- `config/config.json`: Default configuration
- `config/YT-Download-GUI.spec`: PyInstaller specification (cross-platform)
- `scripts/build_exe.py`: Cross-platform executable build script
- `scripts/build_exe.bat`: Windows batch build script
- `scripts/debug_windows.py`: Windows debugging script

### Documentation
- `docs/BUILD_WINDOWS.md`: Detailed Windows build instructions
- `docs/CONTRIBUTING.md`: Contribution guidelines
- `docs/FEATURES.md`: Feature documentation
- `docs/USAGE.md`: Usage instructions

### Convenience Scripts & Wrappers
- `run_cli.py`: Root-level CLI launcher
- `run_gui.py`: Root-level GUI launcher
- `wrappers/ytdl.py`: Backward-compatible CLI wrapper
- `wrappers/ytdl_gui.py`: Backward-compatible GUI wrapper

### Testing & Tools
- `tools/run_tests.py`: Test runner with multiple execution options
- `tests/`: Comprehensive test suite (unit + integration tests)
- `binaries/`: External binaries (yt-dlp_linux, yt-dlp.exe)

## Troubleshooting

### Common Installation Issues

**"ModuleNotFoundError: No module named 'ytdl'"**
```bash
# Solution: Install the package in development mode
pip install -e .

# Or use wrapper scripts as fallback
python ytdl_gui.py
```

**"ModuleNotFoundError: No module named 'setuptools'"**
```bash
# Solution: Install setuptools
pip install setuptools wheel
```

**"ERROR: Required binary not found" (RESOLVED as of Sept 2025)**
- **Issue resolved**: ConfigService now automatically detects platform and uses correct binary
- **Windows**: Uses `yt-dlp.exe` automatically - no manual configuration needed  
- **Linux/WSL**: Uses `yt-dlp_linux` automatically - no manual configuration needed
- **Legacy fix**: If issues persist, download appropriate binary from https://github.com/yt-dlp/yt-dlp and place in `binaries/` directory

**"pip install -e" fails**
```bash
# Try with explicit Python module
python -m pip install -e .

# Or install build dependencies first
pip install setuptools wheel
pip install -e .
```

**Entry points not working after installation**
```bash
# Check if package is installed
pip show yt-download

# Reinstall if needed
pip uninstall yt-download
pip install -e .

# Use wrapper scripts as fallback
python ytdl.py --help
python ytdl_gui.py
```

**Windows PyInstaller Executable Issues**
```bash
# Run diagnostic script to debug PyInstaller issues
python debug_windows.py

# This will show:
# - Platform and Python version info  
# - ConfigService binary path resolution
# - PyInstaller bundle contents analysis
# - File existence and permissions checking
```