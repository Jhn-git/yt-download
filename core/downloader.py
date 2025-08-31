import subprocess
import os
from typing import List, Optional, Protocol
from .config import ConfigService


class OutputHandler(Protocol):
    def info(self, message: str): ...
    def error(self, message: str): ...


class ConsoleOutputHandler:
    def info(self, message: str):
        print(f"INFO: {message}")
    
    def error(self, message: str):
        print(f"ERROR: {message}")


class DownloaderService:
    def __init__(self, config: ConfigService, output_handler: OutputHandler = None):
        self.config = config
        self.output_handler = output_handler or ConsoleOutputHandler()
    
    def download(self, url: str, output_dir: Optional[str] = None, quality: Optional[str] = None) -> bool:
        try:
            cmd = self._build_command(url, output_dir, quality)
            self.output_handler.info(f"Downloading: {url}")
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=os.getcwd()
            )
            
            # Stream output in real-time
            for line in process.stdout:
                print(line.rstrip())
            
            # Wait for process to complete and get return code
            return_code = process.wait()
            
            if return_code == 0:
                self.output_handler.info("Download completed successfully")
                return True
            else:
                self.output_handler.error("Download failed")
                return False
                
        except Exception as e:
            self.output_handler.error(f"Error during download: {str(e)}")
            return False
    
    def _build_command(self, url: str, output_dir: Optional[str] = None, quality: Optional[str] = None) -> List[str]:
        cmd = [self.config.ytdlp_binary]
        
        download_dir = output_dir or self.config.download_dir
        os.makedirs(download_dir, exist_ok=True)
        cmd.extend(["-o", f"{download_dir}/%(title)s.%(ext)s"])
        
        format_quality = quality or self.config.quality
        if format_quality != "best":
            cmd.extend(["-f", format_quality])
        
        cmd.append(url)
        return cmd
    
    def get_info(self, url: str) -> Optional[dict]:
        try:
            cmd = [self.config.ytdlp_binary, "--dump-json", url]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                import json
                return json.loads(result.stdout.strip())
            return None
        except Exception:
            return None