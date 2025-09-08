import unittest
import argparse
import sys
from unittest.mock import patch, Mock, MagicMock
from ytdl.core.cli import CLIService
from ytdl.core.downloader import OutputHandler
from tests.fixtures.mock_responses import MOCK_VIDEO_INFO


class TestCLIService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_config = Mock()
        self.mock_config.download_dir = "test_downloads"
        self.mock_config.quality = "best"
        
        self.mock_downloader = Mock()
        self.mock_output = Mock(spec=OutputHandler)
        
        self.cli = CLIService(self.mock_config, self.mock_downloader, self.mock_output)
    
    def test_init_creates_parser(self):
        """Test that CLIService initialization creates argument parser."""
        self.assertIsInstance(self.cli.parser, argparse.ArgumentParser)
    
    def test_parser_configuration(self):
        """Test that argument parser is configured correctly."""
        # Test that all expected arguments are configured
        parser_actions = {action.dest: action for action in self.cli.parser._actions}
        
        # Check required arguments exist
        self.assertIn('url', parser_actions)
        self.assertIn('output', parser_actions)
        self.assertIn('quality', parser_actions)
        self.assertIn('audio_only', parser_actions)
        self.assertIn('info', parser_actions)
        self.assertIn('interactive', parser_actions)
        
        # Check URL is optional (nargs="?")
        url_action = parser_actions['url']
        self.assertEqual(url_action.nargs, '?')
        
        # Check quality choices
        quality_action = parser_actions['quality']
        expected_choices = ["best", "worst", "720p", "1080p", "480p"]
        self.assertEqual(quality_action.choices, expected_choices)
    
    def test_parse_args_basic_url(self):
        """Test parsing basic URL argument."""
        args = self.cli.parse_args(["https://youtube.com/watch?v=test123"])
        
        self.assertEqual(args.url, "https://youtube.com/watch?v=test123")
        self.assertIsNone(args.output)
        self.assertIsNone(args.quality)
        self.assertFalse(args.audio_only)
        self.assertFalse(args.info)
        self.assertFalse(args.interactive)
    
    def test_parse_args_all_options(self):
        """Test parsing all command line options."""
        args = self.cli.parse_args([
            "https://youtube.com/watch?v=test123",
            "-o", "/custom/output",
            "-q", "720p",
            "--audio-only",
            "--info"
        ])
        
        self.assertEqual(args.url, "https://youtube.com/watch?v=test123")
        self.assertEqual(args.output, "/custom/output")
        self.assertEqual(args.quality, "720p")
        self.assertTrue(args.audio_only)
        self.assertTrue(args.info)
    
    def test_parse_args_interactive_mode(self):
        """Test parsing interactive mode flag."""
        args = self.cli.parse_args(["-i"])
        
        self.assertIsNone(args.url)
        self.assertTrue(args.interactive)
    
    def test_parse_args_short_and_long_forms(self):
        """Test both short and long argument forms."""
        # Test short forms
        args_short = self.cli.parse_args([
            "https://youtube.com/watch?v=test123",
            "-o", "/output",
            "-q", "1080p",
            "-i"
        ])
        
        # Test long forms
        args_long = self.cli.parse_args([
            "https://youtube.com/watch?v=test123",
            "--output", "/output",
            "--quality", "1080p",
            "--interactive"
        ])
        
        self.assertEqual(args_short.output, args_long.output)
        self.assertEqual(args_short.quality, args_long.quality)
        self.assertEqual(args_short.interactive, args_long.interactive)
    
    def test_run_basic_download(self):
        """Test basic download flow."""
        self.mock_downloader.download.return_value = True
        
        result = self.cli.run(["https://youtube.com/watch?v=test123"])
        
        self.assertEqual(result, 0)
        self.mock_downloader.download.assert_called_once_with(
            url="https://youtube.com/watch?v=test123",
            output_dir=None,
            quality="best"
        )
    
    def test_run_download_with_options(self):
        """Test download with custom options."""
        self.mock_downloader.download.return_value = True
        
        result = self.cli.run([
            "https://youtube.com/watch?v=test123",
            "-o", "/custom/output",
            "-q", "720p"
        ])
        
        self.assertEqual(result, 0)
        self.mock_downloader.download.assert_called_once_with(
            url="https://youtube.com/watch?v=test123",
            output_dir="/custom/output",
            quality="720p"
        )
    
    def test_run_download_failure(self):
        """Test download failure handling."""
        self.mock_downloader.download.return_value = False
        
        result = self.cli.run(["https://youtube.com/watch?v=test123"])
        
        self.assertEqual(result, 1)
    
    def test_run_audio_only_mode(self):
        """Test audio-only download mode."""
        self.mock_downloader.download.return_value = True
        
        result = self.cli.run([
            "https://youtube.com/watch?v=test123",
            "--audio-only"
        ])
        
        self.assertEqual(result, 0)
        self.mock_downloader.download.assert_called_once_with(
            url="https://youtube.com/watch?v=test123",
            output_dir=None,
            quality="bestaudio/best"
        )
    
    def test_run_info_mode(self):
        """Test info mode without downloading."""
        self.mock_downloader.get_info.return_value = MOCK_VIDEO_INFO
        
        result = self.cli.run([
            "https://youtube.com/watch?v=test123",
            "--info"
        ])
        
        self.assertEqual(result, 0)
        self.mock_downloader.get_info.assert_called_once_with("https://youtube.com/watch?v=test123")
        
        # Verify info output
        expected_calls = [
            unittest.mock.call("Title: Test Video Title"),
            unittest.mock.call("Duration: 180 seconds"),
            unittest.mock.call("Uploader: TestChannel")
        ]
        self.mock_output.info.assert_has_calls(expected_calls)
    
    def test_run_info_mode_failure(self):
        """Test info mode when video info retrieval fails."""
        self.mock_downloader.get_info.return_value = None
        
        result = self.cli.run([
            "https://youtube.com/watch?v=test123",
            "--info"
        ])
        
        self.assertEqual(result, 1)
        self.mock_output.error.assert_called_with("Could not fetch video information")
    
    def test_run_no_url_non_interactive(self):
        """Test error when no URL provided in non-interactive mode."""
        result = self.cli.run([])
        
        self.assertEqual(result, 1)
        self.mock_output.error.assert_called_with("URL required when not in interactive mode")
    
    def test_run_keyboard_interrupt(self):
        """Test keyboard interrupt handling."""
        self.mock_downloader.download.side_effect = KeyboardInterrupt()
        
        result = self.cli.run(["https://youtube.com/watch?v=test123"])
        
        self.assertEqual(result, 130)
        self.mock_output.info.assert_called_with("Download cancelled by user")
    
    def test_run_unexpected_exception(self):
        """Test unexpected exception handling."""
        self.mock_downloader.download.side_effect = Exception("Unexpected error")
        
        result = self.cli.run(["https://youtube.com/watch?v=test123"])
        
        self.assertEqual(result, 1)
        self.mock_output.error.assert_called_with("Unexpected error: Unexpected error")
    
    @patch('builtins.input')
    def test_interactive_mode_single_download(self, mock_input):
        """Test interactive mode with single download."""
        mock_input.side_effect = [
            "https://youtube.com/watch?v=test123",
            "quit"
        ]
        self.mock_downloader.download.return_value = True
        
        result = self.cli.run(["-i"])
        
        self.assertEqual(result, 0)
        
        # Verify interactive mode messages
        self.mock_output.info.assert_any_call("Interactive mode - Enter URLs to download (type 'quit' to exit)")
        self.mock_output.info.assert_any_call("Goodbye!")
        
        # Verify download was called
        self.mock_downloader.download.assert_called_once_with(
            url="https://youtube.com/watch?v=test123",
            output_dir=None,
            quality="best"
        )
    
    @patch('builtins.input')
    def test_interactive_mode_multiple_downloads(self, mock_input):
        """Test interactive mode with multiple downloads."""
        mock_input.side_effect = [
            "https://youtube.com/watch?v=test1",
            "https://youtube.com/watch?v=test2",
            "exit"
        ]
        self.mock_downloader.download.return_value = True
        
        result = self.cli.run(["-i"])
        
        self.assertEqual(result, 0)
        self.assertEqual(self.mock_downloader.download.call_count, 2)
    
    @patch('builtins.input')
    def test_interactive_mode_invalid_url(self, mock_input):
        """Test interactive mode with invalid URL."""
        mock_input.side_effect = [
            "not_a_valid_url",
            "quit"
        ]
        
        result = self.cli.run(["-i"])
        
        self.assertEqual(result, 0)
        self.mock_output.error.assert_called_with("Please enter a valid URL starting with http")
        self.mock_downloader.download.assert_not_called()
    
    @patch('builtins.input')
    def test_interactive_mode_empty_input(self, mock_input):
        """Test interactive mode with empty input."""
        mock_input.side_effect = [
            "",
            "   ",  # Whitespace only
            "quit"
        ]
        
        result = self.cli.run(["-i"])
        
        self.assertEqual(result, 0)
        # Should continue without calling download
        self.mock_downloader.download.assert_not_called()
    
    @patch('builtins.input')
    def test_interactive_mode_download_failure(self, mock_input):
        """Test interactive mode continues after download failure."""
        mock_input.side_effect = [
            "https://youtube.com/watch?v=fail",
            "https://youtube.com/watch?v=success",
            "quit"
        ]
        self.mock_downloader.download.side_effect = [False, True]
        
        result = self.cli.run(["-i"])
        
        self.assertEqual(result, 0)
        self.mock_output.error.assert_called_with("Download failed, continuing...")
        self.assertEqual(self.mock_downloader.download.call_count, 2)
    
    @patch('builtins.input')
    def test_interactive_mode_with_preset_options(self, mock_input):
        """Test interactive mode with preset quality and output."""
        mock_input.side_effect = [
            "https://youtube.com/watch?v=test123",
            "quit"
        ]
        self.mock_downloader.download.return_value = True
        
        result = self.cli.run(["-i", "-q", "720p", "-o", "/custom/output"])
        
        self.assertEqual(result, 0)
        
        # Verify settings message includes custom options
        settings_call = [call for call in self.mock_output.info.call_args_list 
                        if "Current settings" in str(call)]
        self.assertTrue(len(settings_call) > 0)
        settings_message = str(settings_call[0])
        self.assertIn("720p", settings_message)
        self.assertIn("/custom/output", settings_message)
        
        # Verify download uses preset options
        self.mock_downloader.download.assert_called_once_with(
            url="https://youtube.com/watch?v=test123",
            output_dir="/custom/output",
            quality="720p"
        )
    
    @patch('builtins.input')
    def test_interactive_mode_keyboard_interrupt(self, mock_input):
        """Test interactive mode handles keyboard interrupt gracefully."""
        mock_input.side_effect = KeyboardInterrupt()
        
        result = self.cli.run(["-i"])
        
        self.assertEqual(result, 0)
        self.mock_output.info.assert_any_call("\nExiting interactive mode")
    
    @patch('builtins.input')
    def test_interactive_mode_eof_error(self, mock_input):
        """Test interactive mode handles EOF error gracefully."""
        mock_input.side_effect = EOFError()
        
        result = self.cli.run(["-i"])
        
        self.assertEqual(result, 0)
        self.mock_output.info.assert_any_call("\nExiting interactive mode")
    
    @patch('builtins.input')
    def test_interactive_mode_quit_variations(self, mock_input):
        """Test interactive mode accepts various quit commands."""
        quit_commands = ["quit", "exit", "q", "QUIT", "EXIT", "Q"]
        
        for quit_cmd in quit_commands:
            with self.subTest(quit_command=quit_cmd):
                mock_input.side_effect = [quit_cmd]
                
                result = self.cli.run(["-i"])
                
                self.assertEqual(result, 0)
                self.mock_output.info.assert_any_call("Goodbye!")
    
    def test_determine_quality_default(self):
        """Test quality determination with default settings."""
        args = Mock()
        args.audio_only = False
        args.quality = None
        
        quality = self.cli._determine_quality(args)
        
        self.assertEqual(quality, "best")  # Should use config default
    
    def test_determine_quality_audio_only(self):
        """Test quality determination for audio-only mode."""
        args = Mock()
        args.audio_only = True
        args.quality = "720p"
        
        quality = self.cli._determine_quality(args)
        
        self.assertEqual(quality, "bestaudio/best")
    
    def test_determine_quality_custom(self):
        """Test quality determination with custom quality."""
        args = Mock()
        args.audio_only = False
        args.quality = "1080p"
        
        quality = self.cli._determine_quality(args)
        
        self.assertEqual(quality, "1080p")
    
    def test_show_info_success(self):
        """Test _show_info method with successful info retrieval."""
        self.mock_downloader.get_info.return_value = MOCK_VIDEO_INFO
        
        result = self.cli._show_info("https://youtube.com/watch?v=test123")
        
        self.assertEqual(result, 0)
        expected_calls = [
            unittest.mock.call("Title: Test Video Title"),
            unittest.mock.call("Duration: 180 seconds"),
            unittest.mock.call("Uploader: TestChannel")
        ]
        self.mock_output.info.assert_has_calls(expected_calls)
    
    def test_show_info_failure(self):
        """Test _show_info method with failed info retrieval."""
        self.mock_downloader.get_info.return_value = None
        
        result = self.cli._show_info("https://youtube.com/watch?v=test123")
        
        self.assertEqual(result, 1)
        self.mock_output.error.assert_called_with("Could not fetch video information")
    
    def test_show_info_missing_fields(self):
        """Test _show_info method with missing info fields."""
        incomplete_info = {"title": "Test Video"}  # Missing duration and uploader
        self.mock_downloader.get_info.return_value = incomplete_info
        
        result = self.cli._show_info("https://youtube.com/watch?v=test123")
        
        self.assertEqual(result, 0)
        expected_calls = [
            unittest.mock.call("Title: Test Video"),
            unittest.mock.call("Duration: Unknown seconds"),
            unittest.mock.call("Uploader: Unknown")
        ]
        self.mock_output.info.assert_has_calls(expected_calls)


if __name__ == '__main__':
    unittest.main()