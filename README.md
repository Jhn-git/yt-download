# YT-Download

A simple, modular YouTube downloader CLI tool built with dependency injection for easy testing and extensibility.

## Features

- **Simple CLI Interface**: Download videos with a single command
- **Interactive Mode**: Download multiple videos without retyping commands
- **Live Progress**: Real-time download progress with speed and ETA
- **Quality Selection**: Choose from various quality options (720p, 1080p, best, worst)
- **Audio-Only Downloads**: Extract audio tracks
- **Video Information**: Preview video details before downloading
- **Configurable**: JSON-based configuration system
- **Logging**: Built-in logging with configurable levels
- **Modular Architecture**: Clean separation of concerns with dependency injection
- **Test-Ready**: Designed for easy unit testing with mockable services

## Quick Start

### Prerequisites

- **Python 3.8+**
- **yt-dlp binary** (included for Linux and Windows - see Platform Notes below)
- **ffmpeg** (for video processing)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Jhn-git/yt-download.git
cd yt-download
```

2. Install the package in development mode:

**Windows (PowerShell - Recommended):**
```powershell
.\setup.ps1
```

**Manual Installation:**
```bash
pip install -e .
```

3. Download a video:
```bash
ytdl "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Usage

For comprehensive usage examples and advanced features, see [USAGE.md](USAGE.md).

### Quick Examples

```bash
# Download a video
ytdl "https://youtube.com/watch?v=VIDEO_ID"

# Interactive mode for multiple downloads
ytdl -i

# Launch GUI interface
ytdl-gui
```

## Configuration

Customize defaults in `config.json`. See [USAGE.md](USAGE.md) for complete configuration options.

## Project Structure

```
src/ytdl/
  ├── main.py        # CLI entry point
  ├── gui_main.py    # GUI entry point
  └── core/
    ├── config.py    # Configuration management
    ├── downloader.py # Video download service
    ├── cli.py       # Command-line interface
    ├── gui.py       # GUI service
    └── logger.py    # Logging service
setup.py             # Package installation configuration
downloads/           # Default download directory
config.json          # Configuration file
ytdl.py              # Backward compatibility wrapper
ytdl_gui.py          # Backward compatibility wrapper
```

## Architecture

This project uses dependency injection to maintain clean separation of concerns:

- **ConfigService**: Manages application configuration
- **DownloaderService**: Handles yt-dlp integration and downloads
- **CLIService**: Manages command-line interface and argument parsing
- **GUIService**: Provides tkinter-based graphical interface
- **LoggerService**: Provides structured logging

This design makes the codebase highly testable and extensible.

## Development

For detailed development instructions, see [CONTRIBUTING.md](CONTRIBUTING.md).

For comprehensive usage examples, see [USAGE.md](USAGE.md).

## Platform Notes

### Binary Configuration

The project includes yt-dlp binaries for both platforms:
- **Linux/WSL**: Uses `./binaries/yt-dlp_linux` (default)
- **Windows**: Uses `./binaries/yt-dlp.exe`

The configuration automatically detects your platform, but you can override the binary path in `config.json`:

```json
{
  "ytdlp_binary": "./binaries/yt-dlp_linux"  // or "./binaries/yt-dlp.exe"
}
```

### Cross-Platform Compatibility

- **Development**: Works on Linux, macOS, and Windows
- **Executables**: Must be built on target platform
  - **Windows**: Use `.\build.ps1` for automated builds
  - **Detailed instructions**: See BUILD_WINDOWS.md

## Requirements

- Python 3.8 or higher
- yt-dlp binary (included)
- ffmpeg for video processing

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.