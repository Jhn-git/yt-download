# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

This is a modular YouTube downloader CLI built with dependency injection for testability and extensibility.

### Core Services
- **ConfigService** (`core/config.py`): JSON-based configuration management with defaults
- **DownloaderService** (`core/downloader.py`): Wraps yt-dlp_linux binary calls via subprocess
- **CLIService** (`core/cli.py`): Argument parsing and user interaction
- **LoggerService** (`core/logger.py`): Structured logging with console/file output

### Dependency Flow
```
main() → ConfigService → LoggerService → DownloaderService → CLIService
```

All services use constructor injection. OutputHandler protocol enables mocking for tests.

## Environment
- **Platform**: WSL2 on Windows 11
- **Python**: 3.10.18 (default)
- **Binary**: `./yt-dlp_linux` (included, executable)
- **Dependencies**: ffmpeg (system-installed)

## Common Commands

### Running the Tool
```bash
# Basic download
./ytdl.py "https://youtube.com/watch?v=VIDEO_ID"

# With quality and output directory
./ytdl.py -q 720p -o ~/Videos "URL"

# Audio only
./ytdl.py --audio-only "URL"

# Show info without downloading
./ytdl.py --info "URL"

# Interactive mode for multiple downloads
./ytdl.py -i
./ytdl.py -i -q 720p -o ~/Videos  # with preset settings
```

### Development
```bash
# Make executable
chmod +x ytdl.py

# Test basic functionality
./ytdl.py --help
./ytdl.py --info "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### Testing Pattern
Services accept dependencies via constructor, making them easily mockable:
```python
# Example test setup
mock_config = Mock()
mock_output = Mock()
service = DownloaderService(mock_config, mock_output)
```

## Configuration
- **File**: `config.json` (JSON format)
- **Local overrides**: `config_local.json` (gitignored)
- **Key settings**: download_dir, quality, ytdlp_binary path, log_level

## Important Files
- `ytdl.py`: Main entry point with dependency wiring
- `core/downloader.py`: Core download logic and yt-dlp integration
- `config.json`: Default configuration
- `.gitignore`: Excludes downloads/, *.part, config_local.json