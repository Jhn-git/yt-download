#!/usr/bin/env python3
import sys
from core.config import ConfigService
from core.downloader import DownloaderService
from core.cli import CLIService
from core.logger import LoggerService


def main():
    config = ConfigService()
    logger = LoggerService(
        level=config.get("log_level", "INFO"),
        log_file=config.get("log_file")
    )
    downloader = DownloaderService(config, logger)
    cli = CLIService(config, downloader, logger)
    
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())