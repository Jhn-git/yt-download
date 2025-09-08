import unittest
import json
import os
import tempfile
from unittest.mock import patch, mock_open, Mock
from ytdl.core.config import ConfigService
from tests.fixtures.mock_responses import MINIMAL_CONFIG, FULL_CONFIG, INVALID_CONFIG_JSON


class TestConfigService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config_file = "test_config.json"
        
    def tearDown(self):
        """Clean up after each test method."""
        if os.path.exists(self.test_config_file):
            os.remove(self.test_config_file)
    
    def test_init_with_existing_config_file(self):
        """Test ConfigService initialization with existing config file."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=json.dumps(FULL_CONFIG))), \
             patch('json.load', return_value=FULL_CONFIG):
            
            config = ConfigService(self.test_config_file)
            self.assertEqual(config.download_dir, "/home/user/Videos")
            self.assertEqual(config.quality, "1080p")
            self.assertEqual(config.ytdlp_binary, "./yt-dlp_linux")
    
    def test_init_without_config_file_uses_defaults(self):
        """Test ConfigService initialization when config file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            config = ConfigService(self.test_config_file)
            
            # Should use default configuration
            self.assertEqual(config.download_dir, "downloads")
            self.assertEqual(config.quality, "best")
            self.assertEqual(config.ytdlp_binary, "./yt-dlp_linux")
    
    def test_load_config_with_malformed_json(self):
        """Test config loading when JSON is malformed."""
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open(read_data=INVALID_CONFIG_JSON)):
            
            # Should raise JSONDecodeError
            with self.assertRaises(json.JSONDecodeError):
                ConfigService(self.test_config_file)
    
    def test_get_method_with_existing_key(self):
        """Test get() method with a key that exists in config."""
        with patch('os.path.exists', return_value=False):
            config = ConfigService(self.test_config_file)
            self.assertEqual(config.get("quality"), "best")
            self.assertEqual(config.get("download_dir"), "downloads")
    
    def test_get_method_with_nonexistent_key(self):
        """Test get() method with a key that doesn't exist."""
        with patch('os.path.exists', return_value=False):
            config = ConfigService(self.test_config_file)
            self.assertIsNone(config.get("nonexistent_key"))
    
    def test_get_method_with_default_value(self):
        """Test get() method with default value for nonexistent key."""
        with patch('os.path.exists', return_value=False):
            config = ConfigService(self.test_config_file)
            self.assertEqual(config.get("nonexistent_key", "default_value"), "default_value")
    
    def test_set_method_updates_config(self):
        """Test set() method updates internal configuration."""
        with patch('os.path.exists', return_value=False):
            config = ConfigService(self.test_config_file)
            config.set("quality", "720p")
            self.assertEqual(config.get("quality"), "720p")
            self.assertEqual(config.quality, "720p")
    
    def test_save_config_writes_to_file(self):
        """Test save_config() method writes configuration to file."""
        with patch('os.path.exists', return_value=False):
            config = ConfigService(self.test_config_file)
            config.set("quality", "720p")
            
            with patch('builtins.open', mock_open()) as mock_file, \
                 patch('json.dump') as mock_json_dump:
                
                config.save_config()
                
                # Verify file was opened for writing
                mock_file.assert_called_once_with(self.test_config_file, 'w')
                
                # Verify json.dump was called with correct data
                mock_json_dump.assert_called_once()
                saved_config = mock_json_dump.call_args[0][0]
                self.assertEqual(saved_config["quality"], "720p")
    
    def test_property_accessors(self):
        """Test property accessor methods."""
        test_config = {
            "download_dir": "/test/downloads",
            "quality": "1080p",
            "ytdlp_binary": "/usr/bin/yt-dlp"
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('builtins.open', mock_open()), \
             patch('json.load', return_value=test_config):
            
            config = ConfigService(self.test_config_file)
            self.assertEqual(config.download_dir, "/test/downloads")
            self.assertEqual(config.quality, "1080p")
            self.assertEqual(config.ytdlp_binary, "/usr/bin/yt-dlp")
    
    def test_get_default_config_structure(self):
        """Test that default config has all required keys."""
        with patch('os.path.exists', return_value=False):
            config = ConfigService(self.test_config_file)
            
            # Verify all expected default keys exist
            expected_keys = [
                "download_dir", "quality", "format", "audio_format",
                "ytdlp_binary", "log_level", "log_file"
            ]
            
            for key in expected_keys:
                self.assertIn(key, config._config, f"Default config missing key: {key}")
                # log_file can be None, others should have values
                if key != "log_file":
                    self.assertIsNotNone(config.get(key), f"Default config key {key} should not be None")
    
    def test_config_file_permission_error(self):
        """Test handling of file permission errors during save."""
        with patch('os.path.exists', return_value=False):
            config = ConfigService(self.test_config_file)
            
            # Mock permission error during file write
            with patch('builtins.open', side_effect=PermissionError("Permission denied")):
                with self.assertRaises(PermissionError):
                    config.save_config()
    
    def test_config_persistence_across_instances(self):
        """Test that config changes persist when creating new instances."""
        # Create a real temporary file for this test
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
            temp_config_file = temp_file.name
            json.dump(MINIMAL_CONFIG, temp_file)
        
        try:
            # Create first instance and modify config
            config1 = ConfigService(temp_config_file)
            config1.set("quality", "720p")
            config1.save_config()
            
            # Create second instance and verify changes persist
            config2 = ConfigService(temp_config_file)
            self.assertEqual(config2.get("quality"), "720p")
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_config_file):
                os.remove(temp_config_file)


if __name__ == '__main__':
    unittest.main()