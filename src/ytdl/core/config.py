import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigService:
    """Manages application configuration with JSON-based persistence.
    
    Provides centralized configuration management with defaults, file loading,
    and PyInstaller bundle support. Handles platform-specific binary paths.
    """
    
    def __init__(self, config_file: str = "config/config.json"):
        """Initialize configuration service.
        
        Args:
            config_file: Path to configuration file (default: "config/config.json")
        """
        self.config_file = config_file
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults.
        
        Returns:
            Dictionary containing configuration settings
        """
        # Try to load from bundled config first (PyInstaller)
        config_path = self._get_resource_path(self.config_file)
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = self._get_default_config()
        
        # Update binary path for PyInstaller bundle
        # Handle platform-specific binary names
        import platform
        default_binary = "yt-dlp.exe" if platform.system() == "Windows" else "yt-dlp_linux"
        
        # Always use platform-appropriate binary regardless of config file
        binary_name = default_binary
        
        # Try binaries subdirectory first (correct path), then fallback to root
        binary_path = self._get_resource_path(os.path.join("binaries", binary_name))
        
        # Fallback: try root directory if binaries subdirectory doesn't exist
        if not os.path.exists(binary_path):
            fallback_path = self._get_resource_path(binary_name)
            if os.path.exists(fallback_path):
                binary_path = fallback_path
        
        config["ytdlp_binary"] = binary_path
        
        return config
    
    def _get_resource_path(self, relative_path: str) -> str:
        """Get absolute path to resource, works for PyInstaller bundles"""
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except AttributeError:
            # Running in normal Python environment - find project root
            # Go from src/ytdl/core/config.py -> project root
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        
        return os.path.join(base_path, relative_path)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration settings.
        
        Returns:
            Dictionary with default configuration values
        """
        return {
            "download_dir": "downloads",
            "quality": "best",
            "format": "mp4",
            "audio_format": "mp3",
            "ytdlp_binary": "yt-dlp_linux",
            "log_level": "INFO",
            "log_file": None
        }
    
    def save_config(self):
        """Save current configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get(self, key: str, default: Optional[Any] = None) -> Any:
        """Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
        """
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
    
    @property
    def format(self) -> str:
        return self._config["format"]