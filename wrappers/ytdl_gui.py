#!/usr/bin/env python3
"""
Backward-compatible wrapper for ytdl GUI.

This script provides compatibility with the old file structure while
using the new package-based approach.
"""
import sys

def main():
    """Run the ytdl GUI using the installed package or local development mode."""
    import os
    
    # Remove current directory from path to avoid importing this wrapper script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    original_path = sys.path[:]
    
    # Try importing from installed package first
    try:
        # Temporarily remove current directory to avoid wrapper script conflicts
        if current_dir in sys.path:
            sys.path.remove(current_dir)
        if '' in sys.path:
            sys.path.remove('')
            
        from ytdl.gui_main import main as gui_main
        return gui_main()
    except ImportError:
        pass
    finally:
        # Restore original path
        sys.path[:] = original_path
    
    # Fallback to local development mode
    try:
        # Go up one level from wrappers/ to project root, then to src/
        project_root = os.path.dirname(current_dir)
        src_path = os.path.join(project_root, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        from ytdl.gui_main import main as gui_main
        return gui_main()
    except ImportError:
        print("ERROR: Could not import ytdl package.")
        print("Please run: pip install -e .")
        print("Or ensure the src/ytdl directory exists.")
        return 1

if __name__ == "__main__":
    sys.exit(main())