#!/usr/bin/env python3
"""
Root-level convenience script for YT-Download CLI.
"""
import sys
import os

# Add src to path for development mode
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from ytdl.main import main

if __name__ == "__main__":
    sys.exit(main())