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
- **yt-dlp binary** (included as `yt-dlp_linux`)
- **ffmpeg** (for video processing)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd yt-download
```

2. Make the script executable:
```bash
chmod +x ytdl.py
```

3. Download a video:
```bash
./ytdl.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

## Basic Usage

```bash
# Download with default settings
./ytdl.py "https://youtube.com/watch?v=VIDEO_ID"

# Specify quality and output directory
./ytdl.py -q 720p -o ~/Videos "https://youtube.com/watch?v=VIDEO_ID"

# Download audio only
./ytdl.py --audio-only "https://youtube.com/watch?v=VIDEO_ID"

# Show video information without downloading
./ytdl.py --info "https://youtube.com/watch?v=VIDEO_ID"

# Interactive mode for multiple downloads
./ytdl.py -i
# Or with preset quality/output
./ytdl.py -i -q 720p -o ~/Videos
```

## Interactive Mode

For downloading multiple videos easily:

```bash
$ ./ytdl.py -i
Interactive mode - Enter URLs to download (type 'quit' to exit)
Current settings - Quality: best, Output: downloads
ytdl> https://youtube.com/watch?v=abc123
[download progress displays]
ytdl> https://youtube.com/watch?v=def456
[download progress displays]
ytdl> quit
Goodbye!
```

## Configuration

The `config.json` file allows you to customize default behavior:

```json
{
  "download_dir": "downloads",
  "quality": "best",
  "format": "mp4",
  "audio_format": "mp3",
  "ytdlp_binary": "./yt-dlp_linux",
  "log_level": "INFO",
  "log_file": null
}
```

## Project Structure

```
ytdl.py              # Main CLI entry point
core/
  ├── config.py      # Configuration management
  ├── downloader.py  # Video download service
  ├── cli.py         # Command-line interface
  └── logger.py      # Logging service
downloads/           # Default download directory
config.json          # Configuration file
```

## Architecture

This project uses dependency injection to maintain clean separation of concerns:

- **ConfigService**: Manages application configuration
- **DownloaderService**: Handles yt-dlp integration and downloads
- **CLIService**: Manages command-line interface and argument parsing
- **LoggerService**: Provides structured logging

This design makes the codebase highly testable and extensible.

## Development

For detailed development instructions, see [CONTRIBUTING.md](CONTRIBUTING.md).

For comprehensive usage examples, see [USAGE.md](USAGE.md).

## Requirements

- Python 3.8 or higher
- yt-dlp binary (included)
- ffmpeg for video processing

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.