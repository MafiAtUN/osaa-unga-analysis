"""
Main entry point for UNGA Analysis application
"""

import sys
import os
import streamlit as st
from pathlib import Path

# Add the src directory to the Python path
src_path = Path(__file__).parent.parent
sys.path.insert(0, str(src_path))

def main():
    """Main entry point for the UNGA Analysis application."""
    # Import and run the main app
    from app import main as app_main
    app_main()

if __name__ == "__main__":
    main()
