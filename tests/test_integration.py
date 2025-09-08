import unittest
import tempfile
import json
import os
from unittest.mock import patch, Mock
from ytdl.core.config import ConfigService
from ytdl.core.logger import LoggerService
from ytdl.core.downloader import DownloaderService
from ytdl.core.cli import CLIService
from tests.fixtures.mock_responses import FULL_CONFIG, MOCK_PROGRESS_OUTPUT


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete service dependency chain."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        # Create a temporary config file for integration tests
        self.temp_config_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        )
        json.dump(FULL_CONFIG, self.temp_config_file)
        self.temp_config_file.close()
        
    def tearDown(self):
        """Clean up integration test fixtures."""
        if os.path.exists(self.temp_config_file.name):
            os.remove(self.temp_config_file.name)
    
    def test_full_service_initialization_chain(self):
        """Test complete service initialization with real dependencies."""
        # Initialize services in dependency order
        config = ConfigService(self.temp_config_file.name)
        logger = LoggerService(
            level=config.get("log_level", "INFO"),
            log_file=None  # Don't create real log file in tests
        )
        downloader = DownloaderService(config, logger)
        cli = CLIService(config, downloader, logger)
        
        # Verify all services are properly initialized
        self.assertIsInstance(config, ConfigService)
        self.assertIsInstance(logger, LoggerService)
        self.assertIsInstance(downloader, DownloaderService)
        self.assertIsInstance(cli, CLIService)
        
        # Verify dependency injection worked correctly
        self.assertEqual(downloader.config, config)
        self.assertEqual(downloader.output_handler, logger)
        self.assertEqual(cli.config, config)
        self.assertEqual(cli.downloader, downloader)
        self.assertEqual(cli.output_handler, logger)
    
    def test_config_propagation_through_services(self):
        """Test that configuration values propagate correctly through all services."""
        config = ConfigService(self.temp_config_file.name)
        logger = LoggerService(level=config.get("log_level"))
        downloader = DownloaderService(config, logger)
        
        # Verify config values are accessible through services
        self.assertEqual(config.download_dir, "/home/user/Videos")
        self.assertEqual(config.quality, "1080p")
        self.assertEqual(config.ytdlp_binary, "./yt-dlp_linux")
        
        # Verify downloader uses config values
        self.assertEqual(downloader.config.download_dir, "/home/user/Videos")
        self.assertEqual(downloader.config.quality, "1080p")
    
    @patch('subprocess.Popen')
    @patch('os.makedirs')
    def test_end_to_end_download_flow(self, mock_makedirs, mock_popen):
        """Test complete download flow from CLI to subprocess execution."""
        # Setup mock subprocess
        mock_process = Mock()
        mock_process.stdout = iter(MOCK_PROGRESS_OUTPUT)
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Initialize complete service chain
        config = ConfigService(self.temp_config_file.name)
        logger = LoggerService(level="INFO", log_file=None)
        downloader = DownloaderService(config, logger)
        cli = CLIService(config, downloader, logger)
        
        # Execute CLI command
        with patch('builtins.print'):  # Suppress progress output in tests
            result = cli.run(["https://youtube.com/watch?v=test123", "-q", "720p"])
        
        # Verify successful execution
        self.assertEqual(result, 0)
        
        # Verify subprocess was called with correct parameters
        mock_popen.assert_called_once()
        call_args = mock_popen.call_args[0][0]
        
        self.assertIn("./yt-dlp_linux", call_args)
        self.assertIn("-f", call_args)
        self.assertIn("720p", call_args)
        self.assertIn("https://youtube.com/watch?v=test123", call_args)
        
        # Verify directory creation
        mock_makedirs.assert_called_once_with("/home/user/Videos", exist_ok=True)
    
    @patch('subprocess.run')
    def test_end_to_end_info_flow(self, mock_run):
        """Test complete info retrieval flow from CLI to subprocess execution."""
        # Setup mock subprocess for info retrieval
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps({
            "title": "Integration Test Video",
            "duration": 300,
            "uploader": "TestChannel"
        })
        mock_run.return_value = mock_result
        
        # Initialize complete service chain
        config = ConfigService(self.temp_config_file.name)
        logger = LoggerService(level="INFO", log_file=None)
        downloader = DownloaderService(config, logger)
        cli = CLIService(config, downloader, logger)
        
        # Execute CLI info command
        result = cli.run(["https://youtube.com/watch?v=test123", "--info"])
        
        # Verify successful execution
        self.assertEqual(result, 0)
        
        # Verify subprocess was called with correct parameters
        expected_cmd = ["./yt-dlp_linux", "--dump-json", "https://youtube.com/watch?v=test123"]
        mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True)
    
    @patch('builtins.input')
    @patch('subprocess.Popen')
    @patch('os.makedirs')
    def test_end_to_end_interactive_mode(self, mock_makedirs, mock_popen, mock_input):
        """Test complete interactive mode flow."""
        # Setup mocks
        mock_input.side_effect = [
            "https://youtube.com/watch?v=test1",
            "https://youtube.com/watch?v=test2",
            "quit"
        ]
        
        mock_process = Mock()
        mock_process.stdout = iter(["[download] 100%"])
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        # Initialize complete service chain
        config = ConfigService(self.temp_config_file.name)
        logger = LoggerService(level="INFO", log_file=None)
        downloader = DownloaderService(config, logger)
        cli = CLIService(config, downloader, logger)
        
        # Execute interactive mode
        with patch('builtins.print'):  # Suppress progress output in tests
            result = cli.run(["-i", "-q", "720p"])
        
        # Verify successful execution
        self.assertEqual(result, 0)
        
        # Verify multiple downloads were executed
        self.assertEqual(mock_popen.call_count, 2)
    
    def test_error_propagation_through_services(self):
        """Test that errors propagate correctly through the service chain."""
        # Create config with invalid binary path
        invalid_config = FULL_CONFIG.copy()
        invalid_config["ytdlp_binary"] = "/nonexistent/binary"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_config, f)
            invalid_config_file = f.name
        
        try:
            # Initialize service chain with invalid config
            config = ConfigService(invalid_config_file)
            logger = LoggerService(level="INFO", log_file=None)
            downloader = DownloaderService(config, logger)
            cli = CLIService(config, downloader, logger)
            
            # Mock subprocess to raise OSError (binary not found)
            with patch('subprocess.Popen', side_effect=OSError("Binary not found")):
                result = cli.run(["https://youtube.com/watch?v=test123"])
            
            # Verify error was handled and propagated correctly
            self.assertEqual(result, 1)  # CLI should return error code
        
        finally:
            if os.path.exists(invalid_config_file):
                os.remove(invalid_config_file)
    
    def test_main_function_simulation(self):
        """Test simulation of main() function dependency wiring."""
        # This simulates the main() function in ytdl.py
        with patch('subprocess.Popen') as mock_popen:
            mock_process = Mock()
            mock_process.stdout = iter(["[download] 100%"])
            mock_process.wait.return_value = 0
            mock_popen.return_value = mock_process
            
            # Simulate main() function logic
            config = ConfigService(self.temp_config_file.name)
            logger = LoggerService(
                level=config.get("log_level", "INFO"),
                log_file=config.get("log_file")
            )
            downloader = DownloaderService(config, logger)
            cli = CLIService(config, downloader, logger)
            
            # Simulate CLI execution
            with patch('builtins.print'), patch('os.makedirs'):
                result = cli.run(["https://youtube.com/watch?v=test123"])
            
            self.assertEqual(result, 0)
    
    def test_config_modification_affects_services(self):
        """Test that runtime config modifications affect dependent services."""
        config = ConfigService(self.temp_config_file.name)
        logger = LoggerService(level="INFO", log_file=None)
        downloader = DownloaderService(config, logger)
        
        # Modify config at runtime
        original_quality = config.quality
        config.set("quality", "480p")
        
        # Verify the change is reflected in the service
        self.assertNotEqual(config.quality, original_quality)
        self.assertEqual(config.quality, "480p")
        
        # Verify downloader uses the updated config
        with patch('os.makedirs'):
            cmd = downloader._build_command("https://youtube.com/watch?v=test123")
        
        self.assertIn("-f", cmd)
        self.assertIn("480p", cmd)
    
    def test_logger_as_output_handler_integration(self):
        """Test that LoggerService properly implements OutputHandler protocol."""
        config = ConfigService(self.temp_config_file.name)
        logger = LoggerService(level="INFO", log_file=None)
        
        # Test that logger can be used as OutputHandler
        with patch.object(logger.logger, 'info') as mock_info, \
             patch.object(logger.logger, 'error') as mock_error:
            
            # Use logger as OutputHandler
            downloader = DownloaderService(config, logger)
            
            # Simulate some operations that use the output handler
            logger.info("Test info message")
            logger.error("Test error message")
            
            # Verify logger methods were called
            mock_info.assert_called_with("Test info message")
            mock_error.assert_called_with("Test error message")
    
    def test_service_isolation_and_testability(self):
        """Test that services can be tested in isolation with mocks."""
        # This demonstrates the testability benefit of dependency injection
        
        # Create mock dependencies
        mock_config = Mock()
        mock_config.ytdlp_binary = "./test-binary"
        mock_config.download_dir = "/test/dir"
        mock_config.quality = "test-quality"
        
        mock_output = Mock()
        
        # Create service with mocked dependencies
        downloader = DownloaderService(mock_config, mock_output)
        
        # Verify service uses mocked dependencies
        self.assertEqual(downloader.config, mock_config)
        self.assertEqual(downloader.output_handler, mock_output)
        
        # Test that service calls mock methods
        with patch('subprocess.Popen'), patch('os.makedirs'):
            downloader._build_command("https://test.com")
        
        # This demonstrates how easy it is to test services in isolation


if __name__ == '__main__':
    unittest.main()