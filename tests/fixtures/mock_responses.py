# Mock responses and data for testing

# Mock yt-dlp JSON info response
MOCK_VIDEO_INFO = {
    "title": "Test Video Title",
    "duration": 180,
    "uploader": "TestChannel",
    "id": "test123",
    "ext": "mp4",
    "format_id": "137+140",
    "url": "https://example.com/video.mp4"
}

# Mock yt-dlp progress output lines
MOCK_PROGRESS_OUTPUT = [
    "[download] Downloading video: Test Video Title\n",
    "[download]   0.0% of 10.50MiB at  1.2MiB/s ETA 00:08\n",
    "[download]  25.5% of 10.50MiB at  2.1MiB/s ETA 00:03\n",
    "[download]  50.1% of 10.50MiB at  2.3MiB/s ETA 00:02\n",
    "[download]  75.8% of 10.50MiB at  2.5MiB/s ETA 00:01\n",
    "[download] 100% of 10.50MiB at  2.4MiB/s\n",
    "[ffmpeg] Merging formats into \"Test Video Title.mp4\"\n"
]

# Mock yt-dlp error output
MOCK_ERROR_OUTPUT = [
    "ERROR: Video unavailable\n",
    "ERROR: This video is private\n"
]

# Sample configuration variations for testing
MINIMAL_CONFIG = {
    "download_dir": "downloads",
    "quality": "best"
}

FULL_CONFIG = {
    "download_dir": "/home/user/Videos",
    "quality": "1080p",
    "format": "mp4",
    "audio_format": "mp3",
    "ytdlp_binary": "./yt-dlp_linux",
    "log_level": "INFO",
    "log_file": "ytdl.log"
}

INVALID_CONFIG_JSON = '{"download_dir": "downloads", "quality":}'  # Malformed JSON