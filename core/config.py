import json
import os
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigService:
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "download_dir": "downloads",
            "quality": "best",
            "format": "mp4",
            "audio_format": "mp3",
            "ytdlp_binary": "./yt-dlp_linux",
            "log_level": "INFO",
            "log_file": None
        }
    
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        self._config[key] = value
    
    @property
    def download_dir(self) -> str:
        return self._config["download_dir"]
    
    @property
    def ytdlp_binary(self) -> str:
        return self._config["ytdlp_binary"]
    
    @property
    def quality(self) -> str:
        return self._config["quality"]