import argparse
from typing import List, Optional
from .config import ConfigService
from .downloader import DownloaderService, OutputHandler


class CLIService:
    def __init__(self, config: ConfigService, downloader: DownloaderService, output_handler: OutputHandler):
        self.config = config
        self.downloader = downloader
        self.output_handler = output_handler
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            description="Simple YouTube downloader with dependency injection",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        parser.add_argument(
            "url",
            help="URL to download"
        )
        
        parser.add_argument(
            "-o", "--output",
            help=f"Output directory (default: {self.config.download_dir})"
        )
        
        parser.add_argument(
            "-q", "--quality",
            help=f"Video quality (default: {self.config.quality})",
            choices=["best", "worst", "720p", "1080p", "480p"]
        )
        
        parser.add_argument(
            "--audio-only",
            action="store_true",
            help="Download audio only"
        )
        
        parser.add_argument(
            "--info",
            action="store_true",
            help="Show video information without downloading"
        )
        
        return parser
    
    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        return self.parser.parse_args(args)
    
    def run(self, args: Optional[List[str]] = None) -> int:
        try:
            parsed_args = self.parse_args(args)
            
            if parsed_args.info:
                return self._show_info(parsed_args.url)
            
            quality = self._determine_quality(parsed_args)
            success = self.downloader.download(
                url=parsed_args.url,
                output_dir=parsed_args.output,
                quality=quality
            )
            
            return 0 if success else 1
            
        except KeyboardInterrupt:
            self.output_handler.info("Download cancelled by user")
            return 130
        except Exception as e:
            self.output_handler.error(f"Unexpected error: {str(e)}")
            return 1
    
    def _determine_quality(self, args: argparse.Namespace) -> str:
        if args.audio_only:
            return "bestaudio/best"
        return args.quality or self.config.quality
    
    def _show_info(self, url: str) -> int:
        info = self.downloader.get_info(url)
        if info:
            self.output_handler.info(f"Title: {info.get('title', 'Unknown')}")
            self.output_handler.info(f"Duration: {info.get('duration', 'Unknown')} seconds")
            self.output_handler.info(f"Uploader: {info.get('uploader', 'Unknown')}")
            return 0
        else:
            self.output_handler.error("Could not fetch video information")
            return 1