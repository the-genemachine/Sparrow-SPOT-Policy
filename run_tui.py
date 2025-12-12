#!/usr/bin/env python3
"""
Launcher script for Sparrow SPOT TUI
Run from project root: ./run_tui.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tui.sparrow_tui import main

if __name__ == "__main__":
    main()
