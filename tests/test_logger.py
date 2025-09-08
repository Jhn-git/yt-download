import unittest
import logging
import sys
import tempfile
import os
from unittest.mock import patch, Mock, MagicMock
from ytdl.core.logger import LoggerService


class TestLoggerService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear any existing handlers to avoid interference between tests
        for handler in logging.getLogger("ytdl").handlers[:]:
            logging.getLogger("ytdl").removeHandler(handler)
        for handler in logging.getLogger("test_logger").handlers[:]:
            logging.getLogger("test_logger").removeHandler(handler)
    
    def test_init_with_default_parameters(self):
        """Test LoggerService initialization with default parameters."""
        with patch('logging.StreamHandler') as mock_stream_handler:
            mock_handler = Mock()
            mock_stream_handler.return_value = mock_handler
            
            logger_service = LoggerService()
            
            self.assertEqual(logger_service.logger.name, "ytdl")
            self.assertEqual(logger_service.logger.level, logging.INFO)
            mock_stream_handler.assert_called_once_with(sys.stdout)
    
    def test_init_with_custom_parameters(self):
        """Test LoggerService initialization with custom parameters."""
        with patch('logging.StreamHandler') as mock_stream_handler, \
             patch('logging.FileHandler') as mock_file_handler:
            
            mock_stream = Mock()
            mock_file = Mock()
            mock_stream_handler.return_value = mock_stream
            mock_file_handler.return_value = mock_file
            
            logger_service = LoggerService(
                name="test_logger",
                level="DEBUG",
                log_file="test.log"
            )
            
            self.assertEqual(logger_service.logger.name, "test_logger")
            self.assertEqual(logger_service.logger.level, logging.DEBUG)
            mock_stream_handler.assert_called_once_with(sys.stdout)
            mock_file_handler.assert_called_once_with("test.log")
    
    def test_setup_handlers_console_only(self):
        """Test handler setup for console output only."""
        with patch('logging.StreamHandler') as mock_stream_handler:
            mock_handler = Mock()
            mock_stream_handler.return_value = mock_handler
            
            logger_service = LoggerService(name="test_console")
            
            # Verify console handler was created and configured
            mock_stream_handler.assert_called_once_with(sys.stdout)
            mock_handler.setLevel.assert_called_with(logging.INFO)
            mock_handler.setFormatter.assert_called_once()
    
    def test_setup_handlers_with_file_logging(self):
        """Test handler setup with both console and file output."""
        with patch('logging.StreamHandler') as mock_stream_handler, \
             patch('logging.FileHandler') as mock_file_handler:
            
            mock_stream = Mock()
            mock_file = Mock()
            mock_stream_handler.return_value = mock_stream
            mock_file_handler.return_value = mock_file
            
            logger_service = LoggerService(name="test_file", log_file="test.log")
            
            # Verify both handlers were created and configured
            mock_stream_handler.assert_called_once_with(sys.stdout)
            mock_file_handler.assert_called_once_with("test.log")
            
            # Verify handler levels
            mock_stream.setLevel.assert_called_with(logging.INFO)
            mock_file.setLevel.assert_called_with(logging.DEBUG)
    
    def test_no_duplicate_handlers(self):
        """Test that handlers are not duplicated on multiple initializations."""
        with patch('logging.StreamHandler') as mock_stream_handler:
            mock_handler = Mock()
            mock_stream_handler.return_value = mock_handler
            
            # Create first instance
            logger1 = LoggerService(name="test_dup")
            initial_handler_count = len(logger1.logger.handlers)
            
            # Create second instance with same name
            logger2 = LoggerService(name="test_dup")
            
            # Should not add duplicate handlers
            self.assertEqual(len(logger2.logger.handlers), initial_handler_count)
    
    def test_logging_level_conversion(self):
        """Test that string log levels are converted to logging constants."""
        test_cases = [
            ("DEBUG", logging.DEBUG),
            ("INFO", logging.INFO),
            ("WARNING", logging.WARNING),
            ("ERROR", logging.ERROR),
            ("debug", logging.DEBUG),  # Test case insensitive
            ("info", logging.INFO),
        ]
        
        for level_str, expected_level in test_cases:
            with patch('logging.StreamHandler'):
                logger_service = LoggerService(name=f"test_{level_str}", level=level_str)
                self.assertEqual(logger_service.logger.level, expected_level)
    
    def test_info_method(self):
        """Test info() method calls logger.info()."""
        with patch('logging.StreamHandler'):
            logger_service = LoggerService(name="test_info")
            
            with patch.object(logger_service.logger, 'info') as mock_info:
                logger_service.info("Test info message")
                mock_info.assert_called_once_with("Test info message")
    
    def test_error_method(self):
        """Test error() method calls logger.error()."""
        with patch('logging.StreamHandler'):
            logger_service = LoggerService(name="test_error")
            
            with patch.object(logger_service.logger, 'error') as mock_error:
                logger_service.error("Test error message")
                mock_error.assert_called_once_with("Test error message")
    
    def test_debug_method(self):
        """Test debug() method calls logger.debug()."""
        with patch('logging.StreamHandler'):
            logger_service = LoggerService(name="test_debug")
            
            with patch.object(logger_service.logger, 'debug') as mock_debug:
                logger_service.debug("Test debug message")
                mock_debug.assert_called_once_with("Test debug message")
    
    def test_warning_method(self):
        """Test warning() method calls logger.warning()."""
        with patch('logging.StreamHandler'):
            logger_service = LoggerService(name="test_warning")
            
            with patch.object(logger_service.logger, 'warning') as mock_warning:
                logger_service.warning("Test warning message")
                mock_warning.assert_called_once_with("Test warning message")
    
    def test_formatter_configuration(self):
        """Test that formatter is configured correctly."""
        with patch('logging.StreamHandler') as mock_stream_handler, \
             patch('logging.FileHandler') as mock_file_handler:
            
            mock_stream = Mock()
            mock_file = Mock()
            mock_stream_handler.return_value = mock_stream
            mock_file_handler.return_value = mock_file
            
            logger_service = LoggerService(name="test_format", log_file="test.log")
            
            # Verify formatter was set on both handlers
            self.assertEqual(mock_stream.setFormatter.call_count, 1)
            self.assertEqual(mock_file.setFormatter.call_count, 1)
            
            # Check that the same formatter pattern is used
            stream_formatter = mock_stream.setFormatter.call_args[0][0]
            file_formatter = mock_file.setFormatter.call_args[0][0]
            
            expected_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            self.assertEqual(stream_formatter._fmt, expected_format)
            self.assertEqual(file_formatter._fmt, expected_format)
    
    def test_file_handler_creation_error(self):
        """Test handling of file handler creation errors."""
        with patch('logging.StreamHandler'), \
             patch('logging.FileHandler', side_effect=PermissionError("Permission denied")):
            
            # Should raise PermissionError when file handler creation fails
            with self.assertRaises(PermissionError):
                LoggerService(name="test_file_error", log_file="/root/test.log")
    
    def test_real_logging_output(self):
        """Integration test with actual logging output to verify functionality."""
        # Create a real temporary log file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as temp_file:
            temp_log_file = temp_file.name
        
        try:
            # Create logger service with real file
            logger_service = LoggerService(
                name="integration_test",
                level="DEBUG",
                log_file=temp_log_file
            )
            
            # Log messages at different levels
            test_messages = [
                ("info", "Test info message"),
                ("error", "Test error message"),
                ("debug", "Test debug message"),
                ("warning", "Test warning message")
            ]
            
            for level, message in test_messages:
                getattr(logger_service, level)(message)
            
            # Verify messages were written to file
            with open(temp_log_file, 'r') as f:
                log_content = f.read()
                
            for level, message in test_messages:
                self.assertIn(message, log_content)
                self.assertIn(level.upper(), log_content)
        
        finally:
            # Clean up temporary file
            if os.path.exists(temp_log_file):
                os.remove(temp_log_file)


if __name__ == '__main__':
    unittest.main()