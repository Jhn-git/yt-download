import unittest
import subprocess
import os
import json
from unittest.mock import patch, Mock, MagicMock, call
from ytdl.core.downloader import DownloaderService, OutputHandler, ConsoleOutputHandler
from tests.fixtures.mock_responses import (
    MOCK_VIDEO_INFO, MOCK_PROGRESS_OUTPUT, MOCK_ERROR_OUTPUT
)


class TestOutputHandler(unittest.TestCase):
    """Test the OutputHandler protocol implementation."""
    
    def test_console_output_handler_info(self):
        """Test ConsoleOutputHandler info method."""
        handler = ConsoleOutputHandler()
        
        with patch('builtins.print') as mock_print:
            handler.info("Test info message")
            mock_print.assert_called_once_with("INFO: Test info message")
    
    def test_console_output_handler_error(self):
        """Test ConsoleOutputHandler error method."""
        handler = ConsoleOutputHandler()
        
        with patch('builtins.print') as mock_print:
            handler.error("Test error message")
            mock_print.assert_called_once_with("ERROR: Test error message")


class TestDownloaderService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_config = Mock()
        self.mock_config.ytdlp_binary = "./yt-dlp_linux"
        self.mock_config.download_dir = "test_downloads"
        self.mock_config.quality = "best"
        
        self.mock_output = Mock(spec=OutputHandler)
        self.downloader = DownloaderService(self.mock_config, self.mock_output)
    
    def test_init_with_default_output_handler(self):
        """Test initialization with default ConsoleOutputHandler."""
        downloader = DownloaderService(self.mock_config)
        self.assertIsInstance(downloader.output_handler, ConsoleOutputHandler)
    
    def test_init_with_custom_output_handler(self):
        """Test initialization with custom OutputHandler."""
        custom_handler = Mock(spec=OutputHandler)
        downloader = DownloaderService(self.mock_config, custom_handler)
        self.assertEqual(downloader.output_handler, custom_handler)
    
    @patch('subprocess.Popen')
    @patch('os.makedirs')
    def test_download_success(self, mock_makedirs, mock_popen):
        """Test successful download with real-time progress output."""
        # Mock successful process
        mock_process = Mock()
        mock_process.stdout = iter(MOCK_PROGRESS_OUTPUT)
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            result = self.downloader.download("https://youtube.com/watch?v=test123")
        
        # Verify success
        self.assertTrue(result)
        self.mock_output.info.assert_any_call("Downloading: https://youtube.com/watch?v=test123")
        self.mock_output.info.assert_any_call("Download completed successfully")
        
        # Verify directory creation
        mock_makedirs.assert_called_once_with("test_downloads", exist_ok=True)
        
        # Verify that print was called (exact calls depend on progress line detection)
        # Progress lines should use \r (carriage return), non-progress lines normal print
        self.assertTrue(mock_print.called)
    
    @patch('subprocess.Popen')
    @patch('os.makedirs')
    def test_download_failure(self, mock_makedirs, mock_popen):
        """Test failed download with non-zero return code."""
        # Mock failed process
        mock_process = Mock()
        mock_process.stdout = iter(MOCK_ERROR_OUTPUT)
        mock_process.wait.return_value = 1
        mock_popen.return_value = mock_process
        
        result = self.downloader.download("https://youtube.com/watch?v=invalid")
        
        # Verify failure
        self.assertFalse(result)
        self.mock_output.info.assert_called_with("Downloading: https://youtube.com/watch?v=invalid")
        self.mock_output.error.assert_called_with("Download failed")
    
    @patch('subprocess.Popen')
    @patch('os.makedirs')
    def test_download_exception_handling(self, mock_makedirs, mock_popen):
        """Test download exception handling."""
        # Mock subprocess exception
        mock_popen.side_effect = OSError("Binary not found")
        
        result = self.downloader.download("https://youtube.com/watch?v=test123")
        
        # Verify exception handling
        self.assertFalse(result)
        self.mock_output.error.assert_called_with("Error during download: Binary not found")
    
    def test_build_command_default_parameters(self):
        """Test command building with default parameters."""
        with patch('os.makedirs'):
            cmd = self.downloader._build_command("https://youtube.com/watch?v=test123")
        
        expected_cmd = [
            "./yt-dlp_linux",
            "-o", "test_downloads/%(title)s.%(ext)s",
            "https://youtube.com/watch?v=test123"
        ]
        
        self.assertEqual(cmd, expected_cmd)
    
    def test_build_command_with_custom_output_dir(self):
        """Test command building with custom output directory."""
        with patch('os.makedirs'):
            cmd = self.downloader._build_command(
                "https://youtube.com/watch?v=test123",
                output_dir="/custom/output"
            )
        
        expected_cmd = [
            "./yt-dlp_linux",
            "-o", "/custom/output/%(title)s.%(ext)s",
            "https://youtube.com/watch?v=test123"
        ]
        
        self.assertEqual(cmd, expected_cmd)
    
    def test_build_command_with_custom_quality(self):
        """Test command building with custom quality."""
        with patch('os.makedirs'):
            cmd = self.downloader._build_command(
                "https://youtube.com/watch?v=test123",
                quality="720p"
            )
        
        expected_cmd = [
            "./yt-dlp_linux",
            "-o", "test_downloads/%(title)s.%(ext)s",
            "-f", "720p",
            "https://youtube.com/watch?v=test123"
        ]
        
        self.assertEqual(cmd, expected_cmd)
    
    def test_build_command_with_best_quality_no_format_flag(self):
        """Test command building with 'best' quality doesn't add format flag."""
        with patch('os.makedirs'):
            cmd = self.downloader._build_command(
                "https://youtube.com/watch?v=test123",
                quality="best"
            )
        
        expected_cmd = [
            "./yt-dlp_linux",
            "-o", "test_downloads/%(title)s.%(ext)s",
            "https://youtube.com/watch?v=test123"
        ]
        
        self.assertEqual(cmd, expected_cmd)
    
    def test_build_command_with_all_parameters(self):
        """Test command building with all custom parameters."""
        with patch('os.makedirs'):
            cmd = self.downloader._build_command(
                "https://youtube.com/watch?v=test123",
                output_dir="/custom/dir",
                quality="1080p"
            )
        
        expected_cmd = [
            "./yt-dlp_linux",
            "-o", "/custom/dir/%(title)s.%(ext)s",
            "-f", "1080p",
            "https://youtube.com/watch?v=test123"
        ]
        
        self.assertEqual(cmd, expected_cmd)
    
    @patch('os.makedirs')
    def test_build_command_creates_output_directory(self, mock_makedirs):
        """Test that build_command creates output directory."""
        self.downloader._build_command("https://youtube.com/watch?v=test123")
        
        mock_makedirs.assert_called_once_with("test_downloads", exist_ok=True)
    
    @patch('os.makedirs')
    def test_build_command_creates_custom_output_directory(self, mock_makedirs):
        """Test that build_command creates custom output directory."""
        self.downloader._build_command(
            "https://youtube.com/watch?v=test123",
            output_dir="/custom/path"
        )
        
        mock_makedirs.assert_called_once_with("/custom/path", exist_ok=True)
    
    @patch('subprocess.run')
    def test_get_info_success(self, mock_run):
        """Test successful video info retrieval."""
        # Mock successful subprocess result
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = json.dumps(MOCK_VIDEO_INFO)
        mock_run.return_value = mock_result
        
        info = self.downloader.get_info("https://youtube.com/watch?v=test123")
        
        # Verify correct command was called
        expected_cmd = ["./yt-dlp_linux", "--dump-json", "https://youtube.com/watch?v=test123"]
        mock_run.assert_called_once_with(expected_cmd, capture_output=True, text=True)
        
        # Verify returned info
        self.assertEqual(info, MOCK_VIDEO_INFO)
        self.assertEqual(info["title"], "Test Video Title")
        self.assertEqual(info["duration"], 180)
    
    @patch('subprocess.run')
    def test_get_info_failure(self, mock_run):
        """Test failed video info retrieval."""
        # Mock failed subprocess result
        mock_result = Mock()
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        info = self.downloader.get_info("https://youtube.com/watch?v=invalid")
        
        # Should return None on failure
        self.assertIsNone(info)
    
    @patch('subprocess.run')
    def test_get_info_exception_handling(self, mock_run):
        """Test get_info exception handling."""
        # Mock subprocess exception
        mock_run.side_effect = OSError("Binary not found")
        
        info = self.downloader.get_info("https://youtube.com/watch?v=test123")
        
        # Should return None on exception
        self.assertIsNone(info)
    
    @patch('subprocess.run')
    def test_get_info_invalid_json(self, mock_run):
        """Test get_info with invalid JSON response."""
        # Mock subprocess with invalid JSON
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Invalid JSON response"
        mock_run.return_value = mock_result
        
        info = self.downloader.get_info("https://youtube.com/watch?v=test123")
        
        # Should return None when JSON parsing fails
        self.assertIsNone(info)
    
    @patch('subprocess.Popen')
    @patch('os.makedirs')
    def test_download_with_empty_output(self, mock_makedirs, mock_popen):
        """Test download with empty stdout output."""
        # Mock process with empty output
        mock_process = Mock()
        mock_process.stdout = iter([])
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        result = self.downloader.download("https://youtube.com/watch?v=test123")
        
        # Should still succeed with empty output
        self.assertTrue(result)
        self.mock_output.info.assert_any_call("Download completed successfully")
    
    @patch('subprocess.Popen')
    @patch('os.getcwd')
    def test_download_uses_current_working_directory(self, mock_getcwd, mock_popen):
        """Test that download process uses current working directory."""
        mock_getcwd.return_value = "/current/working/dir"
        mock_process = Mock()
        mock_process.stdout = iter([])
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        with patch('os.makedirs'):
            self.downloader.download("https://youtube.com/watch?v=test123")
        
        # Verify Popen was called with correct cwd
        mock_popen.assert_called_once()
        call_kwargs = mock_popen.call_args[1]
        self.assertEqual(call_kwargs['cwd'], "/current/working/dir")
    
    def test_config_and_output_handler_dependency_injection(self):
        """Test that dependencies are properly injected."""
        custom_config = Mock()
        custom_output = Mock(spec=OutputHandler)
        
        downloader = DownloaderService(custom_config, custom_output)
        
        self.assertEqual(downloader.config, custom_config)
        self.assertEqual(downloader.output_handler, custom_output)
    
    def test_is_progress_line_detection(self):
        """Test progress line detection logic."""
        # Test valid progress lines
        progress_lines = [
            "[download]  23.6% of    4.27GiB at   44.47MiB/s ETA 01:15",
            "[download] 100% of 10.50MiB at 2.4MiB/s",
            "[download]   0.0% of 3.28MiB at 1.50MiB/s ETA 00:02",
            "[download]  45.2% of 3.28MiB at 2.1MiB/s ETA 00:01"
        ]
        
        for line in progress_lines:
            with self.subTest(line=line):
                self.assertTrue(self.downloader._is_progress_line(line))
        
        # Test non-progress lines
        non_progress_lines = [
            "[download] Downloading video: Test Video Title",
            "[ffmpeg] Merging formats into \"Test Video.mp4\"",
            "ERROR: Video unavailable",
            "[youtube] test123: Downloading webpage",
            "[download] Destination: /path/to/video.mp4",
            "Regular output without brackets",
            "[download] without percentage"
        ]
        
        for line in non_progress_lines:
            with self.subTest(line=line):
                self.assertFalse(self.downloader._is_progress_line(line))
    
    @patch('subprocess.Popen')
    @patch('os.makedirs')  
    def test_smart_progress_output_handling(self, mock_makedirs, mock_popen):
        """Test smart progress output with mixed progress and non-progress lines."""
        # Mix of progress and non-progress lines
        mixed_output = [
            "[youtube] test123: Downloading webpage",  # Non-progress
            "[download] Downloading video: Test Video",  # Non-progress
            "[download]   0.0% of 10.5MiB at 1.2MiB/s ETA 00:08",  # Progress
            "[download]  25.5% of 10.5MiB at 2.1MiB/s ETA 00:03",  # Progress
            "[download]  50.1% of 10.5MiB at 2.3MiB/s ETA 00:02",  # Progress
            "[ffmpeg] Merging formats into \"video.mp4\"",  # Non-progress
            "[download] 100% of 10.5MiB at 2.4MiB/s"  # Progress (final)
        ]
        
        mock_process = Mock()
        mock_process.stdout = iter(mixed_output)
        mock_process.wait.return_value = 0
        mock_popen.return_value = mock_process
        
        with patch('builtins.print') as mock_print:
            result = self.downloader.download("https://youtube.com/watch?v=test123")
        
        self.assertTrue(result)
        
        # Verify different print patterns were used
        print_calls = mock_print.call_args_list
        
        # Should have been called multiple times with different patterns
        self.assertTrue(len(print_calls) > 0)
        
        # Check that some calls used carriage return (progress lines)
        progress_calls = [call for call in print_calls 
                         if call[0] and call[0][0].startswith('\r[download]')]
        self.assertTrue(len(progress_calls) > 0, "Should have progress calls with carriage return")
        
        # Check that some calls were normal prints (non-progress lines)
        normal_calls = [call for call in print_calls 
                       if call[0] and not call[0][0].startswith('\r')]
        self.assertTrue(len(normal_calls) > 0, "Should have normal print calls")
    
    def test_progress_line_edge_cases(self):
        """Test progress line detection edge cases."""
        # Edge cases that should NOT be detected as progress
        edge_cases = [
            "",  # Empty string
            "[download]",  # Just the prefix
            "[download] ",  # Prefix with space only
            "[download] Starting download",  # No percentage
            "[download] 25 percent complete",  # Word "percent" instead of %
            "[progress] 25% complete",  # Wrong prefix
            "25% of download complete"  # No [download] prefix
        ]
        
        for line in edge_cases:
            with self.subTest(line=line):
                self.assertFalse(self.downloader._is_progress_line(line))
        
        # Edge cases that SHOULD be detected as progress
        valid_edge_cases = [
            "[download] 0% of 1.0MiB at 100KiB/s",  # Zero percent
            "[download]100% of 1.0MiB",  # No space after ]
            "[download]  100.0% complete"  # Decimal percentage
        ]
        
        for line in valid_edge_cases:
            with self.subTest(line=line):
                self.assertTrue(self.downloader._is_progress_line(line))


if __name__ == '__main__':
    unittest.main()