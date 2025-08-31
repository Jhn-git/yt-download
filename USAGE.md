# Usage Guide

This guide provides comprehensive examples and advanced usage patterns for the YT-Download CLI tool.

## Table of Contents

1. [Basic Downloads](#basic-downloads)
2. [Quality Options](#quality-options)
3. [Output Management](#output-management)
4. [Audio Downloads](#audio-downloads)
5. [Video Information](#video-information)
6. [Configuration](#configuration)
7. [Logging](#logging)
8. [Advanced Examples](#advanced-examples)
9. [Troubleshooting](#troubleshooting)

## Basic Downloads

### Download a Single Video

```bash
./ytdl.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

This downloads the video to the default `downloads/` directory with the best available quality.

### Download with Custom Title

The tool automatically uses the video title as the filename. Special characters are handled safely.

## Quality Options

### Available Quality Settings

- `best` - Highest quality available (default)
- `worst` - Lowest quality available
- `720p` - 720p resolution
- `1080p` - 1080p resolution  
- `480p` - 480p resolution

### Examples

```bash
# Download in 720p
./ytdl.py -q 720p "https://youtube.com/watch?v=VIDEO_ID"

# Download lowest quality (for slow connections)
./ytdl.py -q worst "https://youtube.com/watch?v=VIDEO_ID"

# Download highest quality (explicit)
./ytdl.py -q best "https://youtube.com/watch?v=VIDEO_ID"
```

## Output Management

### Custom Output Directory

```bash
# Download to specific folder
./ytdl.py -o ~/Videos "https://youtube.com/watch?v=VIDEO_ID"

# Download to current directory
./ytdl.py -o . "https://youtube.com/watch?v=VIDEO_ID"

# Create nested directories
./ytdl.py -o ~/Downloads/YouTube/Music "https://youtube.com/watch?v=VIDEO_ID"
```

### Combine Quality and Output

```bash
./ytdl.py -q 1080p -o ~/Videos "https://youtube.com/watch?v=VIDEO_ID"
```

## Audio Downloads

### Extract Audio Only

```bash
# Download audio only (best quality)
./ytdl.py --audio-only "https://youtube.com/watch?v=VIDEO_ID"

# Combine with custom output
./ytdl.py --audio-only -o ~/Music "https://youtube.com/watch?v=VIDEO_ID"
```

Audio files are automatically converted to MP3 format using ffmpeg.

## Video Information

### Preview Before Download

```bash
./ytdl.py --info "https://youtube.com/watch?v=VIDEO_ID"
```

This shows:
- Video title
- Duration (in seconds)
- Uploader name
- Available formats

### Example Output

```
INFO: Title: Never Gonna Give You Up
INFO: Duration: 213 seconds
INFO: Uploader: RickAstleyVEVO
```

## Configuration

### Default Configuration File

The `config.json` file controls default behavior:

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

### Customizing Defaults

Edit `config.json` to change default behavior:

```json
{
  "download_dir": "/home/user/Videos",
  "quality": "720p",
  "log_level": "DEBUG",
  "log_file": "ytdl.log"
}
```

## Logging

### Log Levels

- `DEBUG` - Detailed information for debugging
- `INFO` - General information (default)
- `WARNING` - Warning messages
- `ERROR` - Error messages only

### Console Logging

By default, logs are displayed in the console with timestamps:

```
2024-08-31 10:30:45,123 - ytdl - INFO - Downloading: https://youtube.com/watch?v=...
2024-08-31 10:31:02,456 - ytdl - INFO - Download completed successfully
```

### File Logging

Enable file logging by setting `log_file` in `config.json`:

```json
{
  "log_file": "ytdl.log",
  "log_level": "DEBUG"
}
```

## Advanced Examples

### Batch Processing Script

Create a shell script for multiple downloads:

```bash
#!/bin/bash
# batch_download.sh

urls=(
  "https://youtube.com/watch?v=VIDEO_ID_1"
  "https://youtube.com/watch?v=VIDEO_ID_2"
  "https://youtube.com/watch?v=VIDEO_ID_3"
)

for url in "${urls[@]}"; do
  ./ytdl.py -q 720p -o ~/Videos "$url"
  sleep 2  # Be nice to the server
done
```

### Quality Fallback

If a specific quality isn't available, yt-dlp will automatically select the closest available quality.

### Working with Different Platforms

The tool works with any platform supported by yt-dlp:

```bash
# YouTube
./ytdl.py "https://youtube.com/watch?v=VIDEO_ID"

# Vimeo
./ytdl.py "https://vimeo.com/123456789"

# Many other platforms supported by yt-dlp
```

## Troubleshooting

### Common Issues

#### Permission Denied
```bash
chmod +x ytdl.py
```

#### Python Module Not Found
Ensure you're using Python 3.8+ and all files are in the correct directory structure.

#### Download Fails
- Check internet connection
- Verify the video URL is accessible
- Check if video has region restrictions
- Enable DEBUG logging for more details

#### FFmpeg Not Found
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install ffmpeg

# Check if ffmpeg is installed
which ffmpeg
```

### Debug Mode

Enable detailed logging:

```json
{
  "log_level": "DEBUG",
  "log_file": "debug.log"
}
```

Then check the log file for detailed information about what's happening.

### Video Not Available

Some videos may not be available due to:
- Geographic restrictions
- Age restrictions
- Private/unlisted status
- Copyright restrictions

The tool will display an appropriate error message in these cases.

### Performance Tips

- Use `--info` first to check video details
- Choose appropriate quality based on your needs
- Use `worst` quality for slow connections
- Consider `--audio-only` for music content

## Getting Help

```bash
./ytdl.py --help
```

For more technical details, see the source code documentation in the `core/` directory.