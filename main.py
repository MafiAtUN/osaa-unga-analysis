#!/usr/bin/env python3
"""
UNGA Analysis App - Main Application Entry Point
Production-ready UNGA speech analysis platform
"""

import sys
import os
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the main application
if __name__ == "__main__":
    from src.unga_analysis.main import main
    main()
